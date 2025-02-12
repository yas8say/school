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
def get_divisions(values):
    class_name = values.get("classId")  # Extract classId from the values dictionary
    divisions = frappe.get_all("Student Group", filters={"program": class_name})
    return divisions


@frappe.whitelist()
def get_previous_data():
    if "Administrator" not in frappe.get_roles(frappe.session.user):
        frappe.throw("You are not authorized to perform this action.")
    previous_docs = frappe.get_all("Previous Class Structure", fields=["json_data"])
    
    # Print the entire result for debugging
    print(previous_docs)

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
        #result = f"{academic_year_name} ({academic_term_name})"
        
        for class_info in classes:
            class_name = class_info.get("className")
            class_subjects = class_info.get("subjects")  # Subjects specific to the class
            divisions = class_info.get("divisions")
            
            # Skip program and course creation if dontCreateClasses is True
            if not dont_create_classes:
                # Skip program creation if it already exists
                existing_program = frappe.get_all("Program", filters={"program_name": class_name})
                if existing_program:
                    continue
                
                # Create the Program document
                program_doc = frappe.new_doc("Program")
                program_doc.program_name = class_name
                
                if not class_subjects:
                    frappe.log_error(f"No subjects found for class {class_name}. Skipping Program creation.", "Program Creation Error")
                    continue
                
                # Add subjects from the class's subjects list
                for subject in class_subjects:
                    # Create a unique course for each subject and class
                    subject_name = f"{subject} ({class_name})"
                    
                    # Check if the course already exists
                    existing_course = frappe.get_all("Course", filters={"course_name": subject_name})
                    if not existing_course:
                        # Create the Course document
                        course_doc = frappe.new_doc("Course")
                        course_doc.course_name = subject_name
                        course_doc.save(ignore_permissions=True)
                        frappe.db.commit()
                    
                    # Append the course to the Program's child table
                    program_course = program_doc.append("courses", {})
                    program_course.course = subject_name  # Link by the course's name
                    program_course.course_name = subject  # Set the course name
                
                program_doc.save(ignore_permissions=True)
                frappe.db.commit()
            
            # Create Student Groups for each division
            for division_info in divisions:
                division_name = division_info.get("divisionName")
                student_group_name = f"{division_name} ({academic_year_name})"
                
                # Check if the Student Group already exists
                existing_group = frappe.get_all("Student Group", filters={"student_group_name": student_group_name})
                if existing_group:
                    continue
                
                student_group_doc = frappe.new_doc("Student Group")
                student_group_doc.student_group_name = student_group_name
                student_group_doc.program = class_name
                student_group_doc.group_based_on = "Batch"
                student_group_doc.academic_year = academic_year_name
                student_group_doc.save(ignore_permissions=True)
        
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


import random
import string

@frappe.whitelist()
def bulk_enroll_students(className, divisionName, students):
    if "Administrator" not in frappe.get_roles(frappe.session.user):
        frappe.throw("You are not authorized to perform this action.")
        
    if not className or not divisionName or not students:
        frappe.throw("Class, Division, and Students data are required.")
    
    edu_settings = frappe.get_single("Education Settings")
    year = edu_settings.current_academic_year
    term = edu_settings.current_academic_term

    # Sort students based on Roll No (if provided)
    students = sorted(
        students,
        key=lambda s: s.get("Roll No") if isinstance(s.get("Roll No"), int) else float('inf')
    )

    current_roll_no = 1

    for student in students:
        roll_no = student.get("Roll No")

        if roll_no is None or not isinstance(roll_no, int):
            continue

        # Fill in missing roll numbers with filler students
        while current_roll_no < roll_no:
            filler_student = {
                "Name": f"Filler Student {current_roll_no}",
                "Roll No": current_roll_no,
                "Email Address": generate_unique_email(f"Filler Student {current_roll_no}"),
                "Phone Number": generate_unique_phone(),
            }
            try:
                enroll_student(filler_student, className, divisionName, year, term)
                current_roll_no += 1
            except Exception as e:
                print(
                    f"Error enrolling filler student with Roll No {current_roll_no}: {str(e)}",
                    "Filler Enrollment Error"
                )

        # Enroll the current student
        try:
            enroll_student(student, className, divisionName, year, term)
            current_roll_no = roll_no + 1
        except Exception as e:
            print(
                f"Error enrolling student {student['Name']}: {str(e)}",
                "Student Enrollment Error"
            )

    return {"status": "success", "message": "Students enrolled successfully!"}

import re
import random

@frappe.whitelist()
def generate_unique_email(name):
    while True:
        # Convert spaces to dots and ensure no consecutive dots
        email_name = name.strip().replace(' ', '.').lower()
        email_name = re.sub(r'\.+', '.', email_name)  # Replace multiple dots with a single dot
        email_name = email_name.strip('.')  # Remove leading or trailing dots
        
        email = f"{email_name}@codedaddy.io"
        
        if not frappe.db.exists("User", {"email": email}):
            return email
        
        # If email exists, append a random number for uniqueness
        email = f"{email_name}.{random.randint(1000, 9999)}@codedaddy.io"
        email = email.strip('.')  # Ensure no trailing dot before returning
        
        if not frappe.db.exists("User", {"email": email}):
            return email\



def generate_unique_phone():
    while True:
        phone = f"9{''.join(random.choices(string.digits, k=9))}"
        if not frappe.db.exists("User", {"mobile_no": phone}):
            return phone


@frappe.whitelist()
def enroll_student(student, className, divisionName, year, term):
    if "Name" not in student or not student["Name"]:
        frappe.throw("Student name is missing.")

    student_doc = frappe.new_doc("Student")
    student_doc.first_name = student["Name"]
    student_doc.student_email_id = student.get("Email Address") or generate_unique_email(student["Name"])
    student_doc.student_mobile_number = student.get("Phone Number") or generate_unique_phone()
    student_doc.save()

    program_enrollment = frappe.new_doc("Program Enrollment")
    program_enrollment.student = student_doc.name
    program_enrollment.student_name = student_doc.first_name
    program_enrollment.program = className
    # program_enrollment.academic_year = year
    program_enrollment.student_group = divisionName
    program_enrollment.save()
    program_enrollment.submit()
   # frappe.db.commit()
