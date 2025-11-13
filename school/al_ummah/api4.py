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


def generate_unique_email(first_name, last_name, name):
    base_name = f"{first_name}.{last_name}".replace(" ", ".").lower()
    gr = str(name).strip().lower().replace(" ", "")
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
                user_doc.new_password = "alummah"
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
def enroll_single_student(student_data, className, divisionName, generate_qr_code):
    # print(student_data, className, divisionName)

    # --- Permission check ---
    if "Administrator" not in frappe.get_roles(frappe.session.user):
        frappe.throw("You are not authorized to perform this action.")

    # --- Basic validation ---
    if not student_data or not className or not divisionName:
        frappe.throw("Student data, class, and division are required.")

    # --- Academic context ---
    edu_settings = frappe.get_single("Education Settings")
    year = edu_settings.current_academic_year
    term = edu_settings.current_academic_term

    try:
        # --- Enroll the student ---
        enroll_student(student_data, className, divisionName, year, term, generate_qr_code)

        gr_num = f"GR-{student.get("GR Number")}"
        # --- Get the Student doc name after enrollment ---
        student_id = frappe.db.get_value(
            "Student", {"name": gr_num}, "name"
        )
        if not student_id:
            frappe.throw(f"Could not find enrolled Student with GR Number {gr_num}")

        full_name = " ".join(
            part for part in [
                student_data.get("First Name", "").strip(),
                student_data.get("Middle Name", "").strip(),
                student_data.get("Last Name", "").strip()
            ] if part
        )

        # --- Get the Student Group ---
        student_group = frappe.get_doc("Student Group", {"program": className, "batch": divisionName})
        if not student_group:
            frappe.throw(f"No Student Group found for Program '{className}' and Division '{divisionName}'")

        # --- Determine next roll number ---
        existing_student_ids = {d.student for d in student_group.students}
        max_roll_no = max([d.group_roll_number or 0 for d in student_group.students], default=0)

        # --- Add to Student Group if not already present ---
        if student_id not in existing_student_ids:
            max_roll_no += 1
            add_student_to_group(student_group, student_id, full_name, max_roll_no)
            student_group.save(ignore_permissions=True)

        frappe.db.commit()
        print(f"✅ Student {full_name} enrolled and added to Student Group {student_group.name}")

    except Exception as e:
        frappe.db.rollback()
        frappe.throw(f"Enrollment failed: {str(e)}")

    return {"status": "success", "message": "Student enrolled and added to Student Group successfully!"}

@frappe.whitelist()
def enroll_student(student, className, divisionName, year, term, generate_qr_code):
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

    gr_num = f"GR-{student.get("GR Number")}"
    if frappe.db.exists("Student", {"name": gr_num}):
        frappe.throw(_("Duplicate GR Number for: {0}, {1}").format(full_name, gr_num))

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
        # student_doc.name = student["GR Number"]
        student_doc.save(ignore_permissions=True)
        # ✅ Generate QR Code if enabled
        if generate_qr_code:
            import qrcode
            import base64
            from io import BytesIO

            qr_data = f"{student_doc.name} / {student_doc.name} - {student_doc.student_name}"

            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)

            img = qr.make_image()
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            image_data = buffer.getvalue()

            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": f"{student_doc.name}_qr.png",
                "content": image_data,
                "attached_to_doctype": "Student",
                "attached_to_name": student_doc.name,
                "is_private": 0
            })

            file_doc.insert(ignore_permissions=True)

            # ✅ Do NOT use save() again — use db_set()
            student_doc.db_set("qr_code", file_doc.file_url)
        
        # ✅ Rename Student document to "GR-{GR Number}" format
        name = student["GR Number"]
        new_doc_name = f"GR-{name}"
        auto_name = student_doc.name

        if auto_name != new_doc_name:
            try:
                print(f"📝 Renaming {auto_name} to {new_doc_name}")
                frappe.rename_doc("Student", auto_name, new_doc_name, force=True)
                # Update the student_doc reference after successful rename
                student_doc = frappe.get_doc("Student", new_doc_name)
                print(f"✅ Student renamed successfully to: {student_doc.name}")
            except Exception as rename_error:
                print(f"⚠️ Rename failed: {str(rename_error)}")
                # Continue with the auto-generated name - student is still created
        else:
            print(f"✅ Student already has correct name: {student_doc.name}")

        
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
def bulk_enroll_students(className, divisionName, generate_qr_code, students):
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
        student_group = frappe.get_doc("Student Group", divisionName)
        # student_group = frappe.get_doc("Student Group", {"program": className, "batch": divisionName})
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
                enroll_student(student, className, divisionName, year, term, generate_qr_code)
                gr_num = f"GR-{student.get("GR Number")}"
                # Get enrolled student ID
                student_id = frappe.db.get_value("Student", {"name": gr_num}, "name")

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
    password = "alummah"

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
            user_doc.new_password = password
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


# api4.py - Updated with correct field names

import frappe
import json
import hmac
import hashlib
import requests
from frappe.utils import nowdate, getdate, flt, now_datetime, get_datetime

@frappe.whitelist()
def process_student_payment(student_id, invoice_names, mode_of_payment, paid_to_account, paid_amount, cheque_no=None, cheque_date=None):
    """
    Process student payment for selected invoices using unified payment entry method
    Accepts either:
    - Student.name (primary key) 
    - GR Number (name field)
    """
    try:
        # Validate input parameters
        if not all([student_id, invoice_names, mode_of_payment, paid_to_account, paid_amount]):
            frappe.throw("Missing required parameters")

        # Convert string inputs to proper types
        if isinstance(invoice_names, str):
            try:
                invoice_names = json.loads(invoice_names)
            except json.JSONDecodeError:
                frappe.throw("Invalid invoice_names format - must be valid JSON")
        
        paid_amount = flt(paid_amount)

        # -----------------------------------------------------
        # ✅ Step 1: Resolve Student ID (handle both ID and GR Number)
        # -----------------------------------------------------
        resolved_student_id = None
        student_id = f"GR-{student_id}"
        # Case 1 → Direct student ID exists
        if frappe.db.exists("Student", student_id):
            resolved_student_id = student_id

        # Case 2 → Maybe 'student_id' is actually a GR Number
        else:
            resolved_student_id = frappe.db.get_value(
                "Student",
                {"name": student_id},
                "name"
            )

        if not resolved_student_id:
            frappe.throw(f"No student found for ID/GR Number: {student_id}")

        # Get student document for validation
        student_doc = frappe.get_doc("Student", resolved_student_id)
        normalized_student_id = student_doc.name

        # Validate invoices exist and belong to the student
        valid_invoices = []
        total_outstanding = 0
        
        for invoice_name in invoice_names:
            try:
                invoice = frappe.get_doc("Sales Invoice", invoice_name)
                
                # Check if invoice belongs to the student - compare normalized IDs
                if invoice.student != normalized_student_id:
                    frappe.throw(f"Invoice {invoice_name} belongs to student '{invoice.student}' but you're trying to pay for student '{normalized_student_id}'")
                
                # Check if invoice is unpaid
                if invoice.outstanding_amount > 0:
                    valid_invoices.append({
                        "name": invoice.name,
                        "customer": invoice.customer,
                        "grand_total": invoice.grand_total,
                        "outstanding_amount": invoice.outstanding_amount
                    })
                    total_outstanding += invoice.outstanding_amount
                else:
                    frappe.throw(f"Invoice {invoice_name} is already paid")
                    
            except frappe.DoesNotExistError:
                frappe.throw(f"Invoice {invoice_name} not found")

        if not valid_invoices:
            frappe.throw("No valid unpaid invoices found")
        
        # -----------------------------------------------------
        # ✅ FIXED: Better amount validation with rounding tolerance
        # -----------------------------------------------------
        total_outstanding = flt(total_outstanding, 2)  # Ensure 2 decimal precision
        paid_amount = flt(paid_amount, 2)  # Ensure 2 decimal precision
        
        # Calculate difference and allow for small rounding errors
        amount_difference = abs(paid_amount - total_outstanding)
        
        # Allow for rounding differences up to 0.10 (10 cents) or 0.1%
        rounding_tolerance = max(0.10, total_outstanding * 0.001)  # Whichever is larger
        
        if amount_difference > rounding_tolerance:
            frappe.throw(f"Paid amount ({paid_amount}) does not match total outstanding amount ({total_outstanding}). Difference: {amount_difference}")
        
        # Validate account exists
        if not frappe.db.exists("Account", paid_to_account):
            frappe.throw(f"Account {paid_to_account} not found")
        
        # Validate mode of payment exists
        if not frappe.db.exists("Mode of Payment", mode_of_payment):
            frappe.throw(f"Mode of Payment {mode_of_payment} not found")
        
        # Use the validated total_outstanding amount to avoid rounding issues
        validated_paid_amount = total_outstanding
        
        # Create single payment entry for all invoices
        payment_entry_name = create_payment_entry(
            invoice_data=valid_invoices,
            mode_of_payment=mode_of_payment,
            paid_to_account=paid_to_account,
            paid_amount=validated_paid_amount,  # Use the calculated total
            cheque_no=cheque_no,
            cheque_date=cheque_date,
            student_id=normalized_student_id
        )
        
        # Update invoice statuses
        update_invoice_status([inv["name"] for inv in valid_invoices])
        frappe.db.commit()
        
        # Generate PDF download URL
        pdf_download_url = generate_pdf_download_url(payment_entry_name)
        
        return {
            "success": True,
            "message": f"Payment processed successfully for {len(valid_invoices)} invoice(s)",
            "processed_invoices": [inv["name"] for inv in valid_invoices],
            "total_amount": validated_paid_amount,
            "mode_of_payment": mode_of_payment,
            "payment_date": nowdate(),
            "payment_entry": payment_entry_name,
            "resolved_student_id": normalized_student_id,
            "calculated_total": total_outstanding,
            "paid_amount_received": paid_amount,
            "pdf_download_url": pdf_download_url  # Add PDF URL to response
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.throw(str(e))

# def generate_pdf_download_url(payment_entry_name):
#     """
#     Simple approach with direct port removal
#     """
#     try:
#         from frappe.utils import get_url
#         import re
        
#         # Ensure payment_entry_name is a string
#         if isinstance(payment_entry_name, dict):
#             payment_entry_name = payment_entry_name.get('payment_entry')
        
#         if not payment_entry_name or not frappe.db.exists("Payment Entry", payment_entry_name):
#             return None
        
#         # Your custom printview URL
#         printview_url_path = f"/printview?" \
#                            f"doctype=Payment%20Entry&" \
#                            f"name={payment_entry_name}&" \
#                            f"trigger_print=1&" \
#                            f"format=test&" \
#                            f"no_letterhead=1&" \
#                            f"letterhead=No%20Letterhead&" \
#                            f"settings=%7B%7D&" \
#                            f"_lang=en"
        
#         # Get URL and remove port using regex
#         full_url = get_url(printview_url_path)
#         clean_url = re.sub(r':\d+', '', full_url)  # Remove :8000, :8080, etc.
        
#         print(f"Clean URL without port: {clean_url}")
#         return clean_url
        
#     except Exception as e:
#         frappe.log_error(f"Error: {str(e)}")
#         return None

def generate_pdf_download_url(payment_entry_name):
    """
    Generate mobile-compatible PDF download URL
    """
    try:
        from frappe.utils import get_url
        import re
        
        if isinstance(payment_entry_name, dict):
            payment_entry_name = payment_entry_name.get('payment_entry')
        
        if not payment_entry_name or not frappe.db.exists("Payment Entry", payment_entry_name):
            return None
        
        # Create a simpler URL that's more likely to work on mobile
        pdf_url_path = f"/api/method/frappe.utils.print_format.download_pdf"
        
        # Build the full URL with parameters
        from urllib.parse import urlencode
        params = {
            'doctype': 'Payment Entry',
            'name': payment_entry_name,
            'format': 'test',
            'no_letterhead': 1,
            'letterhead': 'No Letterhead',
            'orientation': 'Landscape',
            'force_download': 1
        }
        
        query_string = urlencode(params)
        full_url = f"{get_url(pdf_url_path)}?{query_string}"
        clean_url = re.sub(r':\d+', '', full_url)
        
        print(f"Mobile PDF URL: {clean_url}")
        return clean_url
        
    except Exception as e:
        frappe.log_error(f"Error generating PDF URL: {str(e)}")
        return None
        
def create_payment_entry(invoice_data, mode_of_payment, paid_to_account, paid_amount, 
                       razorpay_payment_id=None, razorpay_order_id=None, razorpay_payment_details=None,
                       cheque_no=None, cheque_date=None, student_id=None):
    try:
        if not invoice_data or len(invoice_data) == 0:
            return {"success": False, "message": "No invoice data provided"}

        first_invoice_name = invoice_data[0]["name"]
        first_invoice = frappe.get_doc("Sales Invoice", first_invoice_name)
        company = first_invoice.company
        customer = first_invoice.customer

        payment_entry = frappe.new_doc("Payment Entry")
        
        payment_entry.payment_type = "Receive"
        payment_entry.mode_of_payment = mode_of_payment
        payment_entry.party_type = "Customer"
        payment_entry.party = customer
        payment_entry.paid_amount = paid_amount
        payment_entry.received_amount = paid_amount
        payment_entry.paid_to = paid_to_account
        payment_entry.company = company
        payment_entry.posting_date = nowdate()

        if mode_of_payment == "Cheque":
            if not cheque_no or not cheque_date:
                return {"success": False, "message": "Cheque number and date are required for cheque payments"}
            payment_entry.reference_no = cheque_no
            payment_entry.reference_date = getdate(cheque_date)
        
        elif razorpay_payment_id:
            payment_entry.reference_no = razorpay_payment_id
            payment_entry.reference_date = nowdate()

        if student_id:
            payment_entry.student = student_id
        
        if razorpay_order_id:
            payment_entry.razorpay_order_id = razorpay_order_id
        if razorpay_payment_id:
            payment_entry.razorpay_payment_id = razorpay_payment_id
        if razorpay_payment_details:
            payment_entry.razorpay_payment_details = json.dumps(razorpay_payment_details)
        
        payment_entry.remarks = f"Payment for {len(invoice_data)} invoice(s) via {mode_of_payment}"

        for invoice in invoice_data:
            payment_entry.append("references", {
                "reference_doctype": "Sales Invoice",
                "reference_name": invoice["name"],
                "total_amount": invoice["grand_total"],
                "outstanding_amount": invoice["outstanding_amount"],
                "allocated_amount": invoice["outstanding_amount"]
            })

        payment_entry.insert(ignore_permissions=True)
        payment_entry.submit()

        return {
            "success": True,
            "payment_entry": payment_entry.name
        }
        
    except Exception as e:
        frappe.log_error(f"Failed to create payment entry: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to create payment entry: {str(e)}"
        }

def update_invoice_status(invoice_names):
    for invoice_name in invoice_names:
        frappe.db.set_value("Sales Invoice", invoice_name, "status", "Paid")
        frappe.db.set_value("Sales Invoice", invoice_name, "outstanding_amount", 0)

def rollback_payments(processed_invoices):
    try:
        for invoice_name in processed_invoices:
            payment_entries = frappe.get_all("Payment Entry Reference", 
                filters={"reference_name": invoice_name},
                fields=["parent"]
            )
            
            for pe in payment_entries:
                payment_entry = frappe.get_doc("Payment Entry", pe.parent)
                if payment_entry.docstatus == 1:
                    payment_entry.cancel()
                elif payment_entry.docstatus == 0:
                    payment_entry.delete()
                    
    except Exception as e:
        frappe.log_error(f"Error rolling back payments: {str(e)}")

@frappe.whitelist()
def get_all_paid_to_accounts():
    try:
        company = frappe.defaults.get_user_default("company")
        
        if not company:
            companies = frappe.get_all("Company", fields=["name"])
            if companies:
                company = companies[0].name
            else:
                return {
                    "success": False,
                    "message": "No company found"
                }
        
        accounts = frappe.get_all("Account", 
            filters={
                "company": company,
                "is_group": 0,
                "account_type": ["in", ["Receivable", "Bank", "Cash"]]
            },
            fields=["name", "account_name", "account_type", "company"],
            order_by="account_type, account_name"
        )
        
        return {
            "success": True,
            "accounts": accounts,
            "company": company
        }
        
    except Exception as e:
        frappe.log_error(f"Error fetching paid to accounts: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to fetch accounts: {str(e)}",
            "accounts": []
        }

@frappe.whitelist()
def get_sales_invoices_by_student(student_id):
    """
    Get all unpaid sales invoices for a student.
    Accepts either:
    - Student.name  (primary key)
    - GR Number (name field)
    """

    try:
        if not student_id:
            return {
                "success": False,
                "message": "Student ID or GR Number is required"
            }

        # -----------------------------------------------------
        # Step 1: Resolve Student ID
        # -----------------------------------------------------

        resolved_student = None
        gr_num = f"GR-{student_id}"
        
        resolved_student = frappe.db.get_value(
            "Student",
            {"name": gr_num},
            "name"
        )

        # -----------------------------------------------------
        # Step 2: Get Student Data and Group Information
        # -----------------------------------------------------

        student_data = frappe.db.get_value(
            "Student",
            resolved_student,
            [
                "name", 
                "student_name", 
                "image",
                "student_email_id", 
                "student_mobile_number"
            ],
            as_dict=True
        )

        student_groups = frappe.get_all(
            "Student Group Student",
            filters={"student": resolved_student},
            fields=["parent as student_group", "group_roll_number"],
            order_by="creation desc"
        )

        # -----------------------------------------------------
        # Step 3: Get Guardian Information
        # -----------------------------------------------------

        guardian_details = []
        
        # Get guardians using get_doc to access child tables
        student_doc = frappe.get_doc("Student", resolved_student)
        
        # Check if guardians child table exists
        if hasattr(student_doc, 'guardians') and student_doc.guardians:
            for guardian_rel in student_doc.guardians:
                guardian_name = getattr(guardian_rel, 'guardian', None)
                if not guardian_name:
                    guardian_name = getattr(guardian_rel, 'guardian_name', None)
                
                if guardian_name:
                    # Get detailed guardian information from Guardian doctype
                    guardian_info = frappe.db.get_value(
                        "Guardian",
                        guardian_name,
                        [
                            "name",
                            "guardian_name", 
                            "email_address", 
                            "mobile_number",
                            "education",
                            "occupation"
                        ],
                        as_dict=True
                    )
                    
                    if guardian_info:
                        guardian_details.append({
                            "name": guardian_info.name,
                            "guardian_name": guardian_info.guardian_name,
                            "email_address": guardian_info.email_address,
                            "mobile_number": guardian_info.mobile_number,
                            "education": guardian_info.education,
                            "occupation": guardian_info.occupation,
                            "relation": getattr(guardian_rel, 'relation', 'Guardian')
                        })
                    else:
                        # Fallback: use basic info from child table
                        guardian_details.append({
                            "name": guardian_name,
                            "guardian_name": getattr(guardian_rel, 'guardian_name', guardian_name),
                            "relation": getattr(guardian_rel, 'relation', 'Guardian')
                        })

        # Add all data to student_data
        if student_data:
            student_data["student_groups"] = student_groups
            student_data["guardians"] = guardian_details

        # -----------------------------------------------------
        # Step 4: Fetch unpaid sales invoices with items
        # -----------------------------------------------------

        invoices = frappe.get_all(
            "Sales Invoice",
            filters={
                "student": resolved_student,
                "docstatus": 1,  # 1 = Submitted
                "outstanding_amount": [">", 0]
            },
            fields=[
                "name", "customer", "customer_name", "student",
                "posting_date", "grand_total", "outstanding_amount",
                "status", "due_date", "company", "currency"
            ],
            order_by="posting_date desc"
        )

        # -----------------------------------------------------
        # Step 5: Get detailed items for each invoice
        # -----------------------------------------------------

        for invoice in invoices:
            # Get items for this invoice
            items = frappe.get_all(
                "Sales Invoice Item",
                filters={"parent": invoice.name},
                fields=[
                    "name",
                    "item_code",
                    "item_name",
                    "description",
                    "qty",
                    "rate",
                    "amount",
                    "income_account"
                ],
                order_by="idx"
            )
            
            # Add items to invoice
            invoice["items"] = items
            
            # Format currency fields for display
            invoice["grand_total_formatted"] = f"₹{float(invoice.grand_total or 0):,.2f}"
            invoice["outstanding_amount_formatted"] = f"₹{float(invoice.outstanding_amount or 0):,.2f}"
            
            # Calculate paid amount
            invoice["paid_amount"] = float(invoice.grand_total or 0) - float(invoice.outstanding_amount or 0)
            invoice["paid_amount_formatted"] = f"₹{invoice['paid_amount']:,.2f}"

        # -----------------------------------------------------
        # Step 6: Prepare final response
        # -----------------------------------------------------
        
        response_data = {
            "success": True,
            "student_input": student_id,
            "resolved_student_id": resolved_student,
            "student_data": student_data,
            "count": len(invoices),
            "invoices": invoices,
            "summary": {
                "total_invoices": len(invoices),
                "total_outstanding": sum(float(inv.outstanding_amount or 0) for inv in invoices),
                "total_paid": sum(float(inv.get('paid_amount', 0) or 0) for inv in invoices)
            }
        }

        # Format summary amounts
        response_data["summary"]["total_outstanding_formatted"] = f"₹{response_data['summary']['total_outstanding']:,.2f}"
        response_data["summary"]["total_paid_formatted"] = f"₹{response_data['summary']['total_paid']:,.2f}"

        return response_data

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_sales_invoices_by_student Error")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "student_input": student_id
        }

@frappe.whitelist(allow_guest=True)
def verify_razorpay_payment(razorpay_payment_id, razorpay_order_id, razorpay_signature, 
                          invoice_names, student_id, paid_to_account, paid_amount):
    """
    Verify Razorpay payment and process using unified payment entry
    """
    try:
        # Get Razorpay secret key from Frappe settings
        razorpay_settings = frappe.get_single("Razorpay Settings")
        secret_key = razorpay_settings.get_password("api_secret")
        
        if not secret_key:
            return {
                "success": False,
                "message": "Razorpay API secret not configured"
            }
        
        # Verify the signature
        payload = f"{razorpay_order_id}|{razorpay_payment_id}"
        generated_signature = hmac.new(
            secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        if not hmac.compare_digest(generated_signature, razorpay_signature):
            return {
                "success": False,
                "message": "Invalid payment signature"
            }

        # Fetch payment details from Razorpay API for additional verification
        payment_details = get_razorpay_payment_details(razorpay_payment_id, secret_key)
        
        if not payment_details or payment_details.get('status') != 'captured':
            return {
                "success": False,
                "message": "Payment not captured or invalid"
            }

        # Convert string inputs to proper types
        if isinstance(invoice_names, str):
            try:
                invoice_names = json.loads(invoice_names)
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "message": "Invalid invoice_names format"
                }
        
        paid_amount = flt(paid_amount)

        # -----------------------------------------------------
        # ✅ Step 1: Resolve Student ID (handle both ID and GR Number)
        # -----------------------------------------------------
        resolved_student_id = None

        student_id = f"GR-{student_id}"
        # Case 1 → Direct student ID exists
        if frappe.db.exists("Student", student_id):
            resolved_student_id = student_id

        # Case 2 → Maybe 'student_id' is actually a GR Number
        else:
            resolved_student_id = frappe.db.get_value(
                "Student",
                {"name": student_id},
                "name"
            )

        if not resolved_student_id:
            return {
                "success": False,
                "message": f"No student found for ID/GR Number: {student_id}"
            }

        # Get student document for validation
        student_doc = frappe.get_doc("Student", resolved_student_id)
        normalized_student_id = student_doc.name

        # Validate invoices exist and belong to the student
        valid_invoices = []
        total_outstanding = 0
        
        for invoice_name in invoice_names:
            try:
                invoice = frappe.get_doc("Sales Invoice", invoice_name)
                
                # Check if invoice belongs to the student - compare normalized IDs
                if invoice.student != normalized_student_id:
                    return {
                        "success": False,
                        "message": f"Invoice {invoice_name} belongs to student '{invoice.student}' but you're trying to pay for student '{normalized_student_id}'"
                    }
                
                # Check if invoice is unpaid
                if invoice.outstanding_amount > 0:
                    valid_invoices.append({
                        "name": invoice.name,
                        "customer": invoice.customer,
                        "grand_total": invoice.grand_total,
                        "outstanding_amount": invoice.outstanding_amount
                    })
                    total_outstanding += invoice.outstanding_amount
                else:
                    return {
                        "success": False,
                        "message": f"Invoice {invoice_name} is already paid"
                    }
                    
            except frappe.DoesNotExistError:
                return {
                    "success": False,
                    "message": f"Invoice {invoice_name} not found"
                }

        if not valid_invoices:
            return {
                "success": False,
                "message": "No valid unpaid invoices found"
            }
        
        # -----------------------------------------------------
        # ✅ FIXED: Better amount validation with rounding tolerance
        # -----------------------------------------------------
        total_outstanding = flt(total_outstanding, 2)  # Ensure 2 decimal precision
        paid_amount = flt(paid_amount, 2)  # Ensure 2 decimal precision
        
        # Calculate difference and allow for small rounding errors
        amount_difference = abs(paid_amount - total_outstanding)
        
        # Allow for rounding differences up to 0.10 (10 cents) or 0.1%
        rounding_tolerance = max(0.10, total_outstanding * 0.001)  # Whichever is larger
        
        if amount_difference > rounding_tolerance:
            return {
                "success": False,
                "message": f"Paid amount ({paid_amount}) does not match total outstanding amount ({total_outstanding}). Difference: {amount_difference}"
            }
        
        # Verify payment amount matches invoice total (from Razorpay)
        payment_amount = payment_details.get('amount', 0) / 100
        payment_amount = flt(payment_amount, 2)
        
        if abs(payment_amount - total_outstanding) > rounding_tolerance:
            return {
                "success": False,
                "message": f"Payment amount mismatch. Expected: {total_outstanding}, Paid: {payment_amount}"
            }
        
        # Validate account exists
        if not frappe.db.exists("Account", paid_to_account):
            return {
                "success": False,
                "message": f"Account {paid_to_account} not found"
            }
        
        # Use "Online" as mode of payment for Razorpay transactions
        mode_of_payment = "Online"
        
        # Validate mode of payment exists
        if not frappe.db.exists("Mode of Payment", mode_of_payment):
            return {
                "success": False,
                "message": f"Mode of Payment {mode_of_payment} not found"
            }
        
        # Use the validated total_outstanding amount to avoid rounding issues
        validated_paid_amount = total_outstanding
        
        # Create SINGLE payment entry for ALL invoices
        payment_result = create_payment_entry(
            invoice_data=valid_invoices,
            mode_of_payment=mode_of_payment,
            paid_to_account=paid_to_account,
            paid_amount=validated_paid_amount,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_details=payment_details,
            student_id=normalized_student_id
        )
        
        if payment_result.get("success"):
            # Update invoice statuses
            update_invoice_status([inv["name"] for inv in valid_invoices])
            frappe.db.commit()
            
            # Generate PDF download URL
            pdf_download_url = generate_pdf_download_url(payment_result.get("payment_entry"))
            
            return {
                "success": True,
                "message": "Payment processed successfully",
                "payment_id": razorpay_payment_id,
                "invoices_processed": [inv["name"] for inv in valid_invoices],
                "amount": validated_paid_amount,
                "mode_of_payment": mode_of_payment,
                "payment_entry": payment_result.get("payment_entry"),
                "resolved_student_id": normalized_student_id,
                "calculated_total": total_outstanding,
                "paid_amount_received": paid_amount,
                "pdf_download_url": pdf_download_url  # Add PDF URL to response
            }
        else:
            frappe.db.rollback()
            return payment_result
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Razorpay payment processing failed: {str(e)}")
        return {
            "success": False,
            "message": f"Payment processing failed: {str(e)}"
        }

def get_razorpay_payment_details(payment_id, secret_key):
    """
    Fetch payment details from Razorpay API
    """
    try:
        razorpay_settings = frappe.get_single("Razorpay Settings")
        key_id = razorpay_settings.api_key
        
        auth = (key_id, secret_key)
        response = requests.get(
            f"https://api.razorpay.com/v1/payments/{payment_id}",
            auth=auth,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            frappe.log_error(f"Razorpay API error: {response.text}")
            return None
            
    except Exception as e:
        frappe.log_error(f"Failed to fetch Razorpay payment: {str(e)}")
        return None

def get_razorpay_order_details(order_id, secret_key):
    """
    Fetch order details from Razorpay API
    """
    try:
        razorpay_settings = frappe.get_single("Razorpay Settings")
        key_id = razorpay_settings.api_key
        
        auth = (key_id, secret_key)
        response = requests.get(
            f"https://api.razorpay.com/v1/orders/{order_id}",
            auth=auth,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            frappe.log_error(f"Razorpay Order API error: {response.text}")
            return None
            
    except Exception as e:
        frappe.log_error(f"Failed to fetch Razorpay order: {str(e)}")
        return None

@frappe.whitelist()
def create_razorpay_order(invoice_names, student_id, total_amount, paid_to_account):
    """
    Create Razorpay order for the selected invoices
    """
    try:
        razorpay_settings = frappe.get_single("Razorpay Settings")
        secret_key = razorpay_settings.get_password("api_secret")
        key_id = razorpay_settings.api_key
        
        if not key_id or not secret_key:
            return {
                "success": False,
                "message": "Razorpay credentials not configured. Please set up API Key and API Secret in Razorpay Settings."
            }
        
        # Convert amount to paise (Razorpay requirement)
        amount_in_paise = int(float(total_amount) * 100)
        
        # Create order data
        order_data = {
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": f"stu_{student_id}_{now_datetime().strftime('%Y%m%d_%H%M%S')}",
            "notes": {
                "student_id": student_id,
                "invoice_names": json.dumps(invoice_names),
                "paid_to_account": paid_to_account,
                "description": f"Payment for {len(invoice_names)} invoice(s)"
            },
            "payment_capture": 1
        }
        
        # Create order via Razorpay API
        auth = (key_id, secret_key)
        response = requests.post(
            "https://api.razorpay.com/v1/orders",
            json=order_data,
            auth=auth,
            timeout=10
        )
        
        if response.status_code == 200:
            order_data = response.json()
            return {
                "success": True,
                "order_id": order_data['id'],
                "amount": order_data['amount'],
                "currency": order_data['currency'],
                "key_id": key_id
            }
        else:
            frappe.log_error(f"Razorpay order creation failed: {response.text}")
            return {
                "success": False,
                "message": "Failed to create payment order. Please check Razorpay settings."
            }
            
    except Exception as e:
        frappe.log_error(f"Razorpay order creation error: {str(e)}")
        return {
            "success": False,
            "message": f"Payment setup failed: {str(e)}"
        }

@frappe.whitelist()
def get_razorpay_settings_status():
    """
    Check if Razorpay settings are configured
    """
    try:
        razorpay_settings = frappe.get_single("Razorpay Settings")
        has_key_id = bool(razorpay_settings.api_key)
        has_secret_key = bool(razorpay_settings.get_password("api_secret"))
        
        return {
            "success": True,
            "configured": has_key_id and has_secret_key,
            "has_key_id": has_key_id,
            "has_secret_key": has_secret_key
        }
    except Exception as e:
        return {
            "success": False,
            "configured": False,
            "error": str(e)
        }