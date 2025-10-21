import frappe
import random
import string
import re
import json
import frappe
import base64
from io import BytesIO
from datetime import datetime
from frappe import _

@frappe.whitelist()
def get_academic_years():
    edu_settings = frappe.get_single("Education Settings")
    current_year = edu_settings.current_academic_year

    # Get all academic year names as a flat list (excluding current year)
    other_years = frappe.get_all(
        "Academic Year",
        filters={"name": ["!=", current_year]},
        pluck="name"
    )

    # Insert current year at the beginning
    years = [current_year] + other_years

    return years

@frappe.whitelist()
def get_classes():
    classes = frappe.get_all("Program")
    return classes

@frappe.whitelist()
def get_divisions1(values):
    class_name = values.get("classId")  # Extract classId from the values dictionary
    edu_settings = frappe.get_single("Education Settings")
    year = edu_settings.current_academic_year
    divisions = frappe.get_all("Student Group", filters={"program": class_name, "academic_year": year})
    return divisions
    
@frappe.whitelist()
def get_divisions2(values):
    class_name = values.get("classId")  # Extract classId from the values dictionary
    year = values.get("academicYear")
    divisions = frappe.get_all("Student Group", filters={"program": class_name, "academic_year": year})
    return divisions

def add_student_to_group(student_group, student_id, student_name, roll_no):
    """Append a student to the Student Group child table."""
    child = student_group.append("students", {})
    child.student = student_id
    child.student_name = student_name
    child.active = 1
    child.group_roll_number = roll_no

def safe_int(val):
    try:
        return int(val)
    except (ValueError, TypeError):
        return float('inf')


def generate_unique_email(first_name, last_name, gr_number):
    base_name = f"{first_name}.{last_name}".replace(" ", ".").lower()
    gr = str(gr_number).strip().lower().replace(" ", "")
    base = re.sub(r'\.+', '.', f"{base_name}.{gr}").strip('.')

    while True:
        email = f"{base}@codedaddy.io"
        if not frappe.db.exists("User", {"email": email}):
            return email

        email = f"{base}.{random.randint(1000, 9999)}@codedaddy.io"
        if not frappe.db.exists("User", {"email": email}):
            return email


def generate_unique_phone():
    while True:
        phone = f"9{''.join(random.choices(string.digits, k=9))}"
        if not frappe.db.exists("User", {"mobile_no": phone}):
            return phone

def convert_to_ddmmyyyy(d): 
    try: datetime.strptime(d,"%d-%m-%Y"); return d
    except: return datetime.strptime(d,"%Y-%m-%d").strftime("%d-%m-%Y")

@frappe.whitelist(allow_guest=True)
def add_guardian_to_student(student_id, student_name, guardian_info):
    try:
        guardian_no = guardian_info.get("guardian_no")
        guardian_name = guardian_info.get("guardian_name")
        if not guardian_no:
            frappe.throw("Guardian number missing.")
        if not guardian_name:
            frappe.throw("Guardian name missing.")

        # Extract student's last name for guardian email
        student_name_parts = student_name.strip().split()
        last_name = student_name_parts[-1] if len(student_name_parts) > 1 else "guardian"

        # Guardian first name comes from guardian_name
        first_name = guardian_name.strip()

        # Generate email properly using student's last name
        guardian_email = (
            guardian_info.get("guardian_email")
            or generate_unique_email(first_name, last_name, guardian_no)
        )

        # Check if Guardian exists
        existing_guardian = frappe.db.get_value("Guardian", {"mobile_number": guardian_no}, "name")

        if existing_guardian:
            guardian_name = frappe.db.get_value("Guardian", {"name": existing_guardian}, "guardian_name")
        else:
            # Check if User exists by mobile or email
            existing_user = (
                frappe.db.get_value("User", {"mobile_no": guardian_no}, "name") or
                frappe.db.get_value("User", {"email": guardian_email}, "name")
            )

            if existing_user:
                user_name = existing_user
                # Ensure Guardian role is assigned
                user_doc = frappe.get_doc("User", user_name)
                if "Guardian" not in [r.role for r in user_doc.roles]:
                    user_doc.add_roles("Guardian")
            else:
                # Create new User
                user_doc = frappe.get_doc({
                    "doctype": "User",
                    "mobile_no": guardian_no,
                    "first_name": guardian_name,
                    "email": guardian_email,
                }).insert(ignore_permissions=True)
                user_doc.add_roles("Guardian")
                user_doc.user_type = "Website User"
                user_name = user_doc.name

            # Create Guardian and link to User
            guardian_doc = frappe.get_doc({
                "doctype": "Guardian",
                "guardian_name": guardian_name,
                "mobile_number": guardian_no,
                "email_address": guardian_email,
                "user": user_name,
                "date_of_birth": guardian_info.get("date_of_birth"),
                "occupation": guardian_info.get("occupation"),
                "designation": guardian_info.get("designation"),
                "work_address": guardian_info.get("work_address"),
                "education": guardian_info.get("education"),
            }).insert(ignore_permissions=True)

            existing_guardian = guardian_doc.name

        # Link Guardian to Student
        student_doc = frappe.get_doc("Student", student_id)
        if any(g.guardian == existing_guardian for g in student_doc.guardians):
            return "Guardian already linked."

        student_guardian = student_doc.append("guardians", {})
        student_guardian.guardian = existing_guardian
        student_guardian.guardian_name = guardian_name

        # Handle relation Select field safely
        relation = guardian_info.get("relation", "Others")
        allowed = [opt.strip() for opt in frappe.get_meta("Student Guardian").get_field("relation").options.split("\n")]
        if relation not in allowed:
            relation = "Others"
        student_guardian.relation = relation

        student_doc.save(ignore_permissions=True)
        frappe.db.commit()

        return "Guardian linked successfully."

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Add Guardian Error")
        return f"Error: {str(e)}"

@frappe.whitelist()
def enroll_student(student, className, divisionName, year, term):
    dob = student["Student Date of Birth"]
    first_name = student["First Name"]
    middle_name = student.get("Middle Name", "")
    last_name = student["Last Name"]
    full_name = " ".join(part for part in [first_name, middle_name, last_name] if part.strip())
    email = student.get("Email Address")

    # ✅ Extract guardian details from student object
    guardian_info = {
        "guardian_name": student.get("Guardian Name"),
        "guardian_email": student.get("Guardian Email"),
        "guardian_no": student.get("Guardian Number"),
        "relation": student.get("Relation"),
        "date_of_birth": student.get("Guardian Date of Birth"),
        "occupation": student.get("Guardian Occupation"),
        "designation": student.get("Guardian Designation"),
        "work_address": student.get("Guardian Work Address"),
        "education": student.get("Guardian Education"),
    }

    # --- Duplicate Checks ---
    if email and frappe.db.exists("Student", {"student_email_id": email}):
        frappe.throw(_("Duplicate email for: {0}, {1}").format(full_name, email))

    if frappe.db.exists("Student", {"gr_number": student.get("GR Number")}):
        frappe.throw(_("Duplicate GR Number for: {0}, {1}").format(full_name, student.get("GR Number")))

    # --- Generate fallback email ---
    if not email or "@" not in email:
        email = generate_unique_email(first_name, last_name, student.get("GR Number", ""))

    student_doc = None
    program_enrollment = None
    
    try:
        # --- Step 1: Create User ---
        phone = str(student.get("Phone Number") or generate_unique_phone())
        user = frappe.new_doc("User")
        user.first_name = first_name
        user.middle_name = middle_name
        user.last_name = last_name
        user.email = email
        user.username = f"{first_name.lower()}{student.get('GR Number', '')}".replace(" ", "")
        if not frappe.db.exists("User", {"mobile_no": phone}):
            user.mobile_no = phone
        user.date_birth = dob
        user.send_welcome_email = 0
        user.enabled = 1
        user.user_type = "Website User"
        user.save()
        
        # Check if User creation was successful
        if not user.name:
            frappe.throw("Failed to create User account")
        
        print(f"✅ User created successfully: {user.name}")

        # --- Step 2: Create Student (only if User was successful) ---
        student_doc = frappe.new_doc("Student")
        student_doc.first_name = first_name
        student_doc.middle_name = middle_name
        student_doc.last_name = last_name
        student_doc.student_email_id = email
        student_doc.user = email
        student_doc.date_of_birth = dob
        student_doc.student_mobile_number = phone
        student_doc.gr_number = student["GR Number"]
        student_doc.save()
        
        # Check if Student creation was successful
        if not student_doc.name:
            # If Student creation fails, delete the created User
            frappe.delete_doc("User", user.name)
            frappe.throw("Failed to create Student record")
        
        print(f"✅ Student created successfully: {student_doc.name}")

        # --- Step 3: Create Program Enrollment (only if Student was successful) ---
        program_enrollment = frappe.new_doc("Program Enrollment")
        program_enrollment.student = student_doc.name
        program_enrollment.program = className
        program_enrollment.student_batch_name = divisionName
        program_enrollment.academic_year = year
        program_enrollment.academic_term = term
        program_enrollment.save()
        
        # Check if Program Enrollment creation was successful
        if not program_enrollment.name:
            # If Program Enrollment fails, delete the created Student and User
            frappe.delete_doc("Student", student_doc.name)
            frappe.delete_doc("User", user.name)
            frappe.throw("Failed to create Program Enrollment")
        
        # Submit Program Enrollment only if creation was successful
        program_enrollment.submit()
        print(f"✅ Program Enrollment created and submitted successfully: {program_enrollment.name}")

        # --- Step 4: Add Guardian (only if all previous steps were successful) ---
        if guardian_info["guardian_name"] and guardian_info["guardian_no"]:
            try:
                add_guardian_to_student(
                    student_id=student_doc.name,
                    student_name=student_doc.student_name,
                    guardian_info=guardian_info
                )
                print(f"✅ Guardian added successfully for student: {student_doc.name}")
            except Exception as guardian_error:
                # If guardian addition fails, log the error but don't rollback the entire enrollment
                print(f"⚠️ Guardian addition failed for {student_doc.name}: {str(guardian_error)}")
                # Continue without throwing error - student is still enrolled

        return {
            "success": True,
            "user": user.name,
            "student": student_doc.name,
            "program_enrollment": program_enrollment.name
        }

    except Exception as e:
        # Cleanup: If any step fails, delete any successfully created documents
        # cleanup_created_docs(user, student_doc, program_enrollment)
        frappe.throw(f"Failed to enroll student {full_name}: {str(e)}")


def cleanup_created_docs(user, student, program_enrollment):
    """Clean up any successfully created documents if enrollment fails at any step"""
    try:
        # Delete in reverse order of creation
        if program_enrollment and program_enrollment.name:
            if frappe.db.exists("Program Enrollment", program_enrollment.name):
                frappe.delete_doc("Program Enrollment", program_enrollment.name)
        
        if student and student.name:
            if frappe.db.exists("Student", student.name):
                frappe.delete_doc("Student", student.name)
        
        if user and user.name:
            if frappe.db.exists("User", user.name):
                frappe.delete_doc("User", user.name)
                
    except Exception as cleanup_error:
        print(f"⚠️ Cleanup error: {str(cleanup_error)}")
        # Don't throw error during cleanup


@frappe.whitelist()
def bulk_enroll_students(className, divisionName, students):
    print(f"Received {len(students)} students")

    # --- Security check ---
    if "Administrator" not in frappe.get_roles(frappe.session.user):
        frappe.throw("You are not authorized to perform this action.")

    # --- Basic validation ---
    if not className or not divisionName or not students:
        frappe.throw("Class, Division, and Students data are required.")

    # --- Fetch academic context ---
    edu_settings = frappe.get_single("Education Settings")
    year = edu_settings.current_academic_year
    term = edu_settings.current_academic_term

    # --- Validate student data ---
    def is_valid_student(s):
        roll = safe_int(s.get("Roll No"))
        gr = s.get("GR Number", "").strip()
        return roll != float("inf") and roll > 0 and gr

    valid_students = [s for s in students if is_valid_student(s)]
    invalid_students = [s for s in students if not is_valid_student(s)]
    for s in invalid_students:
        print("Skipping invalid row:", s)

    # --- Sort by Roll No ---
    valid_students.sort(key=lambda s: safe_int(s.get("Roll No")))

    # --- Initialize result dictionary ---
    enrollment_results = {}

    try:
        # --- Get existing Student Group ---
        student_group = frappe.get_doc("Student Group", {"program": className, "batch": divisionName})
        if not student_group:
            frappe.throw(f"No Student Group found for Program '{className}' and Division '{divisionName}'")

        # --- Cache existing students & roll numbers ---
        existing_student_ids = {d.student for d in student_group.students}
        next_roll = max([d.group_roll_number or 0 for d in student_group.students], default=0)

        # --- Single loop: Enroll & add to group ---
        added_count = 0
        successful_count = 0
        failed_count = 0
        
        for student in valid_students:
            full_name = f"{student.get('First Name', '').strip()} {student.get('Middle Name', '').strip()} {student.get('Last Name', '').strip()}".strip()
            email = student.get("Email Address", "")
            print(f">>> Enrolling student: {full_name} | Roll No: {student.get('Roll No')}")
            
            # Initialize result entry for this student
            enrollment_results[full_name] = {
                "email": email,
                "status": "pending",
                "message": ""
            }

            try:
                # Enroll student
                enroll_student(student, className, divisionName, year, term)

                # Get enrolled student ID
                student_id = frappe.db.get_value("Student", {"gr_number": student.get("GR Number")}, "name")

                # Add to Student Group if not already there
                if student_id and student_id not in existing_student_ids:
                    next_roll += 1
                    add_student_to_group(student_group, student_id, full_name, next_roll)
                    existing_student_ids.add(student_id)
                    added_count += 1

                # Mark as success
                enrollment_results[full_name]["status"] = "success"
                enrollment_results[full_name]["message"] = f"Successfully enrolled and added to {className} - {divisionName}"
                successful_count += 1
                print(f"✅ Successfully enrolled: {full_name}")

            except Exception as e:
                # Mark as error but continue with next student
                error_msg = str(e)
                enrollment_results[full_name]["status"] = "error"
                enrollment_results[full_name]["message"] = error_msg
                failed_count += 1
                print(f"❌ Failed to enroll {full_name}: {error_msg}")
                # Continue to next student without breaking the loop

        # --- Save group once at end ---
        if added_count > 0:
            student_group.save()
            print(f"✅ Added {added_count} students to Student Group '{student_group.name}'")

        # --- Commit all database changes at the end ---
        frappe.db.commit()

        print(f"✅ Bulk enrollment completed. Successful: {successful_count}, Failed: {failed_count}, Total processed: {len(valid_students)}")

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Bulk Enroll Failed")
        frappe.throw(f"Enrollment process failed: {str(e)}")

    # Prepare response
    enrolled_students = []
    failed_enrollments = []
    
    for name, result in enrollment_results.items():
        if result["status"] == "success":
            enrolled_students.append(name)
        else:
            # Find the student data for failed enrollments
            student_data = next((s for s in valid_students if 
                f"{s.get('First Name', '').strip()} {s.get('Middle Name', '').strip()} {s.get('Last Name', '').strip()}".strip() == name), {})
            failed_enrollments.append({
                "student_data": student_data,
                "error": result["message"]
            })

    return {
        "success": True,
        "message": f"Enrollment completed: {successful_count} successful, {failed_count} failed out of {len(valid_students)} students",
        "enrollment_results": enrollment_results,
        "enrolled_students": enrolled_students,
        "failed_enrollments": failed_enrollments,
        "summary": {
            "total_processed": len(valid_students),
            "successful": successful_count,
            "failed": failed_count,
            "added_to_group": added_count
        }
    }



@frappe.whitelist()
def bulk_enroll_instructors(teachers):
    if not teachers or not isinstance(teachers, list):
        frappe.throw("Invalid input: 'teachers' must be a non-empty list.")

    # --- Initialize result dictionary ---
    enrollment_results = {}
    successful_count = 0
    failed_count = 0

    for teacher in teachers:
        try:
            user_doc = None
            first_name = teacher.get("First Name", "")
            middle_name = teacher.get("Middle Name", "")
            last_name = teacher.get("Last Name", "")
            phone = teacher.get("Mobile", "")
            email = teacher.get("Email", "")
            attendance_device_id = teacher.get("Attendance Device ID (Biometric/RF tag ID)", "")
            full_name = " ".join(filter(None, [first_name, middle_name, last_name])).strip()

            # Initialize result entry for this instructor
            enrollment_results[full_name] = {
                "email": email,
                "status": "pending",
                "message": ""
            }

            # --- Check if Instructor already exists ---
            existing_instructor = frappe.db.exists("Instructor", {"instructor_name": full_name})
            if existing_instructor:
                raise Exception(
                    f"❌ Duplicate Instructor found: {full_name}. "
                    f"Existing record already exists in Instructor doctype."
                )

            # --- Check existing User/Employee ---
            existing_email = frappe.db.exists("User", {"email": email})
            existing_phone = frappe.db.exists("User", {"mobile_no": phone})
            existing_ID = frappe.db.exists("Employee", {"attendance_device_id": attendance_device_id})

            employee_doc = None
            if existing_ID:
                employee_doc = frappe.get_doc("Employee", existing_ID)

            user_doc = None
            if existing_email:
                user_doc = frappe.get_doc("User", existing_email)
            elif existing_phone:
                user_doc = frappe.get_doc("User", existing_phone)
            elif existing_ID and employee_doc and employee_doc.user_id:
                user_doc = frappe.get_doc("User", employee_doc.user_id)

            # --- Duplicate checks for Email / Phone / Attendance ID ---
            if existing_email and "Instructor" in frappe.get_roles(existing_email):
                raise Exception(
                    f"❌ Duplicate email found for existing user: {user_doc.name} ({email}). "
                    f"New record attempted for: {email}"
                )

            if existing_phone and "Instructor" in frappe.get_roles(existing_phone):
                raise Exception(
                    f"❌ Duplicate phone number found for existing user: {user_doc.name} ({phone}). "
                    f"New record attempted for: {phone}"
                )

            if existing_ID and employee_doc and "Instructor" in frappe.get_roles(employee_doc.user_id):
                raise Exception(
                    f"❌ Duplicate Attendance Device ID found for existing user: {user_doc.name} ({attendance_device_id}). "
                    f"New record attempted for: {attendance_device_id}"
                )

            # --- Proceed to creation ---
            gender = teacher.get("Gender", "")
            date_of_birth = teacher.get("Date of Birth", "")
            division = teacher.get("Division", "")
            date_of_joining = teacher.get("Date of Joining", "")
            bank_name = teacher.get("Bank Name", "")
            bank_ac_no = teacher.get("Bank A/C No.", "")
            current_address = teacher.get("Current Address", "")
            permanent_address = teacher.get("Permanent Address", "")
            blood_group = teacher.get("Blood Group", "")
            qualification = teacher.get("Qualification (Education)", "")
            pan_number = teacher.get("PAN Number", "")
            ifsc_code = teacher.get("IFSC Code", "")
            class_name = teacher.get("Class", "")

            # Call the creation function with validation data
            success = create_user_and_instructor(
                full_name, first_name, middle_name, last_name, gender, phone, email, date_of_birth,
                division, attendance_device_id, date_of_joining, bank_name, bank_ac_no, current_address,
                permanent_address, blood_group, qualification, pan_number, ifsc_code,
                class_name, user_doc
            )

            if success:
                # Mark as success
                enrollment_results[full_name]["status"] = "success"
                enrollment_results[full_name]["message"] = f"Successfully enrolled instructor {full_name}"
                successful_count += 1
                print(f"✅ Bulk enrolled: {full_name} ({email})")

        except Exception as e:
            # Mark as error but continue with next instructor
            error_msg = str(e)
            enrollment_results[full_name]["status"] = "error"
            enrollment_results[full_name]["message"] = error_msg
            failed_count += 1
            print(f"❌ Failed to enroll {full_name}: {error_msg}")
            # Continue to next instructor without breaking the loop

    # --- Commit all database changes at the end ---
    frappe.db.commit()

    print(f"✅ Bulk instructor enrollment completed. Successful: {successful_count}, Failed: {failed_count}, Total processed: {len(teachers)}")

    # Prepare response
    enrolled_instructors = []
    failed_enrollments = []
    
    for name, result in enrollment_results.items():
        if result["status"] == "success":
            enrolled_instructors.append(name)
        else:
            # Find the instructor data for failed enrollments
            instructor_data = next((t for t in teachers if 
                " ".join(filter(None, [
                    t.get("First Name", "").strip(),
                    t.get("Middle Name", "").strip(),
                    t.get("Last Name", "").strip()
                ])) == name), {})
            failed_enrollments.append({
                "instructor_data": instructor_data,
                "error": result["message"]
            })

    return {
        "success": True,
        "message": f"Instructor enrollment completed: {successful_count} successful, {failed_count} failed out of {len(teachers)} instructors",
        "enrollment_results": enrollment_results,
        "enrolled_instructors": enrolled_instructors,
        "failed_enrollments": failed_enrollments,
        "summary": {
            "total_processed": len(teachers),
            "successful": successful_count,
            "failed": failed_count
        }
    }


def create_user_and_instructor(full_name, first_name, middle_name, last_name, gender, phone, email, date_of_birth, 
                             division="", attendance_device_id="", date_of_joining="", bank_name="", 
                             bank_ac_no="", current_address="", permanent_address="", blood_group="", 
                             qualification="", pan_number="", ifsc_code="", class_name="", user_doc=None):

    salutation = "Mr" if gender and gender.lower() == "male" else "Ms"
    password = "#pass4AWAMI"

    if not email or not phone:
        raise Exception("Email and Mobile are required")
    
    try:
        # --- Step 1: Create User (only if not provided) ---
        if not user_doc:
            user_doc = frappe.new_doc("User")
            user_doc.first_name = first_name
            user_doc.middle_name = middle_name
            user_doc.last_name = last_name
            user_doc.email = email
            user_doc.username = f"{first_name.lower()}{phone}".replace(" ", "")
            user_doc.mobile_no = phone
            user_doc.date_birth = date_of_birth
            user_doc.send_welcome_email = 0
            user_doc.enabled = 1
            user_doc.user_type = "Website User"
            user_doc.save()
            user_doc.add_roles("Instructor")
     
            # Check if User creation was successful
            if not user_doc.name:
                raise Exception("Failed to create User account")
            
            print(f"✅ User created successfully: {user_doc.name}")
        else:
            print(f"✅ Using existing user: {user_doc.name}")

        # --- Step 2: Create Employee (only if User was successful) ---
        employee_doc = create_employee(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            email=email,
            phone=phone,
            gender=gender,
            salutation=salutation,
            date_of_birth=date_of_birth,
            date_of_joining=date_of_joining,
            bank_name=bank_name,
            bank_ac_no=bank_ac_no,
            current_address=current_address,
            permanent_address=permanent_address,
            blood_group=blood_group,
            attendance_device_id=attendance_device_id,
            qualification=qualification,
            pan_number=pan_number,
            ifsc_code=ifsc_code
        )
        
        # Check if Employee creation was successful
        if not employee_doc or not employee_doc.name:
            raise Exception("Failed to create Employee record")
        
        print(f"✅ Employee created successfully: {employee_doc.name}")

        # --- Step 3: Create Instructor (only if Employee was successful) ---
        instructor_doc = frappe.get_doc({
            "doctype": "Instructor",
            "gender": gender,
            "employee": employee_doc.name,
            "status": "Active"
        })
        instructor_doc.insert()
        
        # Check if Instructor creation was successful
        if not instructor_doc.name:
            raise Exception("Failed to create Instructor record")
        
        print(f"✅ Instructor created successfully: {instructor_doc.name}")

        # --- Step 4: Assign to Student Group (only if all previous steps were successful) ---
        if division:
            try:
                student_group = frappe.get_doc("Student Group", {"student_group_name": division})
                if not any(row.instructor == instructor_doc.name for row in student_group.instructors):
                    student_group.append("instructors", {"instructor": instructor_doc.name})
                    student_group.save()
                    print(f"✅ Instructor assigned to division: {division}")
            except Exception as e:
                print(f"⚠️ Could not add instructor to division '{division}': {e}")
                # Continue without throwing error - instructor is still created
        else:
            print(f"⚠️ Skipping group assignment: No Division for {full_name} ({email})")

        return True

    except Exception as e:
        # Error handling without cleanup
        print(f"❌ Failed to create instructor {full_name}: {str(e)}")
        raise Exception(f"Failed to create instructor {full_name}: {str(e)}")


def create_employee(first_name, middle_name, last_name, email, phone, gender, salutation, date_of_birth,
                   date_of_joining, bank_name, bank_ac_no, current_address, permanent_address, blood_group,
                   attendance_device_id, qualification, pan_number="", ifsc_code=""):
    try:
        dob = frappe.utils.getdate(date_of_birth) if date_of_birth else None
    except Exception as e:
        raise Exception(f"Invalid Date of Birth: {str(e)}")

    doj = frappe.utils.nowdate()
    if date_of_joining:
        try:
            doj = frappe.utils.getdate(date_of_joining)
        except Exception as e:
            raise Exception(f"Invalid Date of Joining: {str(e)}")

    employee_data = {
        "doctype": "Employee",
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "employee_name": " ".join(filter(None, [first_name, middle_name, last_name])).strip(),
        "salutation": salutation,
        "gender": gender,
        "date_of_birth": dob,
        "date_of_joining": doj,
        "cell_number": phone,
        "status": "Active",
        "user_id": email,
        "bank_name": bank_name,
        "bank_ac_no": bank_ac_no,
        "current_address": current_address,
        "permanent_address": permanent_address,
        "blood_group": blood_group,
        "attendance_device_id": attendance_device_id,
        "qualification": qualification,
        "pan_number": pan_number,
        "ifsc_code": ifsc_code
    }
    
    employee_doc = frappe.get_doc(employee_data)
    employee_doc.insert()
    
    return employee_doc


@frappe.whitelist()
def enroll_single_instructor(teacher):
    """Single instructor enrollment - now calls the bulk function internally"""
    try:
        # Convert single teacher to list and call bulk function
        result = bulk_enroll_instructors([teacher])
        
        # Extract the result for the single instructor
        full_name = " ".join(filter(None, [
            teacher.get("First Name", "").strip(),
            teacher.get("Middle Name", "").strip(),
            teacher.get("Last Name", "").strip()
        ]))
        
        if result["success"] and full_name in result["enrolled_instructors"]:
            print(f"✅ Single instructor enrolled: {full_name}")
            return True
        else:
            # Find the error message
            error_msg = result["enrollment_results"].get(full_name, {}).get("message", "Unknown error")
            raise Exception(error_msg)

    except Exception as e:
        print(f"❌ Error while enrolling single instructor: {str(e)}")
        raise Exception(f"❌ Error while enrolling instructor: {str(e)}")