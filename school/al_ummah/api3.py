import json
import frappe
import base64
from io import BytesIO
from datetime import datetime
from frappe import _
from frappe.utils.data import cstr, flt, getdate
from frappe.model.mapper import get_mapped_doc
from frappe.utils.dateutils import get_dates_from_timegrain
from frappe.model.document import Document
from frappe.utils.file_manager import save_file
from frappe.utils.response import build_response
from frappe.auth import get_logged_user

#qdsr itqf nmqx zmni

import frappe

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



@frappe.whitelist(allow_guest=True)
def create_email_account(email_id, password, append_to=None):
    if "Administrator" not in frappe.get_roles(frappe.session.user):
        frappe.throw("You are not authorized to perform this action.")
    email_dict = {
        "email_id": email_id,
        "service": "GMail",
        "password": password,
        "enable_outgoing": 1,
        "default_outgoing": 1,
        "enable_incoming": 0,
        "append_to": append_to,
        "use_tls": 1, 
        "smtp_server": "smtp.gmail.com",
        "smtp_port": "587",
        "use_imap": 0,
    }

    email_account = frappe.new_doc("Email Account")
    email_account.update(email_dict)
    email_account.save(ignore_permissions=True)
 
 
@frappe.whitelist()
def set_instructor_token(token):
    if "Administrator" not in frappe.get_roles(frappe.session.user):
        frappe.throw("You are not authorized to perform this action.")
    token_doc = frappe.get_single("Instructor Token")
    token_doc.token = token
    token_doc.save()
    
@frappe.whitelist()
def get_classes():
    classes = frappe.get_all("Program")
    return classes

@frappe.whitelist()
def get_divisions2(values):
    class_name = values.get("classId")  # Extract classId from the values dictionary
    year = values.get("academicYear")
    divisions = frappe.get_all("Student Group", filters={"program": class_name, "academic_year": year})
    return divisions

@frappe.whitelist()
def get_divisions1(values):
    class_name = values.get("classId")  # Extract classId from the values dictionary
    edu_settings = frappe.get_single("Education Settings")
    year = edu_settings.current_academic_year
    divisions = frappe.get_all("Student Group", filters={"program": class_name, "academic_year": year})
    return divisions

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
def get_previous_data():
    if "Administrator" not in frappe.get_roles(frappe.session.user):
        frappe.throw("You are not authorized to perform this action.")
    previous_docs = frappe.get_all("Previous Class Structure", fields=["json_data"])
    
    # Print the entire result for debugging
    # print(previous_docs)

    return previous_docs  # Return data if needed

def save_previous_class_structure(values):
    try:
        academic_year = values.get("academicYear")
        structure_doc = frappe.new_doc("Previous Class Structure")
        structure_doc.academic_year = academic_year
        # Convert dictionary to JSON string
        structure_doc.json_data = json.dumps(values)
        structure_doc.save(ignore_permissions=True)
    except Exception as e:
        # Log any errors but don't stop the execution
        frappe.log_error(f"Error saving Previous Class Structure: {str(e)}", "Quick Setup Error")
        
@frappe.whitelist()
def quick_setup(values):
    if "Administrator" not in frappe.get_roles(frappe.session.user):
        frappe.throw("You are not authorized to perform this action.")
    try:    
        # Extract academicYear, term, and institutionName from values
        academic_year = values.get("academicYear")
        terms = values.get("terms", [])
        # institution_name = values.get("institutionName")
        logo = values.get("logo")
        academic_year_start = values.get("academicYearStart")
        academic_year_end = values.get("academicYearEnd")
        current_term = values.get("selectedTerm")
        
        if not academic_year or not terms:
            raise frappe.ValidationError("Missing required fields: academicYear, term, or institutionName.")
        
        # if institution_name or logo:
        #     set_institution_details(institution_name, logo)
        
        # Set academic details
        set_academic_details(
            academic_year, academic_year_start, academic_year_end, terms, current_term
        )
        save_previous_class_structure(values)
        
        # Commit changes to the database
        create_program_and_groups_with_courses(values)

        frappe.db.commit()
            
    except Exception as e:
        frappe.log_error(f"Error in quick setup: {str(e)}", "Quick Setup Error")
        return {"status": "failed", "message": f"Error in quick setup: {str(e)}"}


@frappe.whitelist()
def create_program_and_groups_with_courses(values):
    if "Administrator" not in frappe.get_roles(frappe.session.user):
        frappe.throw("You are not authorized to perform this action.")

    try:
        classes = values.get("classes")
        academic_year_name = values.get("academicYear")
        dont_create_classes = values.get("dontCreateClasses", False)

        for class_info in classes:
            class_name = class_info.get("className")
            class_subjects = class_info.get("subjects", [])
            divisions = class_info.get("divisions", [])

            program_exists = frappe.db.exists("Program", {"program_name": class_name})
            program_doc = None

            # ✅ Create program only if needed
            if not dont_create_classes and not program_exists:
                program_doc = frappe.new_doc("Program")
                program_doc.program_name = class_name

                if not class_subjects:
                    frappe.log_error(f"No subjects for class {class_name}. Skipping program creation.", "Program Creation Error")
                    continue

                for subject in class_subjects:
                    subject_name = f"{subject} ({class_name})"

                    # ✅ Skip course creation if it already exists
                    if not frappe.db.exists("Course", {"course_name": subject_name}):
                        course_doc = frappe.new_doc("Course")
                        course_doc.course_name = subject_name
                        course_doc.save(ignore_permissions=True)
                        frappe.db.commit()

                    # ✅ Add course to program if creating the program
                    program_course = program_doc.append("courses", {})
                    program_course.course = subject_name
                    program_course.course_name = subject

                program_doc.save(ignore_permissions=True)
                frappe.db.commit()

            # ✅ Always ensure courses exist even if program already exists
            for subject in class_subjects:
                subject_name = f"{subject} ({class_name})"
                if not frappe.db.exists("Course", {"course_name": subject_name}):
                    course_doc = frappe.new_doc("Course")
                    course_doc.course_name = subject_name
                    course_doc.save(ignore_permissions=True)
                    frappe.db.commit()

            # ✅ Always create divisions/groups
            for division_info in divisions:
                division_name = division_info.get("divisionName")
                student_group_name = f"{division_name} ({academic_year_name})"

                # Create batch if not exists
                if not frappe.db.exists("Student Batch Name", {"batch_name": student_group_name}):
                    batch_doc = frappe.new_doc("Student Batch Name")
                    batch_doc.batch_name = student_group_name
                    batch_doc.save(ignore_permissions=True)

                # Skip if student group already exists
                if frappe.db.exists("Student Group", {"student_group_name": student_group_name}):
                    continue

                # Create student group
                student_group_doc = frappe.new_doc("Student Group")
                student_group_doc.student_group_name = student_group_name
                student_group_doc.program = class_name
                student_group_doc.group_based_on = "Batch"
                student_group_doc.academic_year = academic_year_name
                student_group_doc.batch = student_group_name
                student_group_doc.save(ignore_permissions=True)

        # ✅ Final commit and response
        frappe.db.commit()
        return {"status": "success", "message": "Programs and Student Groups created successfully."}

    except Exception as e:
        frappe.log_error(f"Error in create_program_and_groups_with_courses: {str(e)}", "Setup Error")
        return {"status": "failed", "message": f"An error occurred: {str(e)}"}



@frappe.whitelist()
def set_academic_details(academic_year_name, year_start_date, year_end_date, terms, selected_term):
    if "Administrator" not in frappe.get_roles(frappe.session.user):
        frappe.throw("You are not authorized to perform this action.")
    try:
        # Create Academic Year Document
        year_doc = frappe.new_doc("Academic Year")
        year_doc.academic_year_name = academic_year_name
        year_doc.year_start_date = year_start_date
        year_doc.year_end_date = year_end_date
        year_doc.insert(ignore_permissions=True)
        year_doc.save()
        
        # Create Academic Term Documents
        for term in terms:
            term_name = term.get("name")
            term_start_date = term.get("startDate")
            term_end_date = term.get("endDate")
            
            if not term_name or not term_start_date or not term_end_date:
                raise frappe.ValidationError("Missing term details (name, startDate, or endDate).")
            
            term_doc = frappe.new_doc("Academic Term")
            term_doc.academic_year = academic_year_name
            term_doc.term_name = term_name
            term_doc.term_start_date = term_start_date
            term_doc.term_end_date = term_end_date
            term_doc.insert(ignore_permissions=True)
            term_doc.save()
        
        if selected_term:
         # Update Education Settings with the selected term
            formatted_current_term = f"{academic_year_name} ({selected_term})"
            edu_settings = frappe.get_single("Education Settings")
            edu_settings.current_academic_year = academic_year_name
            edu_settings.current_academic_term = formatted_current_term  # Set the selected term
            edu_settings.save(ignore_permissions=True)
        frappe.db.commit()
        
        return {"status": "success", "message": "Academic details set successfully."}
    except Exception as e:
        frappe.log_error(f"Error in setting academic details: {str(e)}", "Set Academic Details Error")
        return {"status": "failed", "message": f"Error in setting academic details: {str(e)}"}

@frappe.whitelist()
def set_institution_details(name, image=None):
    if "Administrator" not in frappe.get_roles(frappe.session.user):
        frappe.throw("You are not authorized to perform this action.")
    """
    Set the institution name and logo in Website Settings.

    :param name: Institution name
    :param image: Base64 encoded image string
    """
    website_doc = frappe.get_doc("Website Settings")
    
    # Ensure the base64 string has proper padding
    # if len(image) % 4 != 0:
    #     image += '=' * (4 - len(image) % 4)
    
    try:
        if image:
            image = image.split(",", 1)[1]
            # Decode the base64 image string
            image_data = base64.b64decode(image)
            
            # Save the image file and link it to the document
            fname = "logo.jpg"  # Adjust the file name as needed
            saved_file = save_file(
                fname=fname,
                dt="Website Settings",  # Doctype
                dn="Website Settings",  # Corrected argument for file name
                content=image_data,
                is_private=0  # Set to 1 if the file should be private
            )
            
            # Link the file to the Website Settings
            website_doc.app_logo = saved_file.file_url
            
        website_doc.app_name = name
        website_doc.save(ignore_permissions=True)
        frappe.db.commit()
    
    except base64.binascii.Error as e:
        frappe.log_error(f"Error decoding image: {str(e)}", "Set Institution Details Error")
        raise frappe.ValidationError("Invalid base64 image data")

import frappe
import random
import string
import re

# @frappe.whitelist()
# def bulk_enroll_students(className, divisionName, students):
#     print(f"Received {len(students)} students")

#     # --- Security check ---
#     if "Administrator" not in frappe.get_roles(frappe.session.user):
#         frappe.throw("You are not authorized to perform this action.")

#     # --- Basic validation ---
#     if not className or not divisionName or not students:
#         frappe.throw("Class, Division, and Students data are required.")

#     # --- Fetch academic context ---
#     edu_settings = frappe.get_single("Education Settings")
#     year = edu_settings.current_academic_year
#     term = edu_settings.current_academic_term

#     # --- Helper to validate student data ---
#     def is_valid_student(s):
#         roll = safe_int(s.get("Roll No"))
#         gr = s.get("GR Number", "").strip()
#         return roll != float("inf") and roll > 0 and gr

#     valid_students = [s for s in students if is_valid_student(s)]
#     invalid_students = [s for s in students if not is_valid_student(s)]
#     for s in invalid_students:
#         print("Skipping invalid row:", s)

#     # --- Sort by Roll No ---
#     valid_students.sort(key=lambda s: safe_int(s.get("Roll No")))

#     try:
#         # --- Enroll each student ---
#         for student in valid_students:
#             full_name = f"{student.get('First Name', '').strip()} {student.get('Middle Name', '').strip()} {student.get('Last Name', '').strip()}".strip()
#             print(f">>> Enrolling student: {full_name} | Roll No: {student.get('Roll No')}")
#             enroll_student(student, className, divisionName, year, term)

#         # --- Commit enrollments ---
#         frappe.db.commit()
#         print("✅ All students enrolled successfully. Now updating Student Group...")

#         # --- Fetch Student Group ---
#         student_group = frappe.get_doc("Student Group", {"program": className, "batch": divisionName})
#         if not student_group:
#             frappe.throw(f"No Student Group found for Program '{className}' and Division '{divisionName}'")

#         # --- Fetch enrolled students from Program Enrollment ---
#         enrolled_students = get_program_enrollment(
#             academic_year=year,
#             academic_term=term,
#             program=className,
#             batch=divisionName,
#         )

#         # --- Prepare existing data ---
#         existing_student_ids = {d.student for d in student_group.students}
#         max_roll_no = max([d.group_roll_number or 0 for d in student_group.students], default=0)

#         # --- Add missing students to Student Group ---
#         added_count = 0
#         for s in enrolled_students:
#             if s.student not in existing_student_ids:
#                 child = student_group.append("students", {})
#                 child.student = s.student
#                 child.student_name = s.student_name
#                 child.active = 1
#                 max_roll_no += 1
#                 child.group_roll_number = max_roll_no
#                 added_count += 1

#         # --- Save and commit group update ---
#         if added_count > 0:
#             student_group.save(ignore_permissions=True)
#             frappe.db.commit()
#             print(f"✅ Added {added_count} new students to Student Group '{student_group.name}'")
#         else:
#             print("ℹ️ All students already present in Student Group.")

#     except Exception as e:
#         frappe.db.rollback()
#         frappe.log_error(frappe.get_traceback(), "Bulk Enroll Failed")
#         frappe.throw(f"Enrollment failed: {str(e)}")

#     return {
#         "status": "success",
#         "message": f"{len(valid_students)} students enrolled successfully and synced to Student Group!"
#     }

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
        for student in valid_students:
            full_name = f"{student.get('First Name', '').strip()} {student.get('Middle Name', '').strip()} {student.get('Last Name', '').strip()}".strip()
            print(f">>> Enrolling student: {full_name} | Roll No: {student.get('Roll No')}")

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

        # --- Save group once at end ---
        if added_count > 0:
            student_group.save(ignore_permissions=True)
            frappe.db.commit()
            print(f"✅ Added {added_count} students to Student Group '{student_group.name}'")
        else:
            frappe.db.commit()
            print("ℹ️ All students already exist in the group.")

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Bulk Enroll Failed")
        frappe.throw(f"Enrollment failed: {str(e)}")

    return {
        "status": "success",
        "message": f"{len(valid_students)} students enrolled and synced with Student Group!"
    }

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


@frappe.whitelist()
def enroll_student(student, className, divisionName, year, term):
    first_name = student["First Name"]
    middle_name = student.get("Middle Name", "")
    last_name = student["Last Name"]
    full_name = " ".join(part for part in [first_name, middle_name, last_name] if part.strip())
    email = student.get("Email Address")

    print(student)
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

    print("Guardian Info:", guardian_info)

    # --- Duplicate Checks ---
    if email and frappe.db.exists("Student", {"student_email_id": email}):
        frappe.throw(_("Duplicate email for: {0}, {1}").format(full_name, email))

    if frappe.db.exists("Student", {"gr_num": student.get("GR Number")}):
        frappe.throw(_("Duplicate GR Number for: {0}, {1}").format(full_name, student.get("GR Number")))

    # --- Generate fallback email ---
    if not email or "@" not in email:
        email = generate_unique_email(first_name, last_name, student.get("GR Number", ""))

    # --- Create User ---
    phone = str(student.get("Phone Number") or generate_unique_phone())
    user = frappe.new_doc("User")
    user.first_name = first_name
    user.middle_name = middle_name
    user.last_name = last_name
    user.email = email
    user.username = f"{first_name.lower()}{student.get('GR Number', '')}".replace(" ", "")
    if not frappe.db.exists("User", {"mobile_no": phone}):
        user.mobile_no = phone
    user.send_welcome_email = 0
    user.enabled = 1
    user.user_type = "Website User"
    user.save(ignore_permissions=True)

    # --- Create Student ---
    student_doc = frappe.new_doc("Student")
    student_doc.first_name = first_name
    student_doc.middle_name = middle_name
    student_doc.last_name = last_name
    student_doc.student_email_id = email
    student_doc.user = email
    student_doc.student_mobile_number = phone
    student_doc.gr_number = student["GR Number"]
    student_doc.save(ignore_permissions=True)

    # --- Create Program Enrollment ---
    program_enrollment = frappe.new_doc("Program Enrollment")
    program_enrollment.student = student_doc.name
    program_enrollment.program = className
    program_enrollment.student_batch_name = divisionName
    program_enrollment.academic_year = year
    program_enrollment.academic_term = term
    program_enrollment.save(ignore_permissions=True)
    program_enrollment.submit()

    # --- Add Guardian ---
    if guardian_info["guardian_name"] and guardian_info["guardian_no"]:
        add_guardian_to_student(
            student_id=student_doc.name,
            student_name=student_doc.student_name,
            guardian_info=guardian_info
        )



@frappe.whitelist()
def enroll_single_student(student_data, className, divisionName):
    print(student_data, className, divisionName)

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
        enroll_student(student_data, className, divisionName, year, term)

        # --- Get the Student doc name after enrollment ---
        student_id = frappe.db.get_value(
            "Student", {"gr_number": student_data.get("GR Number")}, "name"
        )
        if not student_id:
            frappe.throw(f"Could not find enrolled Student with GR Number {student_data.get('GR Number')}")

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
def get_students(
	academic_year,
    group_based_on,
	academic_term=None,
	program=None,
	batch=None,
	student_category=None,
	course=None,
):
	enrolled_students = get_program_enrollment(
		academic_year, academic_term, program, batch, student_category, course
	)

	if enrolled_students:
		student_list = []
		for s in enrolled_students:
			if frappe.db.get_value("Student", s.student, "enabled"):
				s.update({"active": 1})
			else:
				s.update({"active": 0})
			student_list.append(s)
		return student_list
	else:
		frappe.msgprint(_("No students found"))
		return []


def get_program_enrollment(
	academic_year,
	academic_term=None,
	program=None,
	batch=None,
	student_category=None,
	course=None,
):

	condition1 = " "
	condition2 = " "
	if academic_term:
		condition1 += " and pe.academic_term = %(academic_term)s"
	if program:
		condition1 += " and pe.program = %(program)s"
	if batch:
		condition1 += " and pe.student_batch_name = %(batch)s"
	if student_category:
		condition1 += " and pe.student_category = %(student_category)s"
	if course:
		condition1 += " and pe.name = pec.parent and pec.course = %(course)s"
		condition2 = ", `tabProgram Enrollment Course` pec"

	return frappe.db.sql(
		"""
		select
			pe.student, pe.student_name
		from
			`tabProgram Enrollment` pe {condition2}
		where
			pe.academic_year = %(academic_year)s
			and pe.docstatus = 1 {condition1}
		order by
			pe.modified asc
		""".format(
			condition1=condition1, condition2=condition2
		),
		(
			{
				"academic_year": academic_year,
				"academic_term": academic_term,
				"program": program,
				"batch": batch,
				"student_category": student_category,
				"course": course,
			}
		),
		as_dict=1,
	)

import json
import frappe
from frappe import _

@frappe.whitelist()
def bulk_enroll_instructors(teachers):
    print(teachers)
    if not teachers or not isinstance(teachers, list):
        frappe.throw("Invalid input: 'teachers' must be a non-empty list.")

    at_least_one_success = False

    for teacher in teachers:
        full_name = f"{teacher.get('First Name', '').strip()} {teacher.get('Middle Name', '').strip()} {teacher.get('Last Name', '').strip()}".strip()
        first_name = teacher.get("First Name", "") or (full_name.split()[0] if full_name else "")
        gender = teacher.get("Gender", "")
        phone = teacher.get("Mobile", "")
        email = teacher.get("Email", "")
        date_of_birth = teacher.get("Date of Birth", "")
        salutation = "Mr" if gender.lower() == "male" else "Ms"
        password = "#pass4AWAMI"
        role = "Instructor"

        try:
            create_user_and_instructor(
                email=email,
                full_name=full_name,
                first_name=first_name,
                phone=phone,
                password=password,
                role=role,
                gender=gender,
                salutation=salutation,
                date_of_birth=date_of_birth,
                extra_fields=teacher
            )
            at_least_one_success = True
        except Exception as e:
            frappe.throw(f"Failed to enroll {full_name}: {str(e)}")

    frappe.db.commit()

    if not at_least_one_success:
        frappe.throw("No instructor was enrolled successfully.")

    return {"message": "✅ Bulk enrollment completed successfully."}



@frappe.whitelist()
def create_user_and_instructor(email, full_name, first_name, phone, password, role, gender, salutation, date_of_birth, extra_fields=None):
    from frappe import _

    # Check if User exists
    user_doc = None
    if frappe.db.exists("User", {"email": email}):
        user_doc = frappe.get_doc("User", {"email": email})
    elif frappe.db.exists("User", {"mobile_no": phone}):
        user_doc = frappe.get_doc("User", {"mobile_no": phone})
    
    # If user doesn't exist, create one
    if not user_doc:
        user_doc = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "mobile_no": phone,
            "first_name": first_name,
            "new_password": password,
        }).insert(ignore_permissions=True)

    # Add roles if not already assigned
    for r in ["Instructor", "Academics User"]:
        if r not in user_doc.get("roles"):
            user_doc.add_roles(r)

    # Create Employee
    employee_doc = None
    attendance_id = extra_fields.get("Attendance Device ID (Biometric/RF tag ID)") if extra_fields else None

    if attendance_id and frappe.db.exists("Employee", {"attendance_device_id": attendance_id}):
        employee_doc = frappe.get_doc("Employee", {"attendance_device_id": attendance_id})
    else:
        employee_doc = create_employee(email, first_name, phone, gender, salutation, date_of_birth, extra_fields)
        if not employee_doc:
            raise Exception("Employee creation failed")

    # Create Instructor
    instructor_doc = None
    if frappe.db.exists("Instructor", {"instructor_name": full_name}):
        instructor_doc = frappe.get_doc("Instructor", {"instructor_name": full_name})
    else:
        instructor_doc = frappe.get_doc({
            "doctype": "Instructor",
            "instructor_name": full_name,
            "gender": gender,
            "employee": employee_doc.name
        }).insert(ignore_permissions=True)

    # Assign Instructor to Student Group (Division)
    if extra_fields:
        division = extra_fields.get("Division")
        if division:
            try:
                student_group = frappe.get_doc("Student Group", {"student_group_name": division})
                if not any(row.instructor == instructor_doc.name for row in student_group.instructors):
                    student_group.append("instructors", {"instructor": instructor_doc.name})
                    student_group.save(ignore_permissions=True)
            except Exception as e:
                frappe.msgprint(f"⚠️ Could not add instructor to division '{division}': {e}")
        else:
            frappe.msgprint(f"⚠️ Skipping group assignment: No Division for {full_name} ({email})")

    return True



def create_employee(email, first_name, phone, gender, salutation, date_of_birth, extra_fields=None):
    extra_fields = extra_fields or {}

    try:
        dob = frappe.utils.getdate(date_of_birth) if date_of_birth else None
    except Exception as e:
        raise Exception(f"Invalid Date of Birth: {str(e)}")

    doj = frappe.utils.nowdate()
    if extra_fields.get("Date of Joining"):
        try:
            doj = frappe.utils.getdate(extra_fields["Date of Joining"])
        except Exception as e:
            raise Exception(f"Invalid Date of Joining: {str(e)}")

    return frappe.get_doc({
        "doctype": "Employee",
        "first_name": first_name,
        "middle_name": extra_fields.get("Middle Name", ""),
        "last_name": extra_fields.get("Last Name", ""),
        "employee_name": extra_fields.get("Full Name", first_name),
        "salutation": salutation,
        "gender": gender,
        "date_of_birth": dob,
        "date_of_joining": doj,
        "cell_number": phone,
        "status": "Active",
        "user_id": email,
        "bank_name": extra_fields.get("Bank Name", ""),
        "bank_ac_no": extra_fields.get("Bank A/C No.", ""),
        "current_address": extra_fields.get("Current Address", ""),
        "permanent_address": extra_fields.get("Permanent Address", ""),
        "blood_group": extra_fields.get("Blood Group", ""),
        "attendance_device_id": extra_fields.get("Attendance Device ID (Biometric/RF tag ID)", ""),
        "qualification": extra_fields.get("Qualification (Education)", ""),
    }).insert(ignore_permissions=True)

@frappe.whitelist()
def enroll_single_instructor(teacher):
    try:
        full_name = f"{teacher.get('First Name', '').strip()} {teacher.get('Middle Name', '').strip()} {teacher.get('Last Name', '').strip()}".strip()
        first_name = teacher.get("First Name", "") or (full_name.split()[0] if full_name else "")
        gender = teacher.get("Gender", "")
        phone = teacher.get("Mobile", "")
        email = teacher.get("Email", "")
        date_of_birth = teacher.get("Date of Birth", "")
        salutation = "Mr" if gender.lower() == "male" else "Ms"
        password = "#pass4AWAMI"
        role = "Instructor"

        if not email or not phone:
            raise Exception(f"Incomplete data | Email: {email}, Phone: {phone}")

        success = create_user_and_instructor(
            email=email,
            full_name=full_name,
            first_name=first_name,
            phone=phone,
            password=password,
            role=role,
            gender=gender,
            salutation=salutation,
            date_of_birth=date_of_birth,
            extra_fields=teacher
        )

        frappe.db.commit()

        if success:
            frappe.msgprint(f"✅ Instructor enrolled: {first_name} ({email})")
        else:
            frappe.throw(f"❌ Failed to enroll instructor: {first_name} ({email})")

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "enroll_single_instructor failed")
        frappe.throw(f"❌ Error while enrolling instructor: {str(e)}")




# @frappe.whitelist()
# def enroll_student(student, className, divisionName, year, term):
#     if "Name" not in student or not student["Name"]:
#         frappe.throw("Student name is missing.")

#     student_doc = frappe.new_doc("Student")
#     student_doc.first_name = student["Name"]

#     if student.get("GR Number"):
#         student_doc.gr_num = student["GR Number"]

#     student_doc.student_email_id = student.get("Email Address") or generate_unique_email(student["Name"])
#     student_doc.student_mobile_number = student.get("Phone Number") or generate_unique_phone()
#     student_doc.save()

#     program_enrollment = frappe.new_doc("Program Enrollment")
#     program_enrollment.student = student_doc.name
#     program_enrollment.student_name = student_doc.first_name
#     program_enrollment.program = className
#     # program_enrollment.academic_year = year
#     program_enrollment.student_batch_name = divisionName
#     program_enrollment.save()
#     program_enrollment.submit()
#    # frappe.db.commit()

def override_response_cookies():
    from frappe import local
    if "sid" in local.response.cookies:
        local.response.cookies["sid"]["samesite"] = "None"
        local.response.cookies["sid"]["secure"] = True