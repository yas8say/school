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

import requests

import base64
from frappe.utils.file_manager import save_file


from frappe.auth import LoginManager

@frappe.whitelist(allow_guest=True)
def login(usr, pwd, role=None):
    """
    Custom login API with role validation
    """
    print("=== login API called ===")
    print(f"Received usr: {usr}, role: {role}")

    try:
        # Resolve user from mobile or email
        user = frappe.db.get_value("User", {"mobile_no": usr}, "name") \
               or frappe.db.get_value("User", {"email": usr}, "name")
        
        if not user:
            frappe.throw("User not found", frappe.AuthenticationError)

        print("Resolved user:", user)

        # Authenticate using LoginManager
        login_manager = LoginManager()
        login_manager.authenticate(user=user, pwd=pwd)  # Raises AuthenticationError if invalid
        
        # Get user roles
        user_roles = frappe.get_roles(user)
        print("User roles:", user_roles)

        # Validate role if provided
        if role:
            required_role = "Guardian" if role == "Guardian" else "Instructor"
            if required_role not in user_roles:
                frappe.throw(
                    f"User does not have {required_role} role. User has roles: {', '.join(user_roles)}",
                    frappe.PermissionError
                )

        # Create session
        login_manager.post_login()

        print("✅ Login successful:", frappe.session.user)
        return {
            "status": "success",
            "user": user,
            "roles": user_roles,
            "sid": frappe.session.sid,
            "message": "Logged In"
        }

    except frappe.AuthenticationError:
        frappe.throw("Invalid credentials", frappe.AuthenticationError)

    except Exception as e:
        frappe.throw(f"Unexpected error: {str(e)}", frappe.ValidationError)

@frappe.whitelist(allow_guest=True)
def admin_login(usr, pwd):
    """
    Custom login API with role validation for Admin portal
    """
    print("=== Admin Login API called ===")
    print(f"Received username: {usr}")

    try:
        # Authenticate using LoginManager
        login_manager = LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        
        # Get user roles
        user_roles = frappe.get_roles(usr)
        print("User roles:", user_roles)

        # Check if user has Administrator role
        if "Administrator" not in user_roles:
            frappe.throw(
                f"Access denied. Administrator role required. Your roles: {', '.join(user_roles)}",
                frappe.PermissionError
            )

        # Create session
        login_manager.post_login()

        print("✅ Admin login successful:", frappe.session.user)
        
        # Return user data including roles
        return {
            "status": "success",
            "user": usr,
            "roles": user_roles,
            "sid": frappe.session.sid,
            "message": "Admin login successful",
            "default_route": "/quick-setup"
        }

    except frappe.AuthenticationError:
        frappe.throw("Invalid username or password", frappe.AuthenticationError)

    except frappe.PermissionError as e:
        frappe.throw(str(e), frappe.PermissionError)

    except Exception as e:
        print(f"Unexpected error in admin_login: {str(e)}")
        frappe.throw("Login failed. Please try again.", frappe.ValidationError)

import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_user_roles():
    """Get the current user's roles"""
    try:
        if frappe.session.user == "Guest":
            frappe.throw(_("Not logged in"))
        
        user_roles = frappe.get_roles(frappe.session.user)
        # Return just the array of roles directly
        return user_roles
        
    except Exception as e:
        frappe.log_error(f"Error getting user roles: {str(e)}")
        # Return empty array on error
        return []

def send_push_message(token, title, body, extra=None):
    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate",
        "content-type": "application/json",
    }

    data = {
        "to": token,                  # ExponentPushToken[...] format
        "title": title,
        "body": body,
    }

    if extra:
        data["data"] = extra  # Optional extra payload

    try:
        response = requests.post("https://exp.host/--/api/v2/push/send", headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print("Push notification sent successfully!")
        print(response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending push notification: {e}")
        return None


@frappe.whitelist(allow_guest=True)
def send_otp_signup(phone: str, email: str = None, token: str = None, role: str = None):
    """
    Sends OTP via MSG91 to the given phone number if:
    - user does not exist,
    - provided token matches the Instructor Token,
    - and role is 'Teacher'.
    """

    # 0. Validate role first
    if role != "teacher":
        return {"success": False, "message": "Only teachers are allowed to signup."}

    # 1. Check if phone or email already registered
    if frappe.db.exists("User", {"mobile_no": phone}):
        return {"success": False, "message": "Phone number already registered!"}
    if email and frappe.db.exists("User", {"email": email}):
        return {"success": False, "message": "Email already registered!"}

    # 2. Check if token matches
    if not token:
        return {"success": False, "message": "Token is required."}

    token_doc = frappe.get_single("Instructor Token")
    if token_doc.token != token:
        return {"success": False, "message": "Invalid token provided."}

    # 3. Send OTP via MSG91
    url = "https://control.msg91.com/api/v5/otp"

    payload = {
        "authkey": MSG91_AUTH_KEY,
        "mobile": f"91{phone}",
        "template_id": MSG91_OTP_TEMPLATE_ID,
        "otp_length": 6,
        "otp_expiry": 1,
        "realTimeResponse": 1
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
# def verify_otp_and_create_user(phone: str, otp: str, email: str, fullName: str, password: str, role: str, addedDivisions: list, gender: str, salutation: str, date_of_birth: str):
#     """
#     Verifies OTP. If successful, creates a new User, Employee, and Instructor.
#     """
#     try:
#         # 1. Verify OTP
#         if not verify_otp(phone, otp):
#             return {"success": False, "message": "Invalid OTP. Please try again."}

#         # 2. Create User, Employee, and Instructor
#         create_user_and_instructor(email, fullName, phone, password, role, addedDivisions, gender, salutation, date_of_birth)

#         return {"success": True, "message": "User, Employee, and Instructor created successfully!"}

#     except Exception as e:
#         frappe.log_error(f"OTP Verification or User Creation Failed: {str(e)}")
#         return {"success": False, "message": "Server error. Please contact support."}


@frappe.whitelist(allow_guest=True)
def verify_otp_and_create_user(phone: str, otp: str, email: str, fullName: str, password: str, role: str, gender=None, salutation=None, dateOfBirth=None):
    """
    Verifies OTP. If successful, creates a new User, Employee, and Instructor.
    """
    print(dateOfBirth)
    try:
        # Step 1: Verify OTP
        if not verify_otp(phone, otp):
            return {"success": False, "message": "Invalid OTP. Please try again."}

        # Step 2: Create User, Employee, and Instructor
        create_user_and_instructor(email, fullName, phone, password, role, gender, salutation, dateOfBirth)

        return {"success": True, "message": "User, Employee, and Instructor created successfully!"}

    except Exception as e:
        frappe.log_error(f"OTP Verification or User Creation Failed: {str(e)}")
        return {"success": False, "message": "Server error. Please contact support."}

def create_employee(email, first_name, phone, gender, salutation, dateOfBirth):
    print(first_name)
    try:
        employee_doc = frappe.get_doc({
            "doctype": "Employee",
            "first_name": first_name,
            "salutation": salutation,
            "gender": gender,
            "date_of_birth": dateOfBirth,
            "cell_number": phone,
            "status": "Active",
            "user_id": email
        }).insert(ignore_permissions=True)

        return employee_doc

    except Exception as e:
        frappe.log_error(f"Employee creation failed: {str(e)}", "create_employee")
        return None

        
def create_user_and_instructor(email, first_name, phone, password, role, gender, salutation, date_of_birth):
    print(email, first_name, phone, password, role, gender, salutation, date_of_birth)
    try:
        # Step 1: Check if user already exists
        if frappe.db.exists("User", {"email": email}):
            frappe.throw(_("User with this email already exists."))

        if frappe.db.exists("User", {"mobile_no": phone}):
            frappe.throw(_("User with this phone number already exists."))

        # Step 2: Create User
        user_doc = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "mobile_no": phone,
            "first_name": first_name,
            "new_password": password,
        }).insert(ignore_permissions=True)

        # Assign roles to user
        user_doc.add_roles("Instructor")
        user_doc.add_roles("Academics User")

        # Step 3: Create Employee
        employee_doc = create_employee(email, first_name, phone, gender, salutation, date_of_birth)
        if not employee_doc:
            frappe.throw(_("Employee creation failed."))

        # Step 4: Link Employee to User
        employee_doc.save(ignore_permissions=True)

    except Exception as e:
        frappe.log_error(f"User/Employee creation failed: {str(e)}", "create_user_and_instructor")
        return

    try:
        # Step 5: Create Instructor and link to User and Employee
        instructor_doc = frappe.get_doc({
            "doctype": "Instructor",
            "instructor_name": first_name,
            "user": email,
            "employee": employee_doc.employee  # Use the employee field here
        }).insert(ignore_permissions=True)

        instructor_doc.save(ignore_permissions=True)

        # Send notification to admin
        send_notification_to_admin(first_name)

    except Exception as e:
        frappe.log_error(f"Instructor creation failed: {str(e)}", "create_user_and_instructor")
        return

@frappe.whitelist()
def get_student_details(student):
    """
    Returns Student details along with a list of their Guardians, including contact info
    and additional details like Email, Occupation, Designation, Work Address, Education, and DOB.
    """
    # 1️⃣ Fetch Student document
    student_doc = frappe.get_doc("Student", student)
    
    student_info = {
        "student": student_doc.name,
        "first_name": student_doc.first_name,
        "middle_name": getattr(student_doc, "middle_name", None),
        "last_name": student_doc.last_name,
        "student_date_of_birth": getattr(student_doc, "date_of_birth", getattr(student_doc, "student_date_of_birth", None)),
        "name": getattr(student_doc, "name", None),
        "email_address": getattr(student_doc, "student_email_id", None),
        "phone_number": getattr(student_doc, "student_mobile_number", None),
        "roll_number": getattr(student_doc, "roll_number", None)
    }

    # 2️⃣ Fetch all linked Guardians
    guardians = frappe.get_all(
        "Student Guardian", 
        fields=["guardian_name", "guardian", "relation"], 
        filters={"parent": student}
    )
    
    guardian_list = []
    for guardian in guardians:
        guardian_doc = frappe.get_doc("Guardian", guardian.get("guardian"))

        guardian_info = {
            "guardian": guardian.get("guardian"),  # Guardian ID
            "guardian_name": guardian.get("guardian_name"),
            "relation": guardian.get("relation"),
            "mobile_number": getattr(guardian_doc, "mobile_number", None),
            "email": getattr(guardian_doc, "email_address", None),
            "occupation": getattr(guardian_doc, "occupation", None),
            "designation": getattr(guardian_doc, "designation", None),
            "work_address": getattr(guardian_doc, "work_address", None),
            "education": getattr(guardian_doc, "education", None),
            "date_of_birth": getattr(guardian_doc, "date_of_birth", None)
        }

        guardian_list.append(guardian_info)
    
    # 3️⃣ Return combined response
    return {
        "student_info": student_info,
        "guardians": guardian_list
    }

@frappe.whitelist()
def update_student_details(
    student_id,
    first_name=None,
    middle_name=None,
    last_name=None,
    student_date_of_birth=None,
    name=None,
    email_address=None,
    phone_number=None,
    roll_number=None,
    student_group=None
):
    """
    Updates Student details, linked User, and linked Customer (via Student.customer).
    Also sets student_name = first + middle + last.
    Updates student's name and roll number inside the given Student Group (without re-adding).
    """
    try:
        if not student_id:
            return {"success": False, "message": "Student ID is required."}

        # 1️⃣ Fetch Student document
        student_doc = frappe.get_doc("Student", student_id)
        if not student_doc:
            return {"success": False, "message": "Student not found."}

        user_id = student_doc.user
        print(f"🧾 Student: {student_doc.name}")
        print(f"👤 Linked User: {user_id}")
        print(f"🏷️ Linked Customer: {student_doc.customer}")

        # 2️⃣ Update linked User first
        if user_id and frappe.db.exists("User", user_id):
            user_doc = frappe.get_doc("User", user_id)

            if first_name:
                user_doc.first_name = first_name
            if last_name:
                user_doc.last_name = last_name
            if email_address:
                user_doc.email = email_address
            if phone_number:
                if not phone_number.isdigit() or len(phone_number) != 10:
                    return {"success": False, "message": "Invalid phone number. Must be 10 digits."}
                user_doc.mobile_no = phone_number
            if student_date_of_birth:
                user_doc.birth_date = student_date_of_birth

            user_doc.flags.ignore_mandatory = True
            user_doc.flags.ignore_validate = True
            user_doc.flags.ignore_permissions = True
            user_doc.save(ignore_permissions=True)
            frappe.db.commit()
            print("✅ Linked User updated")

        # 3️⃣ Update Student document
        updated = False
        if first_name:
            student_doc.first_name = first_name
            updated = True
        if middle_name:
            student_doc.middle_name = middle_name
            updated = True
        if last_name:
            student_doc.last_name = last_name
            updated = True
        if student_date_of_birth:
            if hasattr(student_doc, "date_of_birth"):
                student_doc.date_of_birth = student_date_of_birth
            else:
                student_doc.student_date_of_birth = student_date_of_birth
            updated = True
        if name:
            student_doc.name = name
            updated = True
        if email_address:
            student_doc.student_email_id = email_address
            updated = True
        if phone_number:
            student_doc.student_mobile_number = phone_number
            updated = True
        if roll_number:
            student_doc.roll_number = roll_number
            updated = True

        # 4️⃣ Set full student_name
        full_name_parts = [first_name, middle_name, last_name]
        student_doc.student_name = " ".join([p for p in full_name_parts if p])
        updated = True
        print(f"🧩 student_name set to: {student_doc.student_name}")

        if updated:
            # Prevent permission errors from Customer hooks
            if hasattr(student_doc, "set_missing_customer_details"):
                student_doc.set_missing_customer_details = lambda *a, **kw: None

            student_doc.flags.ignore_permissions = True
            student_doc.flags.ignore_mandatory = True
            student_doc.flags.ignore_validate = True
            student_doc.save(ignore_permissions=True)
            frappe.db.commit()
            print("✅ Student updated in DB")

        # 5️⃣ Update inside the given Student Group
        if student_group:
            if not frappe.db.exists("Student Group", student_group):
                return {"success": False, "message": f"Student Group '{student_group}' not found."}

            group_doc = frappe.get_doc("Student Group", student_group)
            found = False

            for row in group_doc.students:
                if row.student == student_doc.name:
                    row.student_name = student_doc.student_name
                    if roll_number:
                        row.group_roll_number = roll_number
                    found = True
                    break

            if found:
                group_doc.flags.ignore_permissions = True
                group_doc.save(ignore_permissions=True)
                frappe.db.commit()
                print(f"✅ Updated student in group: {student_group}")
            else:
                print(f"⚠️ Student not found in group: {student_group}")

        # 6️⃣ Update linked Customer name (via Student.customer)
        if student_doc.customer and frappe.db.exists("Customer", student_doc.customer):
            customer_doc = frappe.get_doc("Customer", student_doc.customer)
            customer_doc.customer_name = student_doc.student_name
            customer_doc.flags.ignore_permissions = True
            customer_doc.save(ignore_permissions=True)
            frappe.db.commit()
            print(f"✅ Customer '{customer_doc.name}' updated with new name: {student_doc.student_name}")
        else:
            print("ℹ️ No linked Customer found for this Student")

        # Reload for confirmation
        student_doc.reload()

        return {
            "success": True,
            "message": "Student, linked User, Customer, and Student Group updated successfully.",
            "student": student_doc.name,
            "user": user_id or "N/A",
            "student_name": student_doc.student_name,
            "student_group": student_group,
        }

    except Exception as e:
        frappe.log_error(f"Unexpected Error: {str(e)}", "Update Student Details")
        return {"success": False, "message": f"Error: {str(e)}"}


import frappe

@frappe.whitelist()
def update_guardian_details(
    guardian_id,
    guardian_name=None,
    phone_number=None,
    relation=None,
    guardian_date_of_birth=None,
    guardian_email=None,
    occupation=None,
    designation=None,
    work_address=None,
    education=None
):
    """
    Updates Guardian details and first updates the linked User record.
    """
    try:
        if not guardian_id:
            return {"success": False, "message": "Guardian ID is required."}

        # 1️⃣ Fetch Guardian document
        guardian_doc = frappe.get_doc("Guardian", guardian_id)
        if not guardian_doc:
            return {"success": False, "message": "Guardian not found."}

        user_id = guardian_doc.user
        user_doc = None

        # 2️⃣ Fetch linked User and update first
        if user_id and frappe.db.exists("User", user_id):
            user_doc = frappe.get_doc("User", user_id)

            if guardian_name:
                user_doc.first_name = guardian_name
                user_doc.full_name = guardian_name
            if phone_number:
                if not phone_number.isdigit() or len(phone_number) != 10:
                    return {"success": False, "message": "Invalid phone number. Must be 10 digits."}
                user_doc.mobile_no = phone_number
            if guardian_email:
                user_doc.email = guardian_email
            if guardian_date_of_birth:
                user_doc.birth_date = guardian_date_of_birth

            # Save user forcibly bypassing validation
            user_doc.flags.ignore_mandatory = True
            user_doc.flags.ignore_validate = True
            user_doc.flags.ignore_permissions = True
            user_doc.save(ignore_permissions=True)

        # 3️⃣ Update Guardian after User
        if guardian_name:
            guardian_doc.guardian_name = guardian_name
        if phone_number:
            guardian_doc.mobile_number = phone_number
        if relation:
            guardian_doc.relation = relation
        if guardian_date_of_birth:
            guardian_doc.date_of_birth = guardian_date_of_birth
        if guardian_email:
            guardian_doc.email_address = guardian_email
        if occupation:
            guardian_doc.occupation = occupation
        if designation:
            guardian_doc.designation = designation
        if work_address:
            guardian_doc.work_address = work_address
        if education:
            guardian_doc.education = education

        guardian_doc.save(ignore_permissions=True)

        # 4️⃣ Final commit
        frappe.db.commit()

        return {
            "success": True,
            "message": "Guardian and linked User details updated successfully.",
            "guardian": guardian_doc.name,
            "user": user_id or "N/A"
        }

    except frappe.DoesNotExistError:
        frappe.log_error(f"Guardian {guardian_id} not found.", "Update Guardian Details")
        return {"success": False, "message": "Guardian not found."}

    except Exception as e:
        frappe.log_error(f"Unexpected Error: {str(e)}", "Update Guardian Details")
        return {"success": False, "message": f"Error: {str(e)}"}



@frappe.whitelist(allow_guest=True)
def update_guardian_phone(guardian_id, phone_number):
    try:
        if not guardian_id or not phone_number:
            return "Guardian ID and phone number are required."

        # Validate phone number format
        if not phone_number.isdigit() or len(phone_number) != 10:
            return "Invalid phone number. Must be 10 digits."

        # Fetch guardian document
        guardian_doc = frappe.get_doc("Guardian", guardian_id)
        if not guardian_doc:
            return "Guardian not found."

        # Update guardian's mobile number
        guardian_doc.mobile_number = phone_number
        guardian_doc.save(ignore_permissions=True)

        # Fetch user document using guardian's email address
        if guardian_doc.email_address:
            user_doc = frappe.get_doc("User", guardian_doc.email_address)
            if user_doc:
                user_doc.mobile_no = phone_number
                user_doc.save(ignore_permissions=True)

        frappe.db.commit()
        return "Phone number updated successfully in both Guardian and User records."

    except frappe.DoesNotExistError:
        frappe.log_error(f"Guardian {guardian_id} does not exist.", "Update Guardian Phone")
        return "Guardian not found."
    except Exception as e:
        frappe.log_error(f"Unexpected Error: {str(e)}", "Update Guardian Phone")
        return f"Error: {str(e)}"



@frappe.whitelist()
def get_student_guardian_names(student):
    """Returns List of Guardians of a Student with relation, contact, and additional details."""
    # Fetch all guardians linked to the student
    guardians = frappe.get_all(
        "Student Guardian", 
        fields=["guardian_name", "guardian", "relation"], 
        filters={"parent": student}
    )
    
    guardian_list = []
    for guardian in guardians:
        guardian_doc = frappe.get_doc("Guardian", guardian.get("guardian"))
        print(guardian_doc.email_address)
        guardian_info = {
            "guardian": guardian.get("guardian"),  # Guardian ID
            "guardian_name": guardian.get("guardian_name"),
            "relation": guardian.get("relation"),
            "mobile_number": guardian_doc.mobile_number if guardian_doc else None,
            "email": guardian_doc.email_address if hasattr(guardian_doc, "email_address") else None,
            "occupation": guardian_doc.occupation if hasattr(guardian_doc, "occupation") else None,
            "designation": guardian_doc.designation if hasattr(guardian_doc, "designation") else None,
            "work_address": guardian_doc.work_address if hasattr(guardian_doc, "work_address") else None,
            "education": guardian_doc.education if hasattr(guardian_doc, "education") else None
        }

        guardian_list.append(guardian_info)
    
    return guardian_list

@frappe.whitelist()
def update_student_profile_image(student_id, base64_image):
    """Efficiently update a student's profile image (base64 → File Doctype)."""
    import base64

    try:
        # Validate inputs
        if not student_id or not base64_image:
            return {"status": "error", "message": "Student ID and image data are required."}

        if not frappe.db.exists("Student", student_id):
            return {"status": "error", "message": f"Student {student_id} not found."}

        # Extract base64 data
        base64_data = base64_image.split(",", 1)[1] if base64_image.startswith("data:") else base64_image
        image_data = base64.b64decode(base64_data)

        # Size limits (1KB–5MB)
        if len(image_data) < 1024:
            return {"status": "error", "message": "Image data too small."}
        if len(image_data) > 5 * 1024 * 1024:
            return {"status": "error", "message": "Image too large (max 5MB)."}

        # Remove old public files for the student
        old_files = frappe.get_all(
            "File",
            filters={
                "attached_to_doctype": "Student",
                "attached_to_name": student_id,
                "is_private": 0,
            },
            pluck="name",
        )
        for file_name in old_files:
            frappe.delete_doc("File", file_name, ignore_permissions=True)

        # Create and insert new file
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"{student_id}_profile.jpg",
            "content": image_data,
            "attached_to_doctype": "Student",
            "attached_to_name": student_id,
            "is_private": 0
        })
        file_doc.insert(ignore_permissions=True)

        # Update Student record with new image URL
        frappe.db.set_value("Student", student_id, "image", file_doc.file_url)
        frappe.db.commit()

        return {
            "status": "success",
            "message": "Profile image updated successfully.",
            "image_url": file_doc.file_url
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(message=frappe.get_traceback(), title="Update Student Profile Image Error")
        return {"status": "error", "message": f"Failed to update image: {str(e)}"}


        
# @frappe.whitelist()
# def update_student_profile_image(student_id, base64_image):
#     try:
#         print("User:", frappe.session.user)

#         # Decode base64 image
#         image_data = base64.b64decode(base64_image.split(",")[1])
#         file_name = f"{student_id}_profile.jpg"

#         # Save file
#         saved_file = save_file(
#             fname=file_name,
#             content=image_data,
#             dt="Student",
#             dn=student_id,
#             is_private=0
#         )
#         print("File URL:", saved_file.file_url)

#         # Update Student image field
#         student_doc = frappe.get_doc("Student", student_id)
#         student_doc.image = saved_file.file_url
#         student_doc.save(ignore_permissions=True)
#         print(f"Updated Student image: {student_id}")

#         # Update Customer doctype image field - ROBUST VERSION
#         try:
#             # Method 1: Get customer from student.customer field
#             customer_name = None
            
#             # Check student document for customer field
#             if student_doc.get('customer'):
#                 customer_name = student_doc.customer
#                 print(f"Found customer via student.customer: {customer_name}")
            
#             # Method 2: If no customer field, try to find by student name
#             if not customer_name:
#                 customers = frappe.get_all("Customer", 
#                     filters={"student": student_id},
#                     fields=["name"]
#                 )
#                 if customers:
#                     customer_name = customers[0].name
#                     print(f"Found customer via Customer.student: {customer_name}")
            
#             # Method 3: Try to find by student name in customer name
#             if not customer_name:
#                 student_name = student_doc.student_name
#                 customers = frappe.get_all("Customer", 
#                     filters={"customer_name": ["like", f"%{student_name}%"]},
#                     fields=["name"]
#                 )
#                 if customers:
#                     customer_name = customers[0].name
#                     print(f"Found customer by name similarity: {customer_name}")
            
#             # Update customer if found
#             if customer_name and frappe.db.exists("Customer", customer_name):
#                 print(f"Updating customer: {customer_name}")
                
#                 # Direct SQL update to avoid field validation issues
#                 frappe.db.set_value('Customer', customer_name, 'image', saved_file.file_url)
#                 print(f"Successfully updated customer image: {customer_name}")
                
#             else:
#                 print(f"No customer found to update for student: {student_id}")
                
#         except Exception as cust_error:
#             print(f"Warning: Could not update customer image: {str(cust_error)}")
#             frappe.log_error(f"Customer image update failed: {str(cust_error)}")

#         frappe.db.commit()

#         return {
#             "status": "success", 
#             "message": "Profile image updated successfully.",
#             "image_url": saved_file.file_url
#         }
#     except Exception as e:
#         frappe.log_error(f"Error updating profile image: {str(e)}")
#         frappe.db.rollback()
#         return {"status": "error", "message": f"An error occurred: {str(e)}"}

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


import requests
from frappe.auth import LoginManager



MSG91_AUTH_KEY = "440500AhNX5vWp2a67a1d344P1"
MSG91_OTP_TEMPLATE_ID = "67b44535d6fc0513410877e4"

@frappe.whitelist(allow_guest=True)
def send_otp(phone: str):
    """
    Sends OTP via MSG91 to the given phone number if the user exists in Frappe's User doctype.
    """
    user_exists = frappe.db.exists("User", {"mobile_no": phone})

    if not user_exists:
        frappe.throw(
            "User does not exist. Try again with a different number.",
            frappe.PermissionError
        )

    url = "https://control.msg91.com/api/v5/otp"

    payload = {
        "authkey": MSG91_AUTH_KEY,
        "mobile": f"91{phone}",
        "template_id": MSG91_OTP_TEMPLATE_ID,
        "otp_length": 6,
        "otp_expiry": 5,
        "realTimeResponse": 1
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


@frappe.whitelist(allow_guest=True)
def send_otp_web(phone: str, role: str):
    """
    Sends OTP via MSG91 to the given phone number if:
      1. The user exists in the 'User' doctype.
      2. The user has the specified role.

    Args:
        phone (str): User's mobile number (without country code)
        role (str): Expected role name (e.g., 'Guardian', 'Instructor')

    Returns:
        dict: Success or failure response
    """
    # 1️⃣ Check if user exists
    user_name = frappe.db.exists("User", {"mobile_no": phone})
    if not user_name:
        return {"success": False, "message": "Phone number not registered!"}

    # 2️⃣ Fetch user document
    user_doc = frappe.get_doc("User", user_name)

    # 3️⃣ Verify role presence
    user_roles = [r.role for r in user_doc.roles]
    if role not in user_roles:
        return {"success": False, "message": f"User does not have '{role}' role."}

    # 4️⃣ Send OTP via MSG91
    url = "https://control.msg91.com/api/v5/otp"
    payload = {
        "authkey": MSG91_AUTH_KEY,
        "mobile": f"91{phone}",
        "template_id": MSG91_OTP_TEMPLATE_ID,
        "otp_length": 6,
        "otp_expiry": 5,
        "realTimeResponse": 1
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if data.get("type") == "success":
            return {"success": True, "otp_sent": True, "message": "OTP sent successfully."}
        else:
            return {"success": False, "message": data.get("message", "OTP sending failed.")}
    
    except requests.exceptions.RequestException as e:
        frappe.log_error(f"MSG91 OTP Sending Error: {str(e)}")
        return {"success": False, "message": "Server Error. Please try again."}

@frappe.whitelist(allow_guest=True)
def verify_otp_and_create_session(phone: str, otp: str, role: str = None):
    """
    Verifies OTP and creates a user session using LoginManager.
    Returns session ID (sid), user info, and roles.
    """
    # 1️⃣ Verify OTP
    if not verify_otp(phone, otp):
        frappe.throw("Incorrect OTP!", frappe.AuthenticationError)

    # 2️⃣ Find user linked to this phone
    user = frappe.db.get_value("User", {"mobile_no": phone}, "name")
    if not user:
        frappe.throw("User not found for this phone number.", frappe.AuthenticationError)

    # 3️⃣ Check role (if provided)
    user_roles = frappe.get_roles(user)
    if role:
        required_role = "Guardian" if role == "Guardian" else "Instructor"
        if required_role not in user_roles:
            frappe.throw(
                f"User does not have {required_role} role. Roles: {', '.join(user_roles)}",
                frappe.PermissionError
            )

    # 4️⃣ Create session using LoginManager
    login_manager = frappe.auth.LoginManager()
    login_manager.user = user
    login_manager.post_login()  # sets frappe.session and sid

    # 5️⃣ Return session info
    print(f"✅ OTP verified, session created for {user}")
    return {
        "status": "success",
        "message": "OTP verified. Session created.",
        "user": user,
        "roles": user_roles,
        "sid": frappe.session.sid
    }


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



@frappe.whitelist(allow_guest=True)  # Use allow_guest=True if users without login need access
def verify_otp_and_get_api_key(phone: str, otp: str):
    """
    Verifies OTP and returns both API key and API secret for authentication.
    """
    if not verify_otp(phone, otp):
        frappe.throw("Incorrect OTP!")
    print(phone)
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
        "mobile": f"91{phone}",  # ✅ Add country code!
        "otp": otp
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        frappe.logger().info(f"MSG91 Verify OTP response: {data}")  # ✅ Optional for debug

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

import requests


from frappe.auth import LoginManager

GOOGLE_OAUTH2_URL = "https://oauth2.googleapis.com/tokeninfo"

# Add this to your Frappe app's Python file (e.g., your_app/hooks.py or a custom API file)

import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def trigger_csrf_error():
    """
    Dummy function to simulate CSRF error scenarios
    This would typically be called when the login page is visited
    """
    return

@frappe.whitelist(allow_guest=True)
def verify_google_token_and_create_session(id_token: str, role: str = None):
    # print(id_token, role)
    """
    Verifies Google ID token, authenticates user by email, 
    validates required role, and creates a Frappe session using LoginManager.
    """
    try:
        # 1️⃣ Verify Google token with Google OAuth2 API
        response = requests.get(f"{GOOGLE_OAUTH2_URL}?id_token={id_token}")
        token_info = response.json()

        if "email" not in token_info:
            frappe.throw("Invalid Google token", frappe.AuthenticationError)

        email = token_info["email"]
        frappe.logger().info(f"🔍 Google token verified for {email}")

        # 2️⃣ Ensure user exists in Frappe
        user = frappe.db.get_value("User", {"email": email}, "name")
        if not user:
            frappe.throw("No user found with this Google account", frappe.AuthenticationError)

        # 3️⃣ Fetch user roles
        user_roles = frappe.get_roles(user)
        frappe.logger().info(f"User roles for {email}: {user_roles}")

        # 4️⃣ Validate role if provided
        if role:
            required_role = role.strip()
            if required_role not in user_roles:
                frappe.throw(
                    f"User does not have '{required_role}' role. Available roles: {', '.join(user_roles)}",
                    frappe.PermissionError
                )

        # 5️⃣ Create session using LoginManager
        login_manager = LoginManager()
        login_manager.user = user
        login_manager.post_login()

        frappe.db.commit()
        frappe.logger().info(f"✅ Google login successful for {email}")

        # 6️⃣ Return success response
        return {
            "success": True,
            "message": "Google authentication successful",
            "user": user,
            "email": email,
            "roles": user_roles,
            "sid": frappe.session.sid
        }

    except frappe.PermissionError as e:
        frappe.local.response["http_status_code"] = 403
        return {"success": False, "error": str(e)}

    except frappe.AuthenticationError as e:
        frappe.local.response["http_status_code"] = 401
        return {"success": False, "error": str(e)}

    except Exception as e:
        frappe.log_error(f"Google Auth Error: {str(e)}", "Google Login")
        frappe.local.response["http_status_code"] = 500
        return {"success": False, "error": "Authentication failed. Please try again."}


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



def send_notification_to_admin(instructor_name):
    """Send push notification to Administrator when an instructor is created."""
    try:
        # Fetch the Administrator's device ID from User Device doctype
        admin_device = frappe.get_all(
            "User Device", filters={"user": "Administrator"}, fields=["device_id"]
        )

        if admin_device:
            device_id = admin_device[0].get("device_id")
            title = "New Instructor Created"
            message = _(f"A new instructor '{instructor_name}' has been created.")

            if device_id:
                send_push_message(device_id, title, message)
                frappe.log("Push notification sent to Administrator")

    except Exception as e:
        frappe.log_error(f"Error sending notification to Administrator: {str(e)}", "send_notification_to_admin")

# def send_notification_to_admin(instructor_name, division_name):
#     """Send push notification to Administrator when an instructor is added to a division."""
#     try:
#         # Fetch the Administrator's device ID from User Device doctype
#         admin_device = frappe.get_all(
#             "User Device", filters={"user": "Administrator"}, fields=["device_id"]
#         )

#         if admin_device:
#             device_id = admin_device[0].get("device_id")
#             title = "Instructor Assigned"
#             message = _(f"A new instructor {instructor_name} has been assigned to {division_name}.")

#             if device_id:
#                 send_push_message(device_id, title, message)
#                 frappe.log("Push notification sent to Administrator")

#     except Exception as e:
#         frappe.log_error(f"Error sending notification to Administrator: {str(e)}", "send_notification_to_admin")




    
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
    guardian = frappe.get_all("Guardian", filters={"user": guardian_id}, limit=1)
    # print("Found Guardian doc:", guardian)

    if not guardian:
        frappe.throw(f"No Guardian found for user: {guardian_id}")

    # Use the name from the query
    guardian_doc = frappe.get_doc("Guardian", guardian[0].name)

    # Retrieve students linked to this guardian
    student_list = [student.as_dict() for student in guardian_doc.get("students")]

    # Process each student
    for student in student_list:
        current_program = get_current_enrollment(student["student"])
        student_groups = get_student_groups(student["student"], current_program.program)

        if not student_groups:
            frappe.throw(f"Student group not found for {student['student']}")

        student_group = student_groups[0]["label"]
        student["student_group"] = student_group

    profile = guardian_doc.image

    response = {
        "name": guardian_doc.guardian_name,
        "img_url": profile,
        "student_list": student_list,
    }

    # print(response)
    return response

@frappe.whitelist()
def get_student_app_data(studentID):
    from frappe.utils import today

    response = {}
    try:
        print(f"🔍 Received studentID: {studentID}, type: {type(studentID)}")

        # Handle case where studentID might be a stringified object
        if isinstance(studentID, str) and studentID.startswith("{"):
            import json
            try:
                student_data = json.loads(studentID)
                studentID = student_data.get("student") or student_data.get("name")
                print(f"📦 Extracted student ID from object: {studentID}")
            except json.JSONDecodeError:
                pass

        # Validate input
        if not studentID:
            frappe.throw("Student ID is required")

        print(f"🎯 Fetching student with ID: {studentID}")

        # Fetch the student record
        student = frappe.get_doc("Student", studentID)
        if not student:
            frappe.throw(f"Student {studentID} not found")

        # Get the current program and student group
        current_program = get_current_enrollment(student.name)
        student_groups = get_student_groups(student.name, current_program.program)
        if not student_groups:
            frappe.throw("Student group not found")

        student_group = student_groups[0]["label"]

        # Fetch student details from the group
        studentDetails = frappe.get_doc("Student Group Student", {
            "student": student.name,
            "parent": student_group,
            "active": 1
        })

        # ✅ Use image URL directly instead of base64
        img_url = student.image or None

        # Basic details
        response.update({
            "img_url": img_url,
            "name": studentDetails.student_name,
            "student": student.name,
            "student_name": studentDetails.student_name,
            "group_roll_no": studentDetails.group_roll_number,
            "student_group": student_group,
            "mobile": student.student_mobile_number,
            "address": student.address_line_1,
        })

        # Split class and section (if formatted like "Class-Section")
        parts = student_group.split("-")
        if len(parts) == 2:
            response["class"] = parts[0]
            response["section"] = parts[1]

        # ✅ Today's attendance
        date = today()
        StudentAttendance = frappe.qb.DocType("Student Attendance")

        today_attendance = (
            frappe.qb.from_(StudentAttendance)
            .select(StudentAttendance.status)
            .where(
                (StudentAttendance.student == student.name)
                & (StudentAttendance.student_group == student_group)
                & (StudentAttendance.date == date)
            )
        ).run(as_dict=True)

        response["status"] = (
            today_attendance[0]["status"] if today_attendance else "No Record"
        )

        # ✅ All attendance records
        all_attendance = (
            frappe.qb.from_(StudentAttendance)
            .select(StudentAttendance.status)
            .where(
                (StudentAttendance.student == student.name)
                & (StudentAttendance.student_group == student_group)
            )
        ).run(as_dict=True)

        present_count = sum(1 for record in all_attendance if record["status"] == "Present")
        absent_count = sum(1 for record in all_attendance if record["status"] == "Absent")
        leave_count = sum(1 for record in all_attendance if record["status"] == "Leave")

        # ✅ Update response
        response.update({
            "present_count": present_count,
            "absent_count": absent_count,
            "leave_count": leave_count,
        })

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Error in get_student_app_data")
        response["error"] = f"An error occurred: {str(e)}"

    return response



# @frappe.whitelist()
# def get_student_app_data(studentID):
#     from frappe.utils import today

#     response = {}
#     try:
#         print(f"🔍 Received studentID: {studentID}, type: {type(studentID)}")
        
#         # Handle case where studentID might be a stringified object
#         if isinstance(studentID, str) and studentID.startswith('{'):
#             import json
#             try:
#                 student_data = json.loads(studentID)
#                 # Extract the actual student ID from the object
#                 studentID = student_data.get('student') or student_data.get('name')
#                 print(f"📦 Extracted student ID from object: {studentID}")
#             except json.JSONDecodeError:
#                 pass
        
#         # If we still don't have a valid student ID, return error
#         if not studentID:
#             frappe.throw("Student ID is required")
        
#         print(f"🎯 Fetching student with ID: {studentID}")

#         # Fetch the student document
#         student = frappe.get_doc("Student", studentID)

#         if not student:
#             frappe.throw(f"Student {studentID} not found")

#         # Get the current program and student group
#         current_program = get_current_enrollment(student.name)
#         student_groups = get_student_groups(student.name, current_program.program)

#         if not student_groups:
#             frappe.throw("Student group not found")

#         student_group = student_groups[0]["label"]
#         studentDetails = frappe.get_doc("Student Group Student", {
#             "student": student.name,
#             "parent": student_group,
#             "active": 1
#         })

#         # Fetch profile image as base64
#         profile = student.image
#         base64image = None
#         if profile:
#             base64image = convert_image_to_base64(profile)

#         # Add basic details to response
#         response.update({
#             "base64profile": base64image,
#             "name": studentDetails.student_name,
#             "student": student.name,  # Make sure this is included
#             "student_name": studentDetails.student_name,
#             "group_roll_no": studentDetails.group_roll_number,
#             "student_group": student_group,
#             "mobile": student.student_mobile_number,
#             "address": student.address_line_1,
#         })

#         # Split student group into class and section
#         parts = student_group.split('-')
#         if len(parts) == 2:
#             response["class"] = parts[0]
#             response["section"] = parts[1]

#         # Attendance calculation
#         date = today()
#         StudentAttendance = frappe.qb.DocType("Student Attendance")

#         # Fetch today's attendance
#         today_attendance = (
#             frappe.qb.from_(StudentAttendance)
#             .select(StudentAttendance.status)
#             .where(
#                 (StudentAttendance.student == student.name) &
#                 (StudentAttendance.student_group == student_group) &
#                 (StudentAttendance.date == date)
#             )
#         ).run(as_dict=True)
#         today_status = today_attendance[0]["status"] if today_attendance else "No Record"
#         response["status"] = today_status

#         # Fetch all attendance records
#         all_attendance = (
#             frappe.qb.from_(StudentAttendance)
#             .select(StudentAttendance.status)
#             .where(
#                 (StudentAttendance.student == student.name) &
#                 (StudentAttendance.student_group == student_group)
#             )
#         ).run(as_dict=True)

#         # Initialize counts
#         present_count = sum(1 for record in all_attendance if record["status"] == "Present")
#         absent_count = sum(1 for record in all_attendance if record["status"] == "Absent")
#         leave_count = sum(1 for record in all_attendance if record["status"] == "Leave")

#         # Update response with attendance counts
#         response.update({
#             "present_count": present_count,
#             "absent_count": absent_count,
#             "leave_count": leave_count,
#         })

#     except frappe.exceptions.ValidationError as e:
#         frappe.log_error(message=str(e), title="Error in get_student_app_data")
#         response["error"] = f"Validation Error: {str(e)}"
#     except Exception as e:
#         frappe.log_error(message=frappe.get_traceback(), title="Error in get_student_app_data")
#         response["error"] = f"An error occurred: {str(e)}"
    
#     # print(f"📤 Sending response: {response}")
#     return response



ROLE_MAPPING = {
    "teacher": "Instructor",
    "parent": "Guardian"
}

@frappe.whitelist()
def get_user_details(username=None, role=None):
    """
    Fetch user details for the current session user 
    based on their validated role (Instructor or Guardian).
    """
    # Ensure user is logged in
    if not frappe.session.user or frappe.session.user == "Guest":
        frappe.throw("User not logged in", frappe.PermissionError)

    session_user = frappe.session.user
    roles = frappe.get_roles(session_user)
    frappe.logger().info(f"👤 Session user: {session_user}, roles: {roles}")

    mapped_role = ROLE_MAPPING.get(role, role)
    frappe.logger().info(f"Expected role: {mapped_role}")

    user_details = None

    # ✅ Explicit checks for role presence
    if mapped_role == "Instructor" and mapped_role in roles:
        user_details = get_instructor_app_data(session_user)
        frappe.logger().info("✅ Instructor data fetched successfully")
    elif mapped_role == "Guardian" and mapped_role in roles:
        user_details = get_guardian_app_data(session_user)
        frappe.logger().info("✅ Guardian data fetched successfully")
    else:
        frappe.throw(
            f"User does not have required role '{mapped_role}'. User roles: {', '.join(roles)}",
            frappe.PermissionError
        )

    return {
        "user": session_user,
        "roles": roles,
        "user_details": user_details
    }



# @frappe.whitelist()
# def get_guardian_app_data(guardian_id):
#     guardian_doc = frappe.get_doc("Guardian", {"email_address": guardian_id})
#     print(guardian_doc)

#     # Retrieve students linked to this guardian and convert them to dictionaries
#     student_list = [student.as_dict() for student in guardian_doc.get("students")]  # Convert to dicts

#     # Now you can modify student_list freely
#     for student in student_list:
#         current_program = get_current_enrollment(student["student"])  # Accessing as dict
#         student_groups = get_student_groups(student["student"], current_program.program)

#         if not student_groups:
#             frappe.throw("Student group not found")

#         student_group = student_groups[0]["label"]
#         print(student)
#         student["student_group"] = student_group  # Add student_group to the dict

#     if not student_list:
#         frappe.throw(f"No students found for Guardian ID: {guardian_id}")

#     profile = guardian_doc.image

#     # Convert the profile image to base64 if available
#     base64image = convert_image_to_base64(profile) if profile else None
#     print(student_list)
#     response = {
#         "name": guardian_doc.guardian_name,
#         "base64profile": base64image,
#         "student_list": student_list,
#     }
#     print(response)
#     return response




# @frappe.whitelist()
# def get_student_app_data(studentID):
#     from frappe.utils import today

#     response = {}
#     # studentID = frappe.session.user

#     try:
#         # Fetch the student document
#         student = frappe.get_doc("Student", {"name": studentID})
#         if not student:
#             frappe.throw("Student not found")

#         # Get the current program and student group
#         current_program = get_current_enrollment(student.name)
#         student_groups = get_student_groups(student.name, current_program.program)

#         if not student_groups:
#             frappe.throw("Student group not found")

#         student_group = student_groups[0]["label"]
#         studentDetails = frappe.get_doc("Student Group Student", {
#             "student": student.name,
#             "parent": student_group,
#             "active": 1
#         })

#         # Fetch profile image as base64
#         profile = student.image
#         base64image = None
#         if profile:
#             base64image = convert_image_to_base64(profile)

#         # Fetch notice list
#         #notice_data = get_notice_list(student_group)

#         # Add basic details to response
#         response.update({
#             #"notices": notice_data,
#             "base64profile": base64image,
#             "name": studentDetails.student_name,
#             "ID":student.name,
#             "group_roll_no": studentDetails.group_roll_number,
#             "student_group": student_group,
#             "mobile": student.student_mobile_number,
#             "address": student.address_line_1,
#         })

#         # Split student group into class and section
#         parts = student_group.split('-')
#         if len(parts) == 2:
#             response["class"] = parts[0]
#             response["section"] = parts[1]

#         # Attendance calculation
#         date = today()
#         StudentAttendance = frappe.qb.DocType("Student Attendance")

#         # Fetch today's attendance
#         today_attendance = (
#             frappe.qb.from_(StudentAttendance)
#             .select(StudentAttendance.status)
#             .where(
#                 (StudentAttendance.student == student.name) &
#                 (StudentAttendance.student_group == student_group) &
#                 (StudentAttendance.date == date)
#             )
#         ).run(as_dict=True)
#         today_status = today_attendance[0]["status"] if today_attendance else "No Record"
#         response["status"] = today_status

#         # Fetch all attendance records
#         all_attendance = (
#             frappe.qb.from_(StudentAttendance)
#             .select(StudentAttendance.status)
#             .where(
#                 (StudentAttendance.student == student.name) &
#                 (StudentAttendance.student_group == student_group)
#             )
#         ).run(as_dict=True)

#         # Initialize counts
#         present_count = sum(1 for record in all_attendance if record["status"] == "Present")
#         absent_count = sum(1 for record in all_attendance if record["status"] == "Absent")
#         leave_count = sum(1 for record in all_attendance if record["status"] == "Leave")

#         # Update response with attendance counts
#         response.update({
#             "present_count": present_count,
#             "absent_count": absent_count,
#             "leave_count": leave_count,
#         })

#     except Exception as e:
#         frappe.log_error(message=frappe.get_traceback(), title="Error in get_student_app_data")
#         frappe.throw(f"An error occurred: {str(e)}")

#     return response


# @frappe.whitelist()
# def get_user_details(username, role):
#     if frappe.session.user:
#         roles = frappe.get_roles(username)
#         user_details = None
#         if "Instructor" in roles and role == "teacher":
#             user_details = get_instructor_app_data(username)
#             print("hello")
#         if "Guardian" in roles and role == "parent":
#             user_details = get_guardian_app_data(username)
#             print("olleh")
        
#         print(user_details)
#         return {"roles": roles, "user_details": user_details}
#     else:
#         return
    
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
    print(profile)

    response = {
        "name": instructor_doc.instructor_name,
        "img_url": profile,
        "student_groups": student_groups,
    }
    return response

import frappe
import base64
import requests
from io import BytesIO
from PIL import Image

# def convert_image_to_base64_with_compression(image_url, max_size=(300, 300), quality=70):
#     """
#     Fetch an image from a given URL, compress it, and return Base64 string.

#     Args:
#         image_url (str): URL of the image (e.g. /files/student.jpg)
#         max_size (tuple): Resize dimensions (width, height)
#         quality (int): Compression quality for JPEG/WebP
#     Returns:
#         str: Base64 encoded compressed image (with data URI prefix)
#     """
#     if not image_url:
#         return None

#     # Replace https with http and append :8000 for local sites
#     base_url = frappe.utils.get_url().replace("https://", "http://")

#     if not image_url.startswith("http"):
#         image_url = base_url + image_url

#     try:
#         response = requests.get(image_url, timeout=5)
#         if response.status_code != 200:
#             return None

#         # Open the image from bytes
#         image_bytes = BytesIO(response.content)
#         with Image.open(image_bytes) as img:
#             # Convert RGBA → RGB to avoid transparency issues
#             if img.mode in ("RGBA", "P"):
#                 img = img.convert("RGB")

#             # Resize (maintaining aspect ratio)
#             img.thumbnail(max_size, Image.Resampling.LANCZOS)

#             # Compress and save to buffer
#             buffer = BytesIO()
#             img.save(buffer, format="JPEG", optimize=True, quality=quality)
#             buffer.seek(0)

#             # Convert to Base64
#             encoded = base64.b64encode(buffer.read()).decode("utf-8")

#             # Return browser-ready Base64 image
#             return f"data:image/jpeg;base64,{encoded}"

#     except Exception as e:
#         frappe.log_error(f"Image compression failed: {str(e)}", "convert_image_to_base64")
#         return None

@frappe.whitelist()
def get_student_attendance_records(based_on, date=None, student_group=None, calculate_count_data=False, course_schedule=None):
    """Main entrypoint — delegates to appropriate function based on flag."""
    if not frappe.session.user:
        return []

    # Fetch student group based on course schedule if needed
    if based_on == "Course Schedule":
        student_group = frappe.db.get_value("Course Schedule", course_schedule, "student_group")

    if calculate_count_data:
        return get_detailed_student_data(student_group, date, course_schedule)
    else:
        data = get_basic_student_data(student_group)
        # print(data)
        return data


# ---------------------- BASIC STUDENT DATA ---------------------- #
import frappe
from datetime import date
from frappe.utils import getdate
from frappe.query_builder import DocType

@frappe.whitelist()
def get_basic_student_data(student_group):
    """Return minimal info — ID, name, roll no, image URL, and attendance status flags."""
    
    # from datetime import date
    # from frappe.query_builder import DocType

    StudentGroupStudent = DocType("Student Group Student")
    Student = DocType("Student")

    # Step 1: Join Student and Student Group Student to get required fields in one query
    student_list = (
        frappe.qb.from_(StudentGroupStudent)
        .inner_join(Student)
        .on(StudentGroupStudent.student == Student.name)
        .select(
            StudentGroupStudent.student,
            StudentGroupStudent.student_name,
            StudentGroupStudent.group_roll_number,
            Student.image.as_("img_url"),  # directly include image from Student doctype
        )
        .where(
            (StudentGroupStudent.parent == student_group)
            & (StudentGroupStudent.active == 1)
        )
        .orderby(StudentGroupStudent.group_roll_number)
    ).run(as_dict=True)

    # Step 2: Attendance lookup
    student_ids = [s["student"] for s in student_list]
    today = date.today()

    attendance_records = frappe.get_all(
        "Student Attendance",
        filters={"student": ["in", student_ids], "date": today},
        fields=["student", "status"],
    )

    # Step 3: Separate present and on-leave students
    present_stud = {rec.student for rec in attendance_records if rec.status and rec.status.lower() == "present"}
    on_leave_stud = {rec.student for rec in attendance_records if rec.status and rec.status.lower() in ["leave", "on leave"]}

    # Step 4: Attach flags (no need to query Student again)
    for student in student_list:
        # student["img_url"] = student.pop("image", None)
        student["present"] = 1 if student["student"] in present_stud else 0
        student["on_leave"] = 1 if student["student"] in on_leave_stud else 0

    return student_list


import frappe
from frappe.utils import getdate

@frappe.whitelist()
def get_detailed_student_data(student_group, date=None, course_schedule=None):
    """Return full data — includes personal info, today's attendance, and summary counts."""

    StudentGroupStudent = DocType("Student Group Student")
    Student = DocType("Student")
    StudentAttendance = DocType("Student Attendance")

    date = getdate()

    # ✅ Step 1: JOIN Student Group Student with Student to get all info in one query
    student_list = (
        frappe.qb.from_(StudentGroupStudent)
        .join(Student)
        .on(StudentGroupStudent.student == Student.name)
        .select(
            StudentGroupStudent.student,
            StudentGroupStudent.student_name,
            StudentGroupStudent.group_roll_number,
            Student.image.as_("img_url"),
            Student.address_line_1.as_("address"),
            Student.student_mobile_number.as_("mobile"),
        )
        .where(
            (StudentGroupStudent.parent == student_group)
            & (StudentGroupStudent.active == 1)
        )
        .orderby(StudentGroupStudent.group_roll_number)
    ).run(as_dict=True)
    
    if not student_list:
        return []

    student_ids = [s.student for s in student_list]

    # ✅ Step 2: Fetch attendance based on course_schedule or date
    if course_schedule:
        student_attendance_list = (
            frappe.qb.from_(StudentAttendance)
            .select(StudentAttendance.student, StudentAttendance.status)
            .where(StudentAttendance.course_schedule == course_schedule)
        ).run(as_dict=True)
    else:
        student_attendance_list = (
            frappe.qb.from_(StudentAttendance)
            .select(StudentAttendance.student, StudentAttendance.status)
            .where(
                (StudentAttendance.student_group == student_group)
                & (StudentAttendance.date == date)
                & ((StudentAttendance.course_schedule == "") | (StudentAttendance.course_schedule.isnull()))
            )
        ).run(as_dict=True)

    # ✅ Step 3: Today's attendance
    today_attendance_list = (
        frappe.qb.from_(StudentAttendance)
        .select(StudentAttendance.student, StudentAttendance.status)
        .where(
            (StudentAttendance.student_group == student_group)
            & (StudentAttendance.date == date)
        )
    ).run(as_dict=True)

    # ✅ Step 4: All attendance (for summary)
    all_attendance_list = (
        frappe.qb.from_(StudentAttendance)
        .select(StudentAttendance.student, StudentAttendance.status)
        .where(StudentAttendance.student_group == student_group)
    ).run(as_dict=True)

    # ✅ Step 5: Enrich each record
    for s in student_list:
        s.status = next((a.status for a in today_attendance_list if a.student == s.student), None)
        s.present_count = sum(1 for a in all_attendance_list if a.student == s.student and a.status == "Present")
        s.absent_count = sum(1 for a in all_attendance_list if a.student == s.student and a.status == "Absent")
        s.leave_count = sum(1 for a in all_attendance_list if a.student == s.student and a.status not in ("Present", "Absent"))
    # print(student_list)
    return student_list

@frappe.whitelist()
def get_guardian_numbers(student_id):
    """Return all guardian names and mobile numbers for a given student."""
    from frappe.query_builder import DocType

    StudentGuardian = DocType("Student Guardian")
    Guardian = DocType("Guardian")

    # Join Student Guardian child table with Guardian to fetch mobile numbers
    guardians = (
        frappe.qb.from_(StudentGuardian)
        .join(Guardian)
        .on(StudentGuardian.guardian == Guardian.name)
        .select(
            Guardian.guardian_name,
            Guardian.mobile_number
        )
        .where(StudentGuardian.parent == student_id)
    ).run(as_dict=True)
    print(guardians)
    # Return clean list
    return guardians or []


# def get_basic_student_data(student_group):
#     """Return minimal info — ID, name, roll no, compressed base64 image, and attendance status flags."""

#     # Step 1: Fetch all active students in the group
#     student_list = frappe.get_all(
#         "Student Group Student",
#         fields=["student", "student_name", "group_roll_number"],
#         filters={"parent": student_group, "active": 1},
#         order_by="group_roll_number",
#     )

#     # Step 2: Collect all student IDs
#     student_ids = [s.student for s in student_list]
#     today = date.today()

#     # Step 3: Fetch today's attendance records for these students
#     attendance_records = frappe.get_all(
#         "Student Attendance",
#         filters={"student": ["in", student_ids], "date": today},
#         fields=["student", "status"],
#     )

#     # Step 4: Separate them into two sets for quick lookup
#     present_stud = {rec.student for rec in attendance_records if rec.status.lower() == "present"}
#     on_leave_stud = {rec.student for rec in attendance_records if rec.status.lower() in "leave"}

#     # Step 5: Enrich each student
#     for student in student_list:
#         student_doc = frappe.get_doc("Student", student.student)
#         profile = student_doc.image

#         # Base64 compressed profile image
#         student.base64profile = (
#             convert_image_to_base64_with_compression(profile) if profile else None
#         )

#         # Mark attendance and leave flags
#         student.present = 1 if student.student in present_stud else 0
#         student.on_leave = 1 if student.student in on_leave_stud else 0

#     return student_list

# ---------------------- DETAILED STUDENT DATA ---------------------- #
# def get_detailed_student_data(student_group, date=None, course_schedule=None):
#     """Returns full data — includes personal info, today's attendance, and summary counts."""
#     student_list = frappe.get_all(
#         "Student Group Student",
#         fields=["student", "student_name", "group_roll_number"],
#         filters={"parent": student_group, "active": 1},
#         order_by="group_roll_number",
#     )

#     StudentAttendance = frappe.qb.DocType("Student Attendance")

#     # Fetch attendance list
#     if course_schedule:
#         student_attendance_list = (
#             frappe.qb.from_(StudentAttendance)
#             .select(StudentAttendance.student, StudentAttendance.status)
#             .where(StudentAttendance.course_schedule == course_schedule)
#         ).run(as_dict=True)
#     else:
#         student_attendance_list = (
#             frappe.qb.from_(StudentAttendance)
#             .select(StudentAttendance.student, StudentAttendance.status)
#             .where(
#                 (StudentAttendance.student_group == student_group)
#                 & (StudentAttendance.date == date)
#                 & (
#                     (StudentAttendance.course_schedule == "")
#                     | (StudentAttendance.course_schedule.isnull())
#                 )
#             )
#         ).run(as_dict=True)

#     # Today's attendance
#     from frappe.utils import getdate
#     date = getdate()
#     today_attendance_list = (
#         frappe.qb.from_(StudentAttendance)
#         .select(StudentAttendance.student, StudentAttendance.status)
#         .where(
#             (StudentAttendance.student_group == student_group)
#             & (StudentAttendance.date == date)
#         )
#     ).run(as_dict=True)

#     # All attendance for counts
#     all_attendance_list = (
#         frappe.qb.from_(StudentAttendance)
#         .select(StudentAttendance.student, StudentAttendance.status)
#         .where(StudentAttendance.student_group == student_group)
#     ).run(as_dict=True)

#     # Main loop: gather all details
#     for student in student_list:
#         student_doc = frappe.get_doc("Student", {"name": student.student})

#         # Common info
#         profile = student_doc.image
#         student.base64profile = convert_image_to_base64(profile) if profile else None
#         student.address = student_doc.address_line_1
#         student.mobile = student_doc.student_mobile_number

#         # Today's attendance
#         student.status = None
#         for attendance in today_attendance_list:
#             if student.student == attendance.student:
#                 student.status = attendance.status
#                 break

#         # Attendance summary
#         student.present_count = 0
#         student.absent_count = 0
#         student.leave_count = 0

#         for attendance in all_attendance_list:
#             if student.student == attendance.student:
#                 if attendance.status == "Present":
#                     student.present_count += 1
#                 elif attendance.status == "Absent":
#                     student.absent_count += 1
#                 else:
#                     student.leave_count += 1

#     return student_list



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
    try:
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
        
        frappe.db.commit()
        
        # Send push notifications to parents of absent students
        send_notification_to_app(student_list)
        
        # Return structured JSON response instead of using msgprint
        return {
            "message": "Attendance has been marked successfully.",
            "present_count": len(present),
            "absent_count": len(absent),
            "status": "success"
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Attendance marking failed: {str(e)}")
        return {
            "message": f"Failed to mark attendance: {str(e)}",
            "status": "error"
        }
    

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


MSG91_AUTH_KEY = "440500AhNX5vWp2a67a1d344P1"
MSG91_TEMPLATE_ID = "67b44535d6fc0513410877e4"
MSG91_SENDER_ID = "AWAMIE"  # Ensure this is approved in MSG91
MSG91_ROUTE = "4"  # Transactional route

@frappe.whitelist()
def send_notification_to_app(student_list):
    for student in student_list:
        guardians = get_student_guardians(student)

        student_doc = frappe.get_doc("Student", student)
        student_name = student_doc.student_name

        for guardian in guardians:
            guardian_doc = frappe.get_doc("Guardian", guardian.get("guardian"))
            guardian_email = guardian_doc.email_address
            guardian_phone = guardian_doc.mobile_number

            if not guardian_email:
                print(f"⚠️ No email found for guardian of student {student_name}")
                continue

            msg = _(f"Dear Parent, your child {student_name} is marked absent today. Please check the attendance for further details.")
            title = _("Al-Ummah Girls High School")

            # Push Notification
            existing_device = frappe.get_all(
                "User Device", filters={"user": guardian_email}, fields=["device_id"]
            )
            if existing_device:
                device_id = existing_device[0].get("device_id")
                if device_id:
                    notify_push(device_id, title, msg, email=guardian_email)

            # Email Notification
            notify_email(guardian_email, "Your child was marked absent", msg)

            # SMS Notification
            if guardian_phone:
                notify_sms(guardian_phone, student_name)

    return {"status": "success", "message": "Notifications sent to guardians of absent students."}
def notify_push(device_id, title, message, email=None):
    try:
        
        send_push_message(device_id, title, message)
        print(f"✅ Push notification sent to {email or device_id}")
    except Exception as e:
        print(f"❌ Error sending push notification to {email or device_id}: {e}")

def notify_email(email, subject, message):
    try:
        frappe.sendmail(
            recipients=[email],
            subject=subject,
            message=message
        )
        print(f"✅ Email sent to {email}")
    except Exception as e:
        print(f"❌ Error sending email to {email}: {e}")

import requests

import requests

def notify_sms(phone: str, student_name: str):
    # Check if the phone number already has the country code '91'
    if not phone.startswith("91"):
        phone = "91" + phone  # Add '91' if missing
    
    try:
        send_absence_sms(phone, student_name)
        print(f"✅ SMS sent to {phone}")
    except Exception as e:
        print(f"❌ Error sending SMS to {phone}: {e}")


def send_absence_sms(mobile: str, student_name: str):
    url = "https://control.msg91.com/api/v5/flow"
    headers = {
        "accept": "application/json",
        "authkey": "440500AhNX5vWp2a67a1d344P1",  # Use your actual MSG91 Auth Key
        "content-type": "application/json"
    }

    payload = {
        "template_id": "67a9cc85d6fc0568b5678ec2",  # Use your actual template ID
        "short_url": "0",  # Turn off if not needed
        "realTimeResponse": "1",  # Optional: Real-time response flag
        "recipients": [
            {
                "mobiles": mobile,
                "var1": student_name  # Replacing ##var1## in the template with the student's name
            }
        ]
    }

    try:
        # Make the POST request to MSG91 API
        response = requests.post(url, json=payload, headers=headers)
        
        # Check if response is successful
        if response.status_code == 200:
            data = response.json()
            if data.get("type") == "success":
                print(f"✅ SMS sent successfully to {mobile}")
            else:
                print(f"❌ SMS failed: {data}")
        else:
            print(f"❌ Error: Status code {response.status_code}. Response: {response.text}")
    except Exception as e:
        print(f"❌ Error sending SMS: {e}")



# def send_sms_via_msg91(mobile, student_name):
#     """
#     Sends an SMS via MSG91 API.
#     """
#     url = "https://control.msg91.com/api/v5/flow/"
#     headers = {
#         "authkey": MSG91_AUTH_KEY,
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "flow_id": MSG91_TEMPLATE_ID,  # Use 'flow_id' instead of 'template_id' for MSG91 Flow API
#         "sender": MSG91_SENDER_ID,
#         "short_url": "1",
#         "recipients": [
#             {
#                 "mobiles": mobile,
#                 "VAR1": student_name  # Matches ##var1## in your MSG91 template
#             }
#         ]
#     }
    
#     try:
#         response = requests.post(url, json=payload, headers=headers)
#         response_data = response.json()
#         if response.status_code == 200 and response_data.get("type") == "success":
#             print(f"SMS successfully sent to {mobile}")
#         else:
#             print(f"Failed to send SMS to {mobile}: {response_data}")
#     except Exception as e:
#         print(f"Error sending SMS to {mobile}: {e}")

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
        existing_guardian = frappe.db.get_value("Guardian", {"mobile_number": phone_number})

        if existing_guardian:
            guardian_name = frappe.db.get_value("Guardian", {"name": existing_guardian}, "guardian_name")
        else:
            guardian_email = generate_unique_email(guardian_name)
            
            user_doc = frappe.get_doc({
                "doctype": "User",
                "mobile_no": phone_number,
                "first_name": guardian_name,
                "email": guardian_email
            }).insert(ignore_permissions=True)
            user_doc.new_password = "alummah"
            user_doc.add_roles("Guardian")
            
            guardian_doc = frappe.get_doc({
                "doctype": "Guardian",
                "guardian_name": guardian_name,
                "mobile_number": phone_number,
                "email_address": guardian_email,
                "user": user_doc.name  # If Guardian DocType has a user link
            }).insert(ignore_permissions=True)

            existing_guardian = guardian_doc.name

        student_doc = frappe.get_doc("Student", student_id)

        if any(g.guardian == existing_guardian for g in student_doc.guardians):
            return "Guardian is already linked to the student."

        student_guardian = student_doc.append("guardians", {})
        student_guardian.guardian = existing_guardian
        student_guardian.guardian_name = guardian_name
        student_guardian.relation = relation

        student_doc.save(ignore_permissions=True)
        frappe.db.commit()

        return "Guardian information saved successfully."

    except frappe.exceptions.ValidationError as e:
        frappe.log_error(f"Validation Error: {str(e)}", "Add Guardian")
        return f"Error: {str(e)}"
    except Exception as e:
        frappe.log_error(f"Unexpected Error: {str(e)}", "Add Guardian")
        return f"Error: {str(e)}"



@frappe.whitelist()
def submit_leave_application(student, from_date, to_date, student_group, reason, image=None):
    import base64
    from frappe.utils.file_manager import save_file

    try:
        # 🔹 Ensure the student exists
        if not frappe.db.exists("Student", student):
            return {"status": "error", "message": f"Student '{student}' not found. Please verify the Student ID."}

        # 🔹 Check for duplicate leave before creating doc
        duplicate = frappe.db.sql(
            """
            SELECT name 
            FROM `tabStudent Leave Application`
            WHERE student=%(student)s
            AND (
                (%(from_date)s BETWEEN from_date AND to_date)
                OR (%(to_date)s BETWEEN from_date AND to_date)
                OR (from_date BETWEEN %(from_date)s AND %(to_date)s)
            )
            AND docstatus < 2
            """,
            {"student": student, "from_date": from_date, "to_date": to_date},
            as_dict=True,
        )

        if duplicate:
            existing = duplicate[0].name
            return {
                "status": "error",
                "message": f"Duplicate leave application already exists ({existing}) for this student between these dates."
            }

        # 🔹 Create new Leave Application
        doc = frappe.new_doc("Student Leave Application")
        doc.student = student
        doc.from_date = from_date
        doc.to_date = to_date
        doc.student_group = student_group
        doc.reason = reason

        doc.insert(ignore_permissions=True, ignore_mandatory=True)

        # 🔹 Handle image (optional)
        if image:
            image_data = base64.b64decode(image)
            fname = "leave_application_image.jpg"

            saved_file = save_file(
                fname=fname,
                content=image_data,
                dt="Student Leave Application",
                dn=doc.name,
                is_private=0
            )
            doc.document = saved_file.file_url

        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "status": "success",
            "message": "Leave application submitted successfully.",
            "docname": doc.name
        }

    except frappe.ValidationError as e:
        frappe.db.rollback()
        return {"status": "error", "message": str(e)}

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(message=frappe.get_traceback(), title="Leave Application Submit Error")
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}



# @frappe.whitelist(allow_guest=True)
# def submit_leave_application(student, from_date, to_date, student_group, document_image=None):
#     # Convert from_date and to_date directly as datetime objects without specifying a format
#     # from_date = datetime.strptime(from_date, "%Y-%m-%d")  # Correct format for YYYY-MM-DD
#     # to_date = datetime.strptime(to_date, "%Y-%m-%d")  # Correct format for YYYY-MM-DD

#     # Create a new Leave Application document
#     doc = frappe.new_doc("Student Leave Application")
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

import requests
import base64
from io import BytesIO

@frappe.whitelist()
def get_leave_application(name):
    try:
        # Fetch the Leave Application document based on student group and student
        leave = frappe.get_doc(
            "Student Leave Application",  # The Doctype
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
    print(student_group)
    """Return list of draft leave applications for a group or a single student's leave details."""
    
    # Ensure user is logged in
    if not frappe.session.user:
        frappe.throw("You must be logged in to access this data.")
    
    # If a specific student is provided → delegate to get_leave_application()
    if student:
        return get_leave_application(student_group, student)
    
    # Fetch all DRAFT (docstatus = 0) leave applications for the group
    leave_list = frappe.get_all(
        "Student Leave Application",
        fields=[
            "name",
            "student",
            "student_name",
            "from_date",
            "to_date",
            "total_leave_days",
            "reason",
            "document",
            "mark_as_present",
            "docstatus"
        ],
        filters={
            "student_group": student_group
        },
        order_by="creation desc"
    )

    # Optional: Attach document image URL if present
    for leave in leave_list:
        leave["img_url"] = leave.get("document") if leave.get("document") else None
    print(leave_list)
    return leave_list



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



import requests
import base64

def convert_image_to_base64(image_url):
    # Replace https with http and append :8000
    base_url = frappe.utils.get_url().replace("https://", "http://")
    # print(f"Using base URL: {base_url}")

    if not image_url.startswith('http'):
        image_url = base_url + image_url

    response = requests.get(image_url)

    if response.status_code == 200:
        image_bytes = BytesIO(response.content)
        return base64.b64encode(image_bytes.read()).decode('utf-8')

    return None


@frappe.whitelist()
def approve_leave(name):
    try:
        leave = frappe.get_doc("Student Leave Application", name)
        if not leave:
            return {"success": False, "message": "Leave application not found.", "status": None}

        # Approve and submit the leave
        leave.save(ignore_permissions=True)
        leave.submit()

        frappe.db.commit()

        return {
            "success": True,
            "message": "Leave approved and submitted successfully.",
            "name": name,
            "status": "Approved",
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Approve Leave Error")
        return {"success": False, "message": f"An error occurred: {str(e)}", "status": None}




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
        print(student_list)
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
def send_push_notification_to_guardian(guardian_email, student_name, notice_heading, notice_message):
    existing_device = frappe.get_all(
        "User Device", filters={"user": guardian_email}, fields=["device_id"]
    )

    if not existing_device:
        return

    device_id = existing_device[0].get("device_id")
    if not device_id:
        return

    title = _(f"Notice: {notice_heading}")
    msg = _(f"Dear Parent, a new notice titled '{notice_heading}' has been posted for your child {student_name}. {notice_message}")

    try:
        
        send_push_message(device_id, title, msg)
        print(f"Push notification sent to {guardian_email} ({device_id})")
    except Exception as e:
        frappe.log_error(f"Push notification error for {guardian_email}: {e}")


def send_email_to_guardian(guardian_email, notice_heading, notice_message, student_name):
    subject = f"Notice: {notice_heading}"
    msg = _(f"Dear Parent, a new notice titled '{notice_heading}' has been posted for your child {student_name}. {notice_message}")

    try:
        frappe.sendmail(
            recipients=[guardian_email],
            subject=subject,
            message=msg
        )
        print(f"Email sent to {guardian_email}")
    except Exception as e:
        frappe.log_error(f"Email sending error for {guardian_email}: {e}")


@frappe.whitelist()
def send_notice_notification_to_app(student_list, notice_heading, notice_message):
    for student in student_list:
        student_doc = frappe.get_doc("Student", student["student"])
        student_name = student_doc.student_name
        guardians = get_student_guardians(student["student"])

        for guardian in guardians:
            guardian_doc = frappe.get_doc("Guardian", guardian.get("guardian"))
            guardian_email = guardian_doc.email_address

            if guardian_email:
                send_push_notification_to_guardian(guardian_email, student_name, notice_heading, notice_message)
                send_email_to_guardian(guardian_email, notice_heading, notice_message, student_name)

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
    try:
        if frappe.session.user:
            # Forcefully get the document ignoring permissions
            notice = frappe.get_doc("Student Notice", name)
            
            # Optionally check docstatus to avoid deleting submitted ones
            if notice.docstatus != 0:
                frappe.throw("Cannot delete a submitted or cancelled notice.")

            # Delete forcefully
            frappe.delete_doc("Student Notice", name, ignore_permissions=True)
            frappe.db.commit()
            return "Notice deleted successfully."
        else:
            frappe.throw("User not logged in.")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delete Notice Error")
        frappe.throw(f"Error deleting notice: {str(e)}")

    

