import json

import frappe
import base64

from frappe import _
from frappe.utils.data import cstr, flt, getdate
from frappe.model.mapper import get_mapped_doc
from datetime import datetime
from frappe.utils.dateutils import get_dates_from_timegrain
from frappe.model.document import Document
from frappe.utils.file_manager import save_file

import frappe


import frappe
import requests

# MSG91 API Credentials
# MSG91_AUTH_KEY = frappe.conf.get("msg91_auth_key")
# MSG91_SENDER_ID = frappe.conf.get("msg91_sender_id")
# MSG91_OTP_TEMPLATE_ID = frappe.conf.get("msg91_otp_template_id")


# @frappe.whitelist(allow_guest=True)
# def send_otp(phone: str):
#     """
#     Sends OTP via MSG91 to the given phone number.
#     """

#     # Check if the user already exists
#     # user_by_email = frappe.db.get("User", {"email": phone})
#     user_by_phone = frappe.db.get("User", {"mobile_no": phone})

#     # if user_by_email and user_by_email.enabled:
#     #     return {"success": False, "message": "User already registered with this email."}
#     if user_by_phone and user_by_phone.enabled:
#         return {"success": False, "message": "User already registered with this phone."}

#     # MSG91 OTP API URL
#     url = "https://control.msg91.com/api/v5/otp"

#     payload = {
#         "authkey": "440500AhNX5vWp2a67a1d344P1",
#         "mobile": phone,
#         "template_id": "67b44535d6fc0513410877e4",
#         "otp_length": 4,
#         "otp_expiry": 1,  # Optional, set the expiry time for the OTP
#         "realTimeResponse": 1  # Optional, to get real-time responses
#     }

#     headers = {"Content-Type": "application/json"}

#     response = requests.post(url, json=payload, headers=headers)
#     data = response.json()

#     if data.get("type") == "success":
#         return {"success": True, "otp_sent": True}
#     else:
#         return {"success": False, "message": data.get("message", "OTP sending failed.")}



# def verify_otp(phone: str, otp: str):
#     """
#     Verifies the OTP using MSG91 API.
#     """
#     url = "https://control.msg91.com/api/v5/otp/verify"

#     payload = {
#         "authkey": "440500AhNX5vWp2a67a1d344P1",
#         "mobile": phone,
#         "otp": otp
#     }

#     headers = {"Content-Type": "application/json"}

#     response = requests.post(url, json=payload, headers=headers)
#     data = response.json()

#     if data.get("type") == "success":
#         return True
#     else:
#         frappe.throw("Incorrect OTP!")

import frappe
import requests
from frappe.auth import LoginManager

MSG91_AUTH_KEY = "440500AhNX5vWp2a67a1d344P1"
MSG91_OTP_TEMPLATE_ID = "67b44535d6fc0513410877e4"

@frappe.whitelist(allow_guest=True)
def send_otp(phone: str):
    """
    Sends OTP via MSG91 to the given phone number if the user exists in Frappe's User doctype.
    """
    # Check if user exists in User doctype with the given phone number
    user_exists = frappe.db.exists("User", {"mobile_no": phone})

    if not user_exists:
        return {"success": False, "message": "Phone number not registered!"}

    # MSG91 OTP API URL
    url = "https://control.msg91.com/api/v5/otp"

    payload = {
        "authkey": MSG91_AUTH_KEY,
        "mobile": phone,
        "template_id": MSG91_OTP_TEMPLATE_ID,
        "otp_length": 4,  # Set OTP length
        "otp_expiry": 1,   # Set OTP expiry time (optional)
        "realTimeResponse": 1  # Get real-time response (optional)
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if data.get("type") == "success":
            return {"success": True, "otp_sent": True}
        else:
            return {"success": False, "message": data.get("message", "OTP sending failed.")}
    
    except requests.exceptions.RequestException as e:
        frappe.log_error(f"MSG91 OTP Sending Error: {str(e)}")
        return {"success": False, "message": "Server Error. Please try again."}

# @frappe.whitelist(allow_guest=True)
# def verify_otp_and_create_session(phone: str, otp: str, role: str):
#     """
#     Verifies OTP using MSG91 API, creates a session, and returns user details.
#     """
#     if not verify_otp(phone, otp):
#         frappe.throw("Incorrect OTP!")

#     user = get_user_name_with_phone(phone)

#     # Set session manually
#     frappe.local.login_manager = LoginManager()
#     frappe.local.login_manager.user = user
#     frappe.session.user = user

#     # Fetch user details and roles
#     return get_user_details(user, role)
from frappe.auth import LoginManager

import frappe

@frappe.whitelist(allow_guest=True)  # Use allow_guest=True if users without login need access
def verify_otp_and_get_api_key(phone: str, otp: str):
    """
    Verifies OTP and returns both API key and API secret for authentication.
    """
    if not verify_otp(phone, otp):
        frappe.throw("Incorrect OTP!")

    user = get_user_name_with_phone(phone)

    # Get user document
    user_doc = frappe.get_doc("User", user)

    # Generate API Key if it doesn't exist
    api_key = user_doc.api_key if user_doc.api_key else frappe.generate_hash(length=15)
    frappe.db.set_value("User", user, "api_key", api_key)

    try:
        api_secret = frappe.utils.password.get_decrypted_password("User", user, "api_secret")
    except frappe.exceptions.AuthenticationError:
        api_secret = frappe.generate_hash(length=30)
        frappe.utils.password.set_encrypted_password("User", user, api_secret, "api_secret")  # FIXED
        frappe.db.commit()

    return {
        "api_key": api_key,
        "api_secret": api_secret
    }



def verify_otp(phone: str, otp: str) -> bool:
    """
    Verifies OTP using MSG91 API.
    """
    url = "https://control.msg91.com/api/v5/otp/verify"

    payload = {
        "authkey": MSG91_AUTH_KEY,
        "mobile": phone,
        "otp": otp
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if data.get("type") == "success":
            return True
        else:
            return False
    
    except requests.exceptions.RequestException as e:
        frappe.log_error(f"MSG91 OTP Verification Error: {str(e)}")
        return False


def get_user_name_with_phone(phone: str):
    """
    Retrieves the user associated with the given phone number.
    """
    user_exists = frappe.db.exists("User", {"mobile_no": phone})

    if not user_exists:
        frappe.throw("Phone number not registered!")

    return frappe.db.get_value("User", {"mobile_no": phone}, "name")

import frappe
import requests

GOOGLE_OAUTH2_URL = "https://oauth2.googleapis.com/tokeninfo"

@frappe.whitelist(allow_guest=True)
def verify_google_token(id_token: str):
    """
    Verifies Google ID token and returns API key & secret if the user exists in Frappe.
    """
    try:
        # Verify the Google ID token
        response = requests.get(f"{GOOGLE_OAUTH2_URL}?id_token={id_token}")
        token_info = response.json()

        if "email" not in token_info:
            return {"success": False, "error": "Invalid token"}

        email = token_info["email"]

        # Check if user exists in Frappe
        if not frappe.db.exists("User", email):
            return {"success": False, "error": "User not found"}

        user_doc = frappe.get_doc("User", email)

        # Generate API Key if it doesn't exist
        api_key = user_doc.api_key if user_doc.api_key else frappe.generate_hash(length=15)
        frappe.db.set_value("User", email, "api_key", api_key)
        frappe.db.commit()

        try:
            api_secret = frappe.utils.password.get_decrypted_password("User", email, "api_secret")
        except frappe.exceptions.AuthenticationError:
            api_secret = frappe.generate_hash(length=30)
            frappe.utils.password.set_encrypted_password("User", email, api_secret, "api_secret")  # FIX HERE
            frappe.db.commit()

        return {
            "api_key": api_key,
            "api_secret": api_secret
        }

    except Exception as e:
        frappe.log_error(f"Google Auth Error: {str(e)}", "Google Login")
        return {"success": False, "error": "Authentication failed"}


# @frappe.whitelist(allow_guest=True)
# def verify_otp_and_login(phone: str, otp: str):
#     """
#     Verifies OTP using MSG91 API and logs in the user if OTP is valid.
#     """
#     if not verify_otp(phone, otp):
#         frappe.throw("Incorrect OTP!")

#     print(login_user_with_phone(phone))

#     return {"success": True, "message": "Logged in successfully!"}


# def verify_otp(phone: str, otp: str) -> bool:
#     """
#     Verifies OTP using MSG91 API.
#     """
#     url = "https://control.msg91.com/api/v5/otp/verify"

#     payload = {
#         "authkey": MSG91_AUTH_KEY,
#         "mobile": phone,
#         "otp": otp
#     }

#     headers = {"Content-Type": "application/json"}

#     try:
#         response = requests.post(url, json=payload, headers=headers)
#         data = response.json()

#         if data.get("type") == "success":
#             return True
#         else:
#             return False
    
#     except requests.exceptions.RequestException as e:
#         frappe.log_error(f"MSG91 OTP Verification Error: {str(e)}")
#         return False


# def login_user_with_phone(phone: str):
#     """
#     Logs in the user with the given phone number by creating a session.
#     """
#     user = get_user_name_with_phone(phone)

#     login_manager = LoginManager()
#     login_manager.login_as(user)


# def get_user_name_with_phone(phone: str):
#     """
#     Retrieves the user associated with the given phone number.
#     """
#     user_exists = frappe.db.exists("User", {"mobile_no": phone})

#     if not user_exists:
#         frappe.throw("Phone number not registered!")

#     user = frappe.db.get_value("User", {"mobile_no": phone}, "name")
#     print(user)
#     return user


  
# def create_user_and_instructor(email, first_name, phone, password, role, addedDivisions):
#     try:
#         # Create User
#         user_doc = frappe.get_doc({
#             "doctype": "User",
#             "email": email,
#             "mobile_no": phone,
#             "first_name": first_name,
#             "new_password": password
#         }).insert(ignore_permissions=True)
#         user_doc.add_roles(role)
#     except Exception as e:
#         frappe.log_error(f"User creation failed: {str(e)}", "create_user_and_instructor")
#         return

#     try:
#         # Create Instructor
#         instructor_doc = frappe.get_doc({
#             "doctype": "Instructor",
#             "instructor_name": first_name
#         }).insert(ignore_permissions=True)
#         instructor_doc.save()
#     except Exception as e:
#         frappe.log_error(f"Instructor creation failed: {str(e)}", "create_user_and_instructor")
#         return

#     try:
#         # Iterate over each division in addedDivisions
#         for division in addedDivisions:
#             # Fetch Student Group
#             student_group_name = frappe.get_value("Student Group", {"student_group_name": division}, "name")
#             if not student_group_name:
#                 frappe.log_error(f"Student Group '{division}' not found", "create_user_and_instructor")
#                 continue  # Skip to the next division if this one is not found

#             # Get the Student Group document
#             group_doc = frappe.get_doc("Student Group", student_group_name)

#             # Append Instructor to the Student Group
#             group_doc.append("instructors", {"instructor": first_name})

#             # Save the updated Student Group
#             group_doc.save(ignore_permissions=True)

#         # Commit all changes to the database
#         frappe.db.commit()

#     except Exception as e:
#         frappe.log_error(f"Error updating Student Group: {str(e)}", "create_user_and_instructor")
#         return



import frappe
from expo_push_notifier.expo_push_notifier.api import send_push_message

def create_user_and_instructor(email, first_name, phone, password, role, addedDivisions):
    try:
        # Create User
        user_doc = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "mobile_no": phone,
            "first_name": first_name,
            "new_password": password
        }).insert(ignore_permissions=True)
        user_doc.add_roles(role)
        user_doc.add_roles("Academics User")
    except Exception as e:
        frappe.log_error(f"User creation failed: {str(e)}", "create_user_and_instructor")
        return

    try:
        # Create Instructor
        instructor_doc = frappe.get_doc({
            "doctype": "Instructor",
            "instructor_name": first_name
        }).insert(ignore_permissions=True)
        instructor_doc.save()
    except Exception as e:
        frappe.log_error(f"Instructor creation failed: {str(e)}", "create_user_and_instructor")
        return

    try:
        # Iterate over each division in addedDivisions
        for division in addedDivisions:
            # Fetch Student Group
            student_group_name = frappe.get_value("Student Group", {"student_group_name": division}, "name")
            if not student_group_name:
                frappe.log_error(f"Student Group '{division}' not found", "create_user_and_instructor")
                continue  # Skip to the next division if this one is not found

            # Get the Student Group document
            group_doc = frappe.get_doc("Student Group", student_group_name)

            # Append Instructor to the Student Group
            group_doc.append("instructors", {"instructor": first_name})

            # Save the updated Student Group
            group_doc.save(ignore_permissions=True)

            # Send notification to Administrator
            send_notification_to_admin(first_name, division)

        # Commit all changes to the database
        frappe.db.commit()

    except Exception as e:
        frappe.log_error(f"Error updating Student Group: {str(e)}", "create_user_and_instructor")
        return

def send_notification_to_admin(instructor_name, division_name):
    """Send push notification to Administrator when an instructor is added to a division."""
    try:
        # Fetch the Administrator's device ID from User Device doctype
        admin_device = frappe.get_all(
            "User Device", filters={"user": "Administrator"}, fields=["device_id"]
        )

        if admin_device:
            device_id = admin_device[0].get("device_id")
            title = "Instructor Assigned"
            message = _(f"A new instructor {instructor_name} has been assigned to {division_name}.")

            if device_id:
                send_push_message(device_id, title, message)
                frappe.log("Push notification sent to Administrator")

    except Exception as e:
        frappe.log_error(f"Error sending notification to Administrator: {str(e)}", "send_notification_to_admin")




    
# def get_user_name_with_phone(email: str):
# 	# find the user to which this phone number belongs to
# 	user_exists = frappe.db.exists("User", {"email": email})

# 	if not user_exists:
# 		frappe.throw("Email address not registered!")

# 	return frappe.db.get_value("User", {"email": email}, "name")

def add_prefix_to_phone(phone_number):
    phone_number = phone_number.strip()  # Remove leading/trailing whitespace
    if not phone_number.startswith("+91"):
        phone_number = "+91" + phone_number
    return phone_number




@frappe.whitelist(allow_guest=True)
def get_divisions(program):
    divisions = frappe.get_all("Student Group", filters={"program": program})
    return divisions

@frappe.whitelist()
def register_device(device_id):
    if frappe.session.user:
        user = frappe.session.user
        # Check if a device ID already exists for the user
        existing_device = frappe.get_all(
            "User Device", filters={"user": user, "device_id": device_id}
        )

        if not existing_device:
            # Create a new User Device record
            doc = frappe.get_doc({
                "doctype": "User Device",
                "user": user,
                "device_id": device_id,
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
        else:
            frappe.log("Device already registered for this user.")
    else:
        return

#school.al_ummah.api.register_device

@frappe.whitelist()
def unregister_device(device_id):
    if frappe.session.user:
        user = frappe.session.user
        # Check if a device ID exists for the user
        existing_device = frappe.get_doc("User Device", {"user": user, "device_id": device_id})
        
        print(existing_device.name)
        if existing_device:
            # Delete the User Device record
            frappe.delete_doc("User Device", existing_device.name, ignore_permissions=True)
            frappe.db.commit()
            return {"status": "success", "message": "Device unregistered successfully."}
        else:
            return {"status": "failed", "message": "Device not found for this user."}
    else:
        return

@frappe.whitelist()
def get_employee_name():
    user_id = frappe.session.user  # Get the logged-in user's ID
    if user_id == "Administrator":
        return None  # Exit if the user is Administrator

    # Fetch the Employee name based on the user_id
    employee = frappe.db.get_value("Employee", {"user_id": user_id}, "name")
    return employee


@frappe.whitelist()
def check_user_with_role():
    user_id = frappe.session.user  # Get the logged-in user's ID
    
    # Check if the user is an Administrator
    if user_id == "Administrator":
        return "Invalid"  # Return "Invalid" if the user is an Administrator, or adjust as needed
    
    roles = frappe.get_roles(user_id)
    
    # Check for valid roles and return specific role name
    if "Instructor" in roles:
        return "Instructor"
    elif "Student" in roles:
        return "Student"
    
    return "Invalid"  # Return "Invalid" if the role is neither Instructor nor Student


@frappe.whitelist()
def hire_employee(source_name):
    """Creates an Employee Record from an Employee Applicant."""
    # Real-time progress (Step 1/2)
    frappe.publish_realtime(
        "convert_to_employee_progress", {"progress": [1, 2]}, user=frappe.session.user
    )

    # Map Employee Applicant to Employee
    employee = get_mapped_doc(
        "Employee Applicant",
        source_name,
        {
            "Employee Applicant": {
                "doctype": "Employee",
                "field_map": {
                    "name": "employee_applicant",  # Special mapping
                },
            }
        },
        ignore_permissions=True,
    )
    employee.save()

    # Real-time progress (Step 2/2)
    frappe.publish_realtime(
        "hire_employee_progress", {"progress": [2, 2]}, user=frappe.session.user
    )

    return employee

@frappe.whitelist()
def get_student_info():
    email = frappe.session.user
    if email == "Administrator":
        return
    student_info = frappe.db.get_list(
        "Student",
        fields=["*"],
        filters={"student_email_id": email},
    )[0]

    current_program = get_current_enrollment(student_info.name)
    if current_program:
        student_groups = get_student_groups(student_info.name, current_program.program)
        student_info["student_groups"] = student_groups
        
        # Check if there is exactly one group in student_groups
        if len(student_groups) == 1:
            # If yes, append the group to student_info
            student_info["student_group"] = student_groups[0]["label"]  # Assuming 'label' is the group name
        
        for group in student_groups:
            print(group)  # Print all student groups for debugging
        
        student_info["current_program"] = current_program

    return student_info


@frappe.whitelist()
def get_guardian_app_data(guardian_id):
    guardian_doc = frappe.get_doc("Guardian", {"email_address": guardian_id})
    print(guardian_doc)

    # Retrieve students linked to this guardian and convert them to dictionaries
    student_list = [student.as_dict() for student in guardian_doc.get("students")]  # Convert to dicts

    # Now you can modify student_list freely
    for student in student_list:
        current_program = get_current_enrollment(student["student"])  # Accessing as dict
        student_groups = get_student_groups(student["student"], current_program.program)

        if not student_groups:
            frappe.throw("Student group not found")

        student_group = student_groups[0]["label"]
        print(student)
        student["student_group"] = student_group  # Add student_group to the dict

    if not student_list:
        frappe.throw(f"No students found for Guardian ID: {guardian_id}")

    profile = guardian_doc.image

    # Convert the profile image to base64 if available
    base64image = convert_image_to_base64(profile) if profile else None
    print(student_list)
    response = {
        "name": guardian_doc.guardian_name,
        "base64profile": base64image,
        "student_list": student_list,
    }
    print(response)
    return response




@frappe.whitelist()
def get_student_app_data(studentID):
    from frappe.utils import today

    response = {}
    # studentID = frappe.session.user

    try:
        # Fetch the student document
        student = frappe.get_doc("Student", {"name": studentID})
        if not student:
            frappe.throw("Student not found")

        # Get the current program and student group
        current_program = get_current_enrollment(student.name)
        student_groups = get_student_groups(student.name, current_program.program)

        if not student_groups:
            frappe.throw("Student group not found")

        student_group = student_groups[0]["label"]
        studentDetails = frappe.get_doc("Student Group Student", {
            "student": student.name,
            "parent": student_group,
            "active": 1
        })

        # Fetch profile image as base64
        profile = student.image
        base64image = None
        if profile:
            base64image = convert_image_to_base64(profile)

        # Fetch notice list
        #notice_data = get_notice_list(student_group)

        # Add basic details to response
        response.update({
            #"notices": notice_data,
            "base64profile": base64image,
            "name": studentDetails.student_name,
            "ID":student.name,
            "group_roll_no": studentDetails.group_roll_number,
            "student_group": student_group,
            "mobile": student.student_mobile_number,
            "address": student.address_line_1,
        })

        # Split student group into class and section
        parts = student_group.split('-')
        if len(parts) == 2:
            response["class"] = parts[0]
            response["section"] = parts[1]

        # Attendance calculation
        date = today()
        StudentAttendance = frappe.qb.DocType("Student Attendance")

        # Fetch today's attendance
        today_attendance = (
            frappe.qb.from_(StudentAttendance)
            .select(StudentAttendance.status)
            .where(
                (StudentAttendance.student == student.name) &
                (StudentAttendance.student_group == student_group) &
                (StudentAttendance.date == date)
            )
        ).run(as_dict=True)
        today_status = today_attendance[0]["status"] if today_attendance else "No Record"
        response["status"] = today_status

        # Fetch all attendance records
        all_attendance = (
            frappe.qb.from_(StudentAttendance)
            .select(StudentAttendance.status)
            .where(
                (StudentAttendance.student == student.name) &
                (StudentAttendance.student_group == student_group)
            )
        ).run(as_dict=True)

        # Initialize counts
        present_count = sum(1 for record in all_attendance if record["status"] == "Present")
        absent_count = sum(1 for record in all_attendance if record["status"] == "Absent")
        leave_count = sum(1 for record in all_attendance if record["status"] == "Leave")

        # Update response with attendance counts
        response.update({
            "present_count": present_count,
            "absent_count": absent_count,
            "leave_count": leave_count,
        })

    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title="Error in get_student_app_data")
        frappe.throw(f"An error occurred: {str(e)}")

    return response


@frappe.whitelist()
def get_user_details(username, role):
    if frappe.session.user:
        roles = frappe.get_roles(username)
        user_details = None
        if "Instructor" in roles and role == "teacher":
            user_details = get_instructor_app_data(username)
            print("hello")
        if "Guardian" in roles and role == "parent":
            user_details = get_guardian_app_data(username)
            print("olleh")
        
        print(user_details)
        return {"roles": roles, "user_details": user_details}
    else:
        return
    
@frappe.whitelist()
def get_instructor_app_data(teacherID):
    """Fetch all required static data in one API call."""
    response = {}
    # user_doc = frappe.get_doc("User", {"email": teacherID})
    emp_doc = frappe.get_doc("Employee", {"user_id": teacherID})
    instructor_doc = frappe.get_doc("Instructor", {"employee": emp_doc.employee})

    student_groups = frappe.db.get_all(
		"Student Group Instructor",
		pluck="parent",
		filters={"instructor": instructor_doc.instructor_name},
	)

    profile = instructor_doc.image

    # Convert the profile image to base64 if available
    base64image = convert_image_to_base64(profile) if profile else None

    # Add teacher info to response
    response = {
        "name": instructor_doc.instructor_name,
        "base64profile": base64image,
        "student_groups": student_groups,
    }
    print(response)
    return response


@frappe.whitelist()
def get_student_attendance_records(based_on, date=None, student_group=None, course_schedule=None):
    if frappe.session.user:
        # Get student group for the logged-in teacher
        # if not student_group:
        #     student_group = get_instructor_group()  # Get the student's group from the teacher's record
        student_list = []

        # THIS CODE IS NOT USED IN APP. Fetch students based on Course Schedule if provided
        if based_on == "Course Schedule":
            student_group = frappe.db.get_value(
                "Course Schedule", course_schedule, "student_group"
            )
            if student_group:
                student_list = frappe.get_all(
                    "Student Group Student",
                    fields=["student", "student_name", "group_roll_number"],
                    filters={"parent": student_group, "active": 1},
                    order_by="group_roll_number",
                )

        if not student_list:
            student_list = frappe.get_all(
                "Student Group Student",
                fields=["student", "student_name", "group_roll_number"],
                filters={"parent": student_group, "active": 1},
                order_by="group_roll_number",
            )

        StudentAttendance = frappe.qb.DocType("Student Attendance")

        # THIS CODE IS NOT USED IN APP. Fetch student attendance if course_schedule is provided
        if course_schedule:
            student_attendance_list = (
                frappe.qb.from_(StudentAttendance)
                .select(StudentAttendance.student, StudentAttendance.status)
                .where((StudentAttendance.course_schedule == course_schedule))
            ).run(as_dict=True)
        else:
            student_attendance_list = (
                frappe.qb.from_(StudentAttendance)
                .select(StudentAttendance.student, StudentAttendance.status)
                .where(
                    (StudentAttendance.student_group == student_group)
                    & (StudentAttendance.date == date)
                    & (
                        (StudentAttendance.course_schedule == "")
                        | (StudentAttendance.course_schedule.isnull())
                    )
                )
            ).run(as_dict=True)
        

        #This part adds todays status to the response
        date = getdate()
        today_attendance_list = (
            frappe.qb.from_(StudentAttendance)
            .select(StudentAttendance.student, StudentAttendance.status)
            .where(
                (StudentAttendance.student_group == student_group)
                & (StudentAttendance.date == date)
                )
            ).run(as_dict=True)
        for student in student_list:
            student_doc = frappe.get_doc("Student", {"name": student.student})
            student.address = student_doc.address_line_1
            student.mobile = student_doc.student_mobile_number
            profile = student_doc.image
            base64image = convert_image_to_base64(profile) if profile else None
            student.base64profile = base64image
            for attendance in today_attendance_list:
                if student.student == attendance.student:
                    student.status = attendance.status



        #This part adds present and absent count to the response
        all_attendance_list = (
            frappe.qb.from_(StudentAttendance)
            .select(StudentAttendance.student, StudentAttendance.status)
            .where(
                (StudentAttendance.student_group == student_group)
            )
        ).run(as_dict=True)
        for student in student_list:
            student.present_count = 0
            student.absent_count = 0
            student.leave_count = 0
            for attendance in all_attendance_list:
                if student.student == attendance.student:
                    if attendance.status == "Present":
                        student.present_count += 1
                    elif attendance.status == "Absent":
                        student.absent_count += 1
                    else: 
                        student.leave_count += 1

        print(student_list)
        # Add student_group to the response structure
        # response = {
        #     "message": student_list  # Add the students below it
        # }
        return student_list
    else:
        return


@frappe.whitelist()
def mark_attendance(
    students_present, students_absent, course_schedule=None, student_group=None, date=None
):
    """Creates Multiple Attendance Records and sends notifications to parents.

    :param students_present: Students Present JSON.
    :param students_absent: Students Absent JSON.
    :param course_schedule: Course Schedule.
    :param student_group: Student Group.
    :param date: Date.
    """
    # print(students_absent)
    # print(students_present)
    date = getdate()
    if student_group:
        academic_year = frappe.db.get_value("Student Group", student_group, "academic_year")
        if academic_year:
            year_start_date, year_end_date = frappe.db.get_value(
                "Academic Year", academic_year, ["year_start_date", "year_end_date"]
            )
            if getdate(date) < getdate(year_start_date) or getdate(date) > getdate(
                year_end_date
            ):
                frappe.throw(
                    _("Attendance cannot be marked outside of Academic Year {0}").format(academic_year)
                )

    present = json.loads(students_present)
    absent = json.loads(students_absent)

    for d in present:
        make_attendance_records(
            d["student"], d["student_name"], "Present", course_schedule, student_group, date
        )

    student_list = []
    for d in absent:
        student_list.append(d["student"])
        make_attendance_records(
            d["student"], d["student_name"], "Absent", course_schedule, student_group, date
        )
    print(student_list)
    frappe.db.commit()
    frappe.msgprint(_("Attendance has been marked successfully."))
    
    # Send push notifications to parents of absent students
    send_notification_to_app(student_list)
    
import frappe
from frappe import _

@frappe.whitelist()
def get_student_guardians(student):
    """Returns List of Guardians of a Student."""
    guardians = frappe.get_all(
        "Student Guardian", 
        fields=["guardian"], 
        filters={"parent": student}
    )
    return guardians
import requests
import frappe

MSG91_AUTH_KEY = "440500AhNX5vWp2a67a1d344P1"
MSG91_TEMPLATE_ID = "67a9cc85d6fc0568b5678ec2"
MSG91_SENDER_ID = "CDTEDU"  # Ensure this is approved in MSG91
MSG91_ROUTE = "4"  # Transactional route

@frappe.whitelist()
def send_notification_to_app(student_list):
    for student in student_list:
        guardians = get_student_guardians(student)
        
        # Get student details
        student_doc = frappe.get_doc("Student", student)
        student_name = student_doc.student_name

        for guardian in guardians:
            guardian_doc = frappe.get_doc("Guardian", guardian.get("guardian"))
            guardian_email = guardian_doc.email_address  # Ensure this field exists
            guardian_phone = guardian_doc.mobile_no  # Ensure this field exists
            
            if guardian_email:
                # Check if a device record exists for the guardian
                existing_device = frappe.get_all(
                    "User Device", filters={"user": guardian_email}, fields=["device_id"]
                )

                if existing_device:
                    device_id = existing_device[0].get("device_id")
                    msg = _(f"Dear Parent, your child {student_name} is marked absent today. Please check the attendance for further details.")
                    title = _("Al-Ummah Girls High School")

                    try:
                        if device_id:
                            # Send push notification to guardian
                            from expo_push_notifier.expo_push_notifier.api import send_push_message
                            send_push_message(device_id, title, msg)
                            print(f"Push notification sent to {guardian_email} ({device_id})")

                        # Send email notification to guardian
                        frappe.sendmail(
                            recipients=[guardian_email],
                            subject="Your child was marked absent",
                            message=msg
                        )
                        print(f"Email sent to {guardian_email}")

                        # Send SMS notification to guardian
                        if guardian_phone:
                            send_sms_via_msg91(guardian_phone, student_name)
                            print(f"SMS sent to {guardian_phone}")

                    except Exception as e:
                        print(f"Error sending notifications to {guardian_email}: {e}")
                        continue  # Continue processing the next guardian

    return {"status": "success", "message": "Notifications sent to guardians of absent students."}

def send_sms_via_msg91(mobile, student_name):
    """
    Sends an SMS via MSG91 API.
    """
    url = "https://control.msg91.com/api/v5/flow/"
    headers = {
        "authkey": MSG91_AUTH_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "flow_id": MSG91_TEMPLATE_ID,  # Use 'flow_id' instead of 'template_id' for MSG91 Flow API
        "sender": MSG91_SENDER_ID,
        "short_url": "1",
        "recipients": [
            {
                "mobiles": mobile,
                "VAR1": student_name  # Matches ##var1## in your MSG91 template
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        if response.status_code == 200 and response_data.get("type") == "success":
            print(f"SMS successfully sent to {mobile}")
        else:
            print(f"Failed to send SMS to {mobile}: {response_data}")
    except Exception as e:
        print(f"Error sending SMS to {mobile}: {e}")

# def send_notification_to_app(student_list):
#     for student in student_list:
#         guardians = get_student_guardians(student)
        
#         # Get student details
#         student_doc = frappe.get_doc("Student", student)
#         student_name = student_doc.student_name

#         for guardian in guardians:
#             guardian_doc = frappe.get_doc("Guardian", guardian.get("guardian"))
#             guardian_email = guardian_doc.email_address  # Ensure this field exists

#             if guardian_email:
#                 # Check if a device record exists for the guardian
#                 existing_device = frappe.get_all(
#                     "User Device", filters={"user": guardian_email}, fields=["device_id"]
#                 )

#                 if existing_device:
#                     device_id = existing_device[0].get("device_id")
#                     msg = _(f"Dear Parent, your child {student_name} is marked absent today. Please check the attendance for further details.")
#                     title = _("Al-Ummah Girls High School")

#                     try:
#                         if device_id:
#                             # Send push notification to guardian
#                             from expo_push_notifier.expo_push_notifier.api import send_push_message
#                             send_push_message(device_id, title, msg)
#                             print(f"Push notification sent to {guardian_email} ({device_id})")

#                         # Send email notification to guardian
#                         frappe.sendmail(
#                             recipients=[guardian_email],
#                             subject="Your child was marked absent",
#                             message=msg
#                         )
#                         print(f"Email sent to {guardian_email}")

#                     except Exception as e:
#                         print(f"Error sending notifications to {guardian_email}: {e}")
#                         continue  # Continue processing the next guardian

#     return {"status": "success", "message": "Notifications sent to guardians of absent students."}



def make_attendance_records(
	student, student_name, status, course_schedule=None, student_group=None, date=None
):
	"""Creates/Update Attendance Record.

	:param student: Student.
	:param student_name: Student Name.
	:param course_schedule: Course Schedule.
	:param status: Status (Present/Absent/Leave).
	"""
	student_attendance = frappe.get_doc(
		{
			"doctype": "Student Attendance",
			"student": student,
			"course_schedule": course_schedule,
			"student_group": student_group,
			"date": date,
		}
	)
	if not student_attendance:
		student_attendance = frappe.new_doc("Student Attendance")
	student_attendance.student = student
	student_attendance.student_name = student_name
	student_attendance.course_schedule = course_schedule
	student_attendance.student_group = student_group
	student_attendance.date = date
	student_attendance.status = status
	student_attendance.save()
	student_attendance.submit()


@frappe.whitelist()
def get_student_group():
    email = frappe.session.user
    if email == "Administrator":
        return
    
    student = frappe.get_doc("Student", {"student_email_id": email})
    current_program = get_current_enrollment(student.name)
    student_groups = get_student_groups(student.name, current_program.program)
    x = []
    x.append(student_groups[0]["label"])
    x.append(convert_image_to_base64(student.image))
    return x

def get_instructor_group():
    teacherID = frappe.session.user
    employee = frappe.get_doc("Employee", {"user_id": teacherID})
    teacher = frappe.get_doc("Instructor", {"employee": employee.name})
    return teacher.student_group

@frappe.whitelist()
# const newLeave = reactive({
#   student: studentInfo.name,
#   student_name: studentInfo.student_name,
#   from_date: '',
#   to_date: '',
#   reason: '',
#   total_days: '',
# })
def apply_leave(leave_data, program_name):
	attendance_based_on_course_schedule = frappe.db.get_single_value(
		"Education Settings", "attendance_based_on_course_schedule"
	)
	if attendance_based_on_course_schedule:
		apply_leave_based_on_course_schedule(leave_data, program_name)
	else:
		apply_leave_based_on_student_group(leave_data, program_name)


def apply_leave_based_on_student_group(leave_data, program_name):
	student_groups = get_student_groups(leave_data.get("student"), program_name)
	leave_dates = get_dates_from_timegrain(
		leave_data.get("from_date"), leave_data.get("to_date")
	)
	for student_group in student_groups:
		for leave_date in leave_dates:
			make_attendance_records(
				leave_data.get("student"),
				leave_data.get("student_name"),
				"Leave",
				None,
				student_group.get("label"),
				leave_date,
			)
               
def get_student_groups(student, program_name):
	# student = 'EDU-STU-2023-00043'

	student_group = frappe.qb.DocType("Student Group")
	student_group_students = frappe.qb.DocType("Student Group Student")

	student_group_query = (
		frappe.qb.from_(student_group)
		.inner_join(student_group_students)
		.on(student_group.name == student_group_students.parent)
		.select((student_group_students.parent).as_("label"))
		.where(student_group_students.student == student)
		.where(student_group.program == program_name)
		.run(as_dict=1)
	)

	return student_group_query



from datetime import datetime

#FRONTEND TEST:
# frappe.call({
#     method: "school.al_ummah.api.submit_leave_application", // The server method you defined
#     type: "POST", // Use POST to send data
#     args: {
#         student: "EDU-STU-2025-00010", // Example argument
#         from_date: "2025-05-01", // Correct format
#         to_date: "2025-05-02", // Correct format
#         student_group: "FIRST-A",
#     },
#     callback: function(response) {
#         if(response.message) {
#             console.log(response.message); // Handle the response here
#         }
#     }
# });

import random
import frappe

# Function to generate unique email for the guardian
def generate_unique_email(name):
    while True:
        email = f"{name.replace(' ', '.').lower()}@codedaddy.io"
        if not frappe.db.exists("User", {"email": email}):
            return email
        # If email exists, append a random number to the name and retry
        email = f"{name.replace(' ', '.').lower()}.{random.randint(1000, 9999)}@codedaddy.io"

@frappe.whitelist(allow_guest=True)
def add_guardian_to_student(student_id, student_name, guardian_name, relation, phone_number):
    try:
        # Check if the guardian already exists based on phone_number
        existing_guardian = frappe.db.get_value("Guardian", {"mobile_number": phone_number}, "name")
        
        if existing_guardian:
            guardian_name = frappe.db.get_value("Guardian", {"name": existing_guardian}, "guardian_name")
        else:
            # Generate a unique email for the guardian
            guardian_email = generate_unique_email(guardian_name)

            # Create the User document
            user_doc = frappe.get_doc({
                "doctype": "User",
                "mobile_no": phone_number,
                "first_name": guardian_name,
                "email": guardian_email  # Use the generated email
            }).insert(ignore_permissions=True)

            # Add the Guardian role to the user
            user_doc.add_roles("Guardian")

            # Create the Guardian document
            guardian_doc = frappe.get_doc({
                "doctype": "Guardian",
                "guardian_name": guardian_name,
                "mobile_number": phone_number,
                "email_address": guardian_email,
            }).insert(ignore_permissions=True, ignore_mandatory=True)

            existing_guardian = guardian_doc.name  # Use newly created Guardian

        # Fetch the student document
        student_doc = frappe.get_doc("Student", student_id)

        # Check if the guardian is already added to the student's child table
        if any(guardian.guardian == existing_guardian for guardian in student_doc.guardians):
            return "Guardian is already linked to the student."

        # Associate the guardian with the student
        student_guardian = student_doc.append("guardians", {})  
        student_guardian.guardian = existing_guardian  
        student_guardian.guardian_name = guardian_name 
        student_guardian.relation = relation

        # Save the student document
        student_doc.save(ignore_permissions=True)
        frappe.db.commit()

        return "Guardian information saved successfully."

    except frappe.exceptions.ValidationError as e:
        frappe.log_error(f"Validation Error: {str(e)}", "Add Guardian")
        return f"Error: {str(e)}"
    except Exception as e:
        frappe.log_error(f"Unexpected Error: {str(e)}", "Add Guardian")
        return f"Error: {str(e)}"



@frappe.whitelist(allow_guest=True)
def submit_leave_application(student, from_date, to_date, student_group, reason, image=None):
    if frappe.session.user:
        # Create a new Leave Application document
        doc = frappe.new_doc("Leave Application")
        doc.student = student
        doc.from_date = from_date
        doc.to_date = to_date
        doc.student_group = student_group
        doc.reason = reason

        # Insert the document to generate a valid `name` for linking
        doc.insert(ignore_permissions=True, ignore_mandatory=True)

        # Attach the image if provided
        if image:
            # Decode the base64 image string
            image_data = base64.b64decode(image)
            fname = "leave_application_image.jpg"  # Adjust the file name as needed

            # Save the image file and link it to the document
            saved_file = save_file(
                fname=fname,           # Corrected argument for file name
                content=image_data,    # File content
                dt="Leave Application", # Doctype
                dn=doc.name,           # Document name
                is_private=0           # Set to 1 if the file should be private
            )
            # Optionally, you can add the file URL to a custom field in the document
            doc.document = saved_file.file_url

        # Save the document after attaching the image
        doc.save()
        frappe.db.commit()  # Ensure the changes are committed to the database

        return {"status": "success", "message": "Leave application submitted successfully", "docname": doc.name}
    else:
        return


# @frappe.whitelist(allow_guest=True)
# def submit_leave_application(student, from_date, to_date, student_group, document_image=None):
#     # Convert from_date and to_date directly as datetime objects without specifying a format
#     # from_date = datetime.strptime(from_date, "%Y-%m-%d")  # Correct format for YYYY-MM-DD
#     # to_date = datetime.strptime(to_date, "%Y-%m-%d")  # Correct format for YYYY-MM-DD

#     # Create a new Leave Application document
#     doc = frappe.new_doc("Leave Application")
#     doc.student = student
#     doc.from_date = from_date
#     doc.to_date = to_date
#     doc.student_group = student_group
#     doc.attendance_based_on = "Student Group"
#     doc.mark_as_present = 1
#     # Insert the new document
#     doc.insert(ignore_permissions=True, ignore_mandatory=True)

#     # Save the document
#     doc.save()
#     doc.submit()
#     frappe.db.commit()  # Ensure data is committed to the database

#     return {"status": "success", "message": "Leave application submitted successfully"}



@frappe.whitelist()
def get_current_enrollment(student, academic_year=None):
	current_academic_year = academic_year or frappe.defaults.get_defaults().academic_year
	if not current_academic_year:
		frappe.throw(_("Please set default Academic Year in Education Settings"))
	program_enrollment_list = frappe.db.sql(
		"""
		select
			name as program_enrollment, student_name, program, student_batch_name as student_batch,
			student_category, academic_term, academic_year
		from
			`tabProgram Enrollment`
		where
			student = %s and academic_year = %s
		order by creation""",
		(student, current_academic_year),
		as_dict=1,
	)

	if program_enrollment_list:
		return program_enrollment_list[0]
	else:
		return None




# @frappe.whitelist()
# def get_student_info():
#     # Get the student group for the logged-in user
#     student_group = get_student_group_by_user_id()

#     # Get the email of the logged-in user
#     email = frappe.session.user

#     if email == "Administrator":
#         return

#     # Fetch the student information
#     student_info = frappe.db.get_list(
#         "Student",
#         fields=["*"],
#         filters={"student_email_id": email},
#     )[0]

#     # Fetch the current enrollment and student groups
#     current_program = get_current_enrollment(student_info["name"])
#     if current_program:
#         student_groups = get_student_groups(student_info["name"], current_program["program"])
#         student_info["student_groups"] = student_groups
#         student_info["current_program"] = current_program

#     # Inject the student group into the response
#     student_info["student_group"] = student_group

#     # Return the complete student information
#     return student_info


# from datetime import datetime

# @frappe.whitelist()
# def get_student_group_by_user_id():
#     # Step 1: Get the current year
#     current_year = str(datetime.now().year)

#     # Step 2: Get the email of the logged-in user
#     user_id = frappe.session.user

#     # Step 3: Fetch the student ID associated with this email
#     student_info = frappe.get_all(
#         "Student",
#         fields=["name"],  # We only need the student ID
#         filters={"student_email_id": user_id}
#     )

#     if student_info:
#         student_id = student_info[0]["name"]

#         # Step 4: Fetch all student groups for the student, filtering by the current year's batch
#         student_group_entries = frappe.get_all(
#             "Student Group Student",
#             fields=["parent"],  # Only fetch the group name (parent)
#             filters={"student": student_id},  # Filter by student ID
#         )

#         # Filter the groups by batch year from the parent (Student Group) records
#         current_year_groups = [
#             entry["parent"]
#             for entry in student_group_entries
#             if frappe.db.get_value("Student Group", entry["parent"], "batch") == current_year
#         ]

#         # Check if there is exactly one record
#         if len(current_year_groups) == 1:
#             group_name = current_year_groups[0]  # Extract the single group name
#             return group_name
#         elif len(current_year_groups) > 1:
#             return {"status": "error", "message": "Multiple groups found for the given user ID in the current year"}
    
#     # Return an error if no group or student is found
#     return {"status": "error", "message": "No group found for the given user ID in the current year"}



#INSTRUCTOR
import frappe
import requests
import base64
from io import BytesIO

@frappe.whitelist()
def get_leave_application(name):
    try:
        # Fetch the Leave Application document based on student group and student
        leave = frappe.get_doc(
            "Leave Application",  # The Doctype
            {   
                "name": name,
                # "student_group": student_group,
                # "mark_as_present": 0,
                # "student": student,
                # "from_date": from_date,
                # "to_date": to_date
            }
        )

        # Extract the required fields
        leave_data = {
            "document": leave.document,
            # "student": leave.student,
            # "student_name": leave.student_name,
            # "from_date": leave.from_date,
            # "to_date": leave.to_date,
            # "total_leave_days": leave.total_leave_days,
            # "reason": leave.reason
        }

        # If the document exists, convert it to base64
        if leave.document:
            leave_data["document_base64"] = convert_image_to_base64(leave.document)

        return leave_data

    except frappe.DoesNotExistError:
        # Handle case where document is not found
        return {"message": "Leave application not found for the specified student and group."}

@frappe.whitelist()
def get_leave_application_list(student_group, student=None):
    if frappe.session.user:
        # If a student is specified, return the leave application for that student
        if student:
            return get_leave_application(student_group, student)
        
        # Fetch all leave applications for the given student group
        leave_list = frappe.get_all(
            "Leave Application",
            fields=["name", "student", "student_name", "from_date", "to_date", "total_leave_days", "reason", "document"],
            filters={"student_group": student_group, "mark_as_present": 0}
        )
        
        # Convert image URLs to base64
        for leave in leave_list:
            if leave.get("document"):
                image_url = leave["document"]
                leave["document_base64"] = convert_image_to_base64(image_url)
        print(leave_list)
        return leave_list
    else:
        return





# def convert_image_to_base64(image_url):
#     # Check if the URL is relative (doesn't contain a scheme like http:// or https://)
#     if not image_url.startswith('http'):
#         #base_url = 'http://edu.school:8000'
#         base_url = frappe.utils.get_url()
#         print(base_url)
#         image_url = base_url + image_url
    
#     # Now perform the request
#     response = requests.get(image_url)
    
#     if response.status_code == 200:
#         image_bytes = BytesIO(response.content)
#         base64_image = base64.b64encode(image_bytes.read()).decode('utf-8')
#         return base64_image
#     else:
#         return None

import os
import base64
import requests
from io import BytesIO
import frappe

def convert_image_to_base64(image_url):
    # Get the Frappe base URL, but override if it's incorrect
    base_url = frappe.utils.get_url()
    
    # Override for local development
    if "ngrok" in base_url or "localhost" in base_url:
        base_url = "http://edu.school:8000"  # Use your actual local URL
    
    print(f"Using base URL: {base_url}")

    if not image_url.startswith('http'):
        image_url = base_url + image_url

    response = requests.get(image_url)

    if response.status_code == 200:
        image_bytes = BytesIO(response.content)
        return base64.b64encode(image_bytes.read()).decode('utf-8')

    return None



#student_group, student, from_date, to_date, status
@frappe.whitelist()
def update_leave_status(name, status):
    if frappe.session.user:
        try:
            # Get the leave application document for the given student and group
            leave = frappe.get_doc(
                "Leave Application",  # The Doctype
                {
                    "name": name,
                    # "student_group": student_group,
                    # "student": student,
                    # "from_date": from_date,
                    # "to_date": to_date
                }
            )

            if not leave:
                # Handle case where the document does not exist
                return {"message": "Leave application not found for the specified student and group."}

            # If status is approved, mark the student as present
            if status == "approved":
                leave.mark_as_present = 1
            elif status == "rejected":
                print(leave)
                leave.delete()
                frappe.db.commit()
                print(leave)
            # Save the changes and commit them to the database
            leave.save()
            leave.submit()
            frappe.db.commit()
            
            # Return success message
            return {"message": "Leave status updated successfully."}

        except Exception as e:
            # Catch any other exceptions and return the error message
            return {"message": f"An error occurred: {str(e)}"}
    else:
        return

@frappe.whitelist(allow_guest=True)
def submit_notice(notice_heading, notice_message, student_group):
    print(student_group)
    if frappe.session.user:
        print(notice_heading, notice_message, student_group)
        student_list = frappe.get_all(
            "Student Group Student",
            fields=["student", "student_name", "group_roll_number"],
            filters={"parent": student_group, "active": 1},
            order_by="group_roll_number",
        )
        send_notice_notification_to_app(student_list, notice_heading, notice_message)
        try:
            if not notice_heading or not notice_message:
                return {"status": "error", "message": "Both title and message are required."}

            # Create a new Leave Application document
            teacherID = frappe.session.user
            employee = frappe.get_doc("Employee", {"user_id": teacherID})
            teacher = frappe.get_doc("Instructor", {"employee": employee.name})
            doc = frappe.new_doc("Student Notice")
            doc.notice_heading = notice_heading
            doc.notice_message = notice_message
            doc.date = getdate()
            doc.instructor = teacher.instructor_name
            doc.student_group = student_group

            # Insert the document to generate a valid `name` for linking
            doc.insert(ignore_permissions=True)
            # Save the document after attaching the image
            doc.save()
            frappe.db.commit()  # Ensure the changes are committed to the database

            # Ensure the message is a string
            return {"status": "success", "message": str("Notice created successfully")}
        except Exception as e:
            # Return the error message as a string
            return {"status": "error", "message": str(e)}
    else:
        return
    
import frappe
from frappe import _

# @frappe.whitelist()
# def get_student_guardians(student):
#     """Returns List of Guardians of a Student."""
#     guardians = frappe.get_all(
#         "Student Guardian", 
#         fields=["guardian"], 
#         filters={"parent": student}
#     )
#     return guardians
"""for guardian in guardians:
    guardian_doc = frappe.get_doc("Guardian", guardian.get("guardian"))
    guardian_email = guardian_doc.email_address  # Ensure this field exists

    if guardian_email:
        # Check if a device record exists for the guardian (using guardian_email)
        existing_devices = frappe.get_all(
            "User Device", filters={"user": guardian_email}, fields=["device_id"], order_by="modified desc", limit_page_length=1
        )

        if existing_devices:
            device_id = existing_devices[0].get("device_id")  # Get the most recent device ID
            msg = _(f"Dear Parent, a new notice titled '{notice_heading}' has been posted for your child {student_name}. {notice_message}")
            title = _(f"Notice: {notice_heading}")  # Use the heading as the title

            try:
                if device_id:
                    # Send push notification to the most recent device
                    from expo_push_notifier.expo_push_notifier.api import send_push_message
                    send_push_message(device_id, title, msg)
                    print(f"Push notification sent to {guardian_email} ({device_id})")

                # Send email notification to the guardian
                frappe.sendmail(
                    recipients=[guardian_email],
                    subject=f"Notice: {notice_heading}",
                    message=msg
                )
                print(f"Email sent to {guardian_email}")

            except Exception as e:
                print(f"Error sending notifications to {guardian_email}: {e}")
                continue  # Continue processing the next guardian
"""
def send_notice_notification_to_app(student_list, notice_heading, notice_message):
    for student in student_list:
        # Query the student record using the 'student' identifier
        student_doc = frappe.get_doc("Student", student["student"])
        student_name = student_doc.student_name

        guardians = get_student_guardians(student["student"])

        for guardian in guardians:
            guardian_doc = frappe.get_doc("Guardian", guardian.get("guardian"))
            guardian_email = guardian_doc.email_address  # Ensure this field exists

            if guardian_email:
                # Check if a device record exists for the guardian (using guardian_email)
                existing_device = frappe.get_all(
                    "User Device", filters={"user": guardian_email}, fields=["device_id"]
                )

                if existing_device:
                    device_id = existing_device[0].get("device_id")
                    msg = _(f"Dear Parent, a new notice titled '{notice_heading}' has been posted for your child {student_name}. {notice_message}")
                    title = _(f"Notice: {notice_heading}")  # Use the heading as the title

                    try:
                        if device_id:
                            # Send push notification to the guardian
                            from expo_push_notifier.expo_push_notifier.api import send_push_message
                            send_push_message(device_id, title, msg)
                            print(f"Push notification sent to {guardian_email} ({device_id})")

                        # Send email notification to the guardian
                        frappe.sendmail(
                            recipients=[guardian_email],
                            subject=f"Notice: {notice_heading}",
                            message=msg
                        )
                        print(f"Email sent to {guardian_email}")

                    except Exception as e:
                        print(f"Error sending notifications to {guardian_email}: {e}")
                        continue  # Continue processing the next guardian

    return {"status": "success", "message": "Push notifications and emails sent for the notice."}



@frappe.whitelist()
def get_notice_list(student_group):
    if frappe.session.user:
        # Fetch all leave applications for the given student group
        notice_list = frappe.get_all(
            "Student Notice",
            fields=["name", "notice_heading", "notice_message", "date"],
            filters={"student_group": student_group}
        )
        print(notice_list)
        return notice_list
    else:
        return

@frappe.whitelist()
def delete_notice(name):
    if frappe.session.user:
        # Fetch all leave applications for the given student group
        notice = frappe.get_doc(
            "Student Notice",
            {"name": name}
        )
        notice.delete()
        frappe.db.commit()
    else:
        return
    

