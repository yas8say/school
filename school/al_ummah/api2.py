# import json

# import frappe
# import base64

# from frappe import _
# from frappe.utils.data import cstr, flt, getdate
# from frappe.model.mapper import get_mapped_doc
# from datetime import datetime
# from frappe.utils.dateutils import get_dates_from_timegrain
# from frappe.model.document import Document
# from frappe.utils.file_manager import save_file



# @frappe.whitelist()
# def register_device(device_id):
#     if frappe.session.user:
#         user = frappe.session.user
#         # Check if a device ID already exists for the user
#         existing_device = frappe.get_all(
#             "User Device", filters={"user": user, "device_id": device_id}
#         )

#         if not existing_device:
#             # Create a new User Device record
#             doc = frappe.get_doc({
#                 "doctype": "User Device",
#                 "user": user,
#                 "device_id": device_id,
#             })
#             doc.insert(ignore_permissions=True)
#             frappe.db.commit()
#         else:
#             frappe.log("Device already registered for this user.")
#     else:
#         return

# #school.al_ummah.api.register_device

# @frappe.whitelist()
# def unregister_device(device_id):
#     if frappe.session.user:
#         user = frappe.session.user
#         # Check if a device ID exists for the user
#         existing_device = frappe.get_doc("User Device", {"user": user, "device_id": device_id})
        
#         print(existing_device.name)
#         if existing_device:
#             # Delete the User Device record
#             frappe.delete_doc("User Device", existing_device.name, ignore_permissions=True)
#             frappe.db.commit()
#             return {"status": "success", "message": "Device unregistered successfully."}
#         else:
#             return {"status": "failed", "message": "Device not found for this user."}
#     else:
#         return

# @frappe.whitelist()
# def get_employee_name():
#     user_id = frappe.session.user  # Get the logged-in user's ID
#     if user_id == "Administrator":
#         return None  # Exit if the user is Administrator

#     # Fetch the Employee name based on the user_id
#     employee = frappe.db.get_value("Employee", {"user_id": user_id}, "name")
#     return employee


# @frappe.whitelist()
# def check_user_with_role():
#     user_id = frappe.session.user  # Get the logged-in user's ID
    
#     # Check if the user is an Administrator
#     if user_id == "Administrator":
#         return "Invalid"  # Return "Invalid" if the user is an Administrator, or adjust as needed
    
#     roles = frappe.get_roles(user_id)
    
#     # Check for valid roles and return specific role name
#     if "Instructor" in roles:
#         return "Instructor"
#     elif "Student" in roles:
#         return "Student"
    
#     return "Invalid"  # Return "Invalid" if the role is neither Instructor nor Student


# @frappe.whitelist()
# def hire_employee(source_name):
#     """Creates an Employee Record from an Employee Applicant."""
#     # Real-time progress (Step 1/2)
#     frappe.publish_realtime(
#         "convert_to_employee_progress", {"progress": [1, 2]}, user=frappe.session.user
#     )

#     # Map Employee Applicant to Employee
#     employee = get_mapped_doc(
#         "Employee Applicant",
#         source_name,
#         {
#             "Employee Applicant": {
#                 "doctype": "Employee",
#                 "field_map": {
#                     "name": "employee_applicant",  # Special mapping
#                 },
#             }
#         },
#         ignore_permissions=True,
#     )
#     employee.save()

#     # Real-time progress (Step 2/2)
#     frappe.publish_realtime(
#         "hire_employee_progress", {"progress": [2, 2]}, user=frappe.session.user
#     )

#     return employee

# @frappe.whitelist()
# def get_student_info():
#     email = frappe.session.user
#     if email == "Administrator":
#         return
#     student_info = frappe.db.get_list(
#         "Student",
#         fields=["*"],
#         filters={"student_email_id": email},
#     )[0]

#     current_program = get_current_enrollment(student_info.name)
#     if current_program:
#         student_groups = get_student_groups(student_info.name, current_program.program)
#         student_info["student_groups"] = student_groups
        
#         # Check if there is exactly one group in student_groups
#         if len(student_groups) == 1:
#             # If yes, append the group to student_info
#             student_info["student_group"] = student_groups[0]["label"]  # Assuming 'label' is the group name
        
#         for group in student_groups:
#             print(group)  # Print all student groups for debugging
        
#         student_info["current_program"] = current_program

#     return student_info

# # @frappe.whitelist()
# # def get_student_app_data():
# #     response = {}
# #     studentID = frappe.session.user
# #     student = frappe.get_doc("Student", {"student_email_id": studentID})
# #     current_program = get_current_enrollment(student.name)
# #     student_groups = get_student_groups(student.name, current_program.program)
# #     student_group = student_groups[0]["label"]
# #     studentDetails = frappe.get_doc("Student Group Student", {"student": student.name, "parent": student_group, "active": 1})
# #     profile = student.image
# #     if profile:
# #         base64image = convert_image_to_base64(profile)
# #     notice_data = get_notice_list(student_group)
# #     response["notices"] = notice_data  # Entire notice list
# #     response["base64profile"] = base64image
# #     response["name"] = studentDetails.student_name
# #     response["group_roll_no"] = studentDetails.group_roll_number
# #     response["student_group"] = student_group
# #     parts = student_group.split('-')
# #     if len(parts) == 2:
# #         response["class"] = parts[0]
# #         response["section"] = parts[1] 
    
# #     from frappe.utils import today

# #     date = today()

# #     # Define the DocType
# #     StudentAttendance = frappe.qb.DocType("Student Attendance")

# #     # Fetch today's attendance for the student
# #     today_attendance = (
# #         frappe.qb.from_(StudentAttendance)
# #         .select(StudentAttendance.status)
# #         .where(
# #             (StudentAttendance.student == student.name)
# #             & (StudentAttendance.student_group == student_group)
# #             & (StudentAttendance.date == date)
# #         )
# #     ).run(as_dict=True)
# #     today_status = today_attendance[0]["status"] if today_attendance else "No Record"
# #     response["status"] = today_status
    
# #     all_attendance = (
# #     frappe.qb.from_(StudentAttendance)
# #     .select(StudentAttendance.status)
# #     .where(
# #         (StudentAttendance.student == student.name)
# #         & (StudentAttendance.student_group == student_group)
# #     )
# #     ).run(as_dict=True)

# #     # Initialize counts
# #     present_count = 0
# #     absent_count = 0
# #     leave_count = 0

# #     # Count statuses in all attendance records
# #     for record in all_attendance:
# #         if record["status"] == "Present":
# #             present_count += 1
# #         elif record["status"] == "Absent":
# #             absent_count += 1
# #         elif record["status"] == "Leave":
# #             leave_count += 1
            
# #     response["present_count"] = present_count
# #     response["absent_count"] = absent_count
# #     response["leave_count"] = leave_count
# #     response["mobile"] = student.student_mobile_number
# #     response["address"] = student.address_line_1
    
# #     return response

# @frappe.whitelist()
# def get_student_app_data(studentID):
#     if frappe.session.user:
#         from frappe.utils import today

#         response = {}
#         # studentID = frappe.session.user

#         try:
#             # Fetch the student document
#             student = frappe.get_doc("Student", {"student_email_id": studentID})
#             if not student:
#                 frappe.throw("Student not found")

#             # Get the current program and student group
#             current_program = get_current_enrollment(student.name)
#             student_groups = get_student_groups(student.name, current_program.program)

#             if not student_groups:
#                 frappe.throw("Student group not found")

#             student_group = student_groups[0]["label"]
#             studentDetails = frappe.get_doc("Student Group Student", {
#                 "student": student.name,
#                 "parent": student_group,
#                 "active": 1
#             })

#             # Fetch profile image as base64
#             profile = student.image
#             base64image = None
#             if profile:
#                 base64image = convert_image_to_base64(profile)

#             # Fetch notice list
#             #notice_data = get_notice_list(student_group)

#             # Add basic details to response
#             response.update({
#                 #"notices": notice_data,
#                 "base64profile": base64image,
#                 "name": studentDetails.student_name,
#                 "ID":student.name,
#                 "group_roll_no": studentDetails.group_roll_number,
#                 "student_group": student_group,
#                 "mobile": student.student_mobile_number,
#                 "address": student.address_line_1,
#             })

#             # Split student group into class and section
#             parts = student_group.split('-')
#             if len(parts) == 2:
#                 response["class"] = parts[0]
#                 response["section"] = parts[1]

#             # Attendance calculation
#             date = today()
#             StudentAttendance = frappe.qb.DocType("Student Attendance")

#             # Fetch today's attendance
#             today_attendance = (
#                 frappe.qb.from_(StudentAttendance)
#                 .select(StudentAttendance.status)
#                 .where(
#                     (StudentAttendance.student == student.name) &
#                     (StudentAttendance.student_group == student_group) &
#                     (StudentAttendance.date == date)
#                 )
#             ).run(as_dict=True)
#             today_status = today_attendance[0]["status"] if today_attendance else "No Record"
#             response["status"] = today_status

#             # Fetch all attendance records
#             all_attendance = (
#                 frappe.qb.from_(StudentAttendance)
#                 .select(StudentAttendance.status)
#                 .where(
#                     (StudentAttendance.student == student.name) &
#                     (StudentAttendance.student_group == student_group)
#                 )
#             ).run(as_dict=True)

#             # Initialize counts
#             present_count = sum(1 for record in all_attendance if record["status"] == "Present")
#             absent_count = sum(1 for record in all_attendance if record["status"] == "Absent")
#             leave_count = sum(1 for record in all_attendance if record["status"] == "Leave")

#             # Update response with attendance counts
#             response.update({
#                 "present_count": present_count,
#                 "absent_count": absent_count,
#                 "leave_count": leave_count,
#             })

#         except Exception as e:
#             frappe.log_error(message=frappe.get_traceback(), title="Error in get_student_app_data")
#             frappe.throw(f"An error occurred: {str(e)}")

#         return response
#     else:
#         return

# @frappe.whitelist()
# def get_user_details(username, role):
#     if frappe.session.user:
#         roles = frappe.get_roles(username)
#         user_details = None
#         if "Instructor" in roles and role == "teacher":
#             user_details = get_instructor_app_data(username)
#             print("hello")
#         if "Student" in roles and role == "parent":
#             user_details = get_student_app_data(username)
#             print("olleh")
        
#         print(user_details)
#         return {"roles": roles, "user_details": user_details}
#     else:
#         return
    
# @frappe.whitelist()
# def get_instructor_app_data(username):
#     """Fetch all required static data in one API call."""
#     response = {}
#     teacherID = username
#     employee = frappe.get_doc("Employee", {"user_id": teacherID})
#     teacher = frappe.get_doc("Instructor", {"employee": employee.name})
#     profile = teacher.image
#     student_group = teacher.student_group

#     # Convert the profile image to base64 if available
#     base64image = convert_image_to_base64(profile) if profile else None

#     # Parse the student group for class and section
#     parts = student_group.split('-')
#     class_name = parts[0] if len(parts) == 2 else None
#     section_name = parts[1] if len(parts) == 2 else None

#     # Add teacher info to response
#     response = {
#         "name": teacher.name,
#         "class": class_name,
#         "section": section_name,
#         "student_group": student_group,
#         "base64profile": base64image,
#     }
#     return response
#     # # Fetch attendance records
#     # attendance_data = get_student_attendance_records(based_on="Student Group", student_group=student_group)
#     # response["attendance"] = attendance_data  # Assuming the first item is the relevant data

#     # notice_data = get_notice_list(swtudent_group)
#     # response["notices"] = notice_data  # Entire notice list

#     # print(response)
#     # return response


# @frappe.whitelist()
# def get_student_attendance_records(based_on, date=None, student_group=None, course_schedule=None):
#     if frappe.session.user:
#         print("_______________",frappe.session.user)
#         # Get student group for the logged-in teacher
#         # if not student_group:
#         #     student_group = get_instructor_group()  # Get the student's group from the teacher's record
#         student_list = []

#         # THIS CODE IS NOT USED IN APP. Fetch students based on Course Schedule if provided
#         if based_on == "Course Schedule":
#             student_group = frappe.db.get_value(
#                 "Course Schedule", course_schedule, "student_group"
#             )
#             if student_group:
#                 student_list = frappe.get_all(
#                     "Student Group Student",
#                     fields=["student", "student_name", "group_roll_number"],
#                     filters={"parent": student_group, "active": 1},
#                     order_by="group_roll_number",
#                 )

#         if not student_list:
#             student_list = frappe.get_all(
#                 "Student Group Student",
#                 fields=["student", "student_name", "group_roll_number"],
#                 filters={"parent": student_group, "active": 1},
#                 order_by="group_roll_number",
#             )

#         StudentAttendance = frappe.qb.DocType("Student Attendance")

#         # THIS CODE IS NOT USED IN APP. Fetch student attendance if course_schedule is provided
#         if course_schedule:
#             student_attendance_list = (
#                 frappe.qb.from_(StudentAttendance)
#                 .select(StudentAttendance.student, StudentAttendance.status)
#                 .where((StudentAttendance.course_schedule == course_schedule))
#             ).run(as_dict=True)
#         else:
#             student_attendance_list = (
#                 frappe.qb.from_(StudentAttendance)
#                 .select(StudentAttendance.student, StudentAttendance.status)
#                 .where(
#                     (StudentAttendance.student_group == student_group)
#                     & (StudentAttendance.date == date)
#                     & (
#                         (StudentAttendance.course_schedule == "")
#                         | (StudentAttendance.course_schedule.isnull())
#                     )
#                 )
#             ).run(as_dict=True)
        

#         #This part adds todays status to the response
#         date = getdate()
#         today_attendance_list = (
#             frappe.qb.from_(StudentAttendance)
#             .select(StudentAttendance.student, StudentAttendance.status)
#             .where(
#                 (StudentAttendance.student_group == student_group)
#                 & (StudentAttendance.date == date)
#                 )
#             ).run(as_dict=True)
#         for student in student_list:
#             student_doc = frappe.get_doc("Student", {"name": student.student})
#             student.address = student_doc.address_line_1
#             student.mobile = student_doc.student_mobile_number
#             profile = student_doc.image
#             base64image = convert_image_to_base64(profile) if profile else None
#             student.base64profile = base64image
#             for attendance in today_attendance_list:
#                 if student.student == attendance.student:
#                     student.status = attendance.status



#         #This part adds present and absent count to the response
#         all_attendance_list = (
#             frappe.qb.from_(StudentAttendance)
#             .select(StudentAttendance.student, StudentAttendance.status)
#             .where(
#                 (StudentAttendance.student_group == student_group)
#             )
#         ).run(as_dict=True)
#         for student in student_list:
#             student.present_count = 0
#             student.absent_count = 0
#             student.leave_count = 0
#             for attendance in all_attendance_list:
#                 if student.student == attendance.student:
#                     if attendance.status == "Present":
#                         student.present_count += 1
#                     elif attendance.status == "Absent":
#                         student.absent_count += 1
#                     else: 
#                         student.leave_count += 1

#         print(student_list)
#         # Add student_group to the response structure
#         # response = {
#         #     "message": student_list  # Add the students below it
#         # }
#         return student_list
#     else:
#         return


# @frappe.whitelist()
# def mark_attendance(
#     students_present, students_absent, course_schedule=None, student_group=None, date=None
# ):
#     """Creates Multiple Attendance Records and sends notifications to parents.

#     :param students_present: Students Present JSON.
#     :param students_absent: Students Absent JSON.
#     :param course_schedule: Course Schedule.
#     :param student_group: Student Group.
#     :param date: Date.
#     """
#     # print(students_absent)
#     # print(students_present)
#     date = getdate()
#     if student_group:
#         academic_year = frappe.db.get_value("Student Group", student_group, "academic_year")
#         if academic_year:
#             year_start_date, year_end_date = frappe.db.get_value(
#                 "Academic Year", academic_year, ["year_start_date", "year_end_date"]
#             )
#             if getdate(date) < getdate(year_start_date) or getdate(date) > getdate(
#                 year_end_date
#             ):
#                 frappe.throw(
#                     _("Attendance cannot be marked outside of Academic Year {0}").format(academic_year)
#                 )

#     present = json.loads(students_present)
#     absent = json.loads(students_absent)

#     for d in present:
#         make_attendance_records(
#             d["student"], d["student_name"], "Present", course_schedule, student_group, date
#         )

#     student_list = []
#     for d in absent:
#         student_list.append(d["student"])
#         make_attendance_records(
#             d["student"], d["student_name"], "Absent", course_schedule, student_group, date
#         )

#     frappe.db.commit()
#     frappe.msgprint(_("Attendance has been marked successfully."))
    
#     # Send push notifications to parents of absent students
#     send_notification_to_app(student_list)


# def send_notification_to_app(student_list):
#     # Loop through the student_list
#     for student in student_list:
#         # Query the student record using the 'student' identifier
#         student_doc = frappe.get_doc("Student", {"name": student})

#         # Get the student's email or other notification details
#         student_email_id = student_doc.student_email_id

#         # If the student has an email, send a notification
#         if student_email_id:
#             # Check if a device record exists for the student (using student_email_id)
#             existing_device = frappe.get_all(
# 				"User Device", filters={"user": student_email_id}, fields=["name", "device_id"]
# 			)
#             print(existing_device)
#             if existing_device:
#                 # Extract the device ID from the first matched record
#                 device_id = existing_device[0].get("device_id")  # Using "device_id" field
#                 msg = f"Dear Parent, your child {student_doc.student_name}, is marked absent today. Please check the attendance for further details."
#                 title = "Al-Ummah Girls High School"
#                 try:
#                     if device_id:
#                         # Send a personalized and improved message to the parent
#                         from expo_push_notifier.expo_push_notifier.api import send_push_message
#                         send_push_message(device_id, title, msg)
#                         print(device_id)

#                         # Send an email notification to the parent
#                         frappe.sendmail(
#                             recipients=[student_email_id],
#                             subject="Your child was marked absent",
#                             message=msg
#                         )

#                         print(f"Push notification and email sent to {student_email_id}")
#                     else:
#                         print(f"No device ID found for {student_email_id}.")
#                 except Exception as e:
#                     print(f"Error sending notifications to {student_email_id}: {e}")
#                     continue  # Continue processing the next student if there's an error

#     return {"status": "success", "message": "Push notifications and emails sent for absent students."}


# def make_attendance_records(
# 	student, student_name, status, course_schedule=None, student_group=None, date=None
# ):
# 	"""Creates/Update Attendance Record.

# 	:param student: Student.
# 	:param student_name: Student Name.
# 	:param course_schedule: Course Schedule.
# 	:param status: Status (Present/Absent/Leave).
# 	"""
# 	student_attendance = frappe.get_doc(
# 		{
# 			"doctype": "Student Attendance",
# 			"student": student,
# 			"course_schedule": course_schedule,
# 			"student_group": student_group,
# 			"date": date,
# 		}
# 	)
# 	if not student_attendance:
# 		student_attendance = frappe.new_doc("Student Attendance")
# 	student_attendance.student = student
# 	student_attendance.student_name = student_name
# 	student_attendance.course_schedule = course_schedule
# 	student_attendance.student_group = student_group
# 	student_attendance.date = date
# 	student_attendance.status = status
# 	student_attendance.save()
# 	student_attendance.submit()


# @frappe.whitelist()
# def get_student_group():
#     email = frappe.session.user
#     if email == "Administrator":
#         return
    
#     student = frappe.get_doc("Student", {"student_email_id": email})
#     current_program = get_current_enrollment(student.name)
#     student_groups = get_student_groups(student.name, current_program.program)
#     x = []
#     x.append(student_groups[0]["label"])
#     x.append(convert_image_to_base64(student.image))
#     return x

# def get_instructor_group():
#     teacherID = frappe.session.user
#     employee = frappe.get_doc("Employee", {"user_id": teacherID})
#     teacher = frappe.get_doc("Instructor", {"employee": employee.name})
#     return teacher.student_group

# @frappe.whitelist()
# # const newLeave = reactive({
# #   student: studentInfo.name,
# #   student_name: studentInfo.student_name,
# #   from_date: '',
# #   to_date: '',
# #   reason: '',
# #   total_days: '',
# # })
# def apply_leave(leave_data, program_name):
# 	attendance_based_on_course_schedule = frappe.db.get_single_value(
# 		"Education Settings", "attendance_based_on_course_schedule"
# 	)
# 	if attendance_based_on_course_schedule:
# 		apply_leave_based_on_course_schedule(leave_data, program_name)
# 	else:
# 		apply_leave_based_on_student_group(leave_data, program_name)


# def apply_leave_based_on_student_group(leave_data, program_name):
# 	student_groups = get_student_groups(leave_data.get("student"), program_name)
# 	leave_dates = get_dates_from_timegrain(
# 		leave_data.get("from_date"), leave_data.get("to_date")
# 	)
# 	for student_group in student_groups:
# 		for leave_date in leave_dates:
# 			make_attendance_records(
# 				leave_data.get("student"),
# 				leave_data.get("student_name"),
# 				"Leave",
# 				None,
# 				student_group.get("label"),
# 				leave_date,
# 			)
               
# def get_student_groups(student, program_name):
# 	# student = 'EDU-STU-2023-00043'

# 	student_group = frappe.qb.DocType("Student Group")
# 	student_group_students = frappe.qb.DocType("Student Group Student")

# 	student_group_query = (
# 		frappe.qb.from_(student_group)
# 		.inner_join(student_group_students)
# 		.on(student_group.name == student_group_students.parent)
# 		.select((student_group_students.parent).as_("label"))
# 		.where(student_group_students.student == student)
# 		.where(student_group.program == program_name)
# 		.run(as_dict=1)
# 	)

# 	return student_group_query



# from datetime import datetime

# #FRONTEND TEST:
# # frappe.call({
# #     method: "school.al_ummah.api.submit_leave_application", // The server method you defined
# #     type: "POST", // Use POST to send data
# #     args: {
# #         student: "EDU-STU-2025-00010", // Example argument
# #         from_date: "2025-05-01", // Correct format
# #         to_date: "2025-05-02", // Correct format
# #         student_group: "FIRST-A",
# #     },
# #     callback: function(response) {
# #         if(response.message) {
# #             console.log(response.message); // Handle the response here
# #         }
# #     }
# # });

# @frappe.whitelist(allow_guest=True)
# def add_guardian_to_student(student_id, student_name, guardian_name, relation):
#     user =  frappe.session.user
#     user_roles = frappe.get_roles(user)
#     guardian_doc = frappe.new_doc("Guardian")
#     guardian_doc.guardian_name = guardian_name
#     guardian_doc.insert(ignore_permissions=True, ignore_mandatory=True)
    
#     student_doc = frappe.get_doc("Student", {"name": student_id})
#     student_guardian = student_doc.append("guardians", {})  
#     student_guardian.guardian = guardian_doc.name  
#     student_guardian.guardian_name = guardian_name 
#     student_guardian.relation = relation
#     # student_guardian.save(ignore_permissions=True)
#     student_doc.save(ignore_permissions=True)
#     frappe.db.commit() 
#     print(student_id, student_name, student_doc.name, guardian_name, relation, guardian_doc.name, user_roles)

# @frappe.whitelist(allow_guest=True)
# def submit_leave_application(student, from_date, to_date, student_group, reason, image=None):
#     if frappe.session.user:
#         # Create a new Leave Application document
#         doc = frappe.new_doc("Leave Application")
#         doc.student = student
#         doc.from_date = from_date
#         doc.to_date = to_date
#         doc.student_group = student_group
#         doc.reason = reason

#         # Insert the document to generate a valid `name` for linking
#         doc.insert(ignore_permissions=True, ignore_mandatory=True)

#         # Attach the image if provided
#         if image:
#             # Decode the base64 image string
#             image_data = base64.b64decode(image)
#             fname = "leave_application_image.jpg"  # Adjust the file name as needed

#             # Save the image file and link it to the document
#             saved_file = save_file(
#                 fname=fname,           # Corrected argument for file name
#                 content=image_data,    # File content
#                 dt="Leave Application", # Doctype
#                 dn=doc.name,           # Document name
#                 is_private=0           # Set to 1 if the file should be private
#             )
#             # Optionally, you can add the file URL to a custom field in the document
#             doc.document = saved_file.file_url

#         # Save the document after attaching the image
#         doc.save()
#         frappe.db.commit()  # Ensure the changes are committed to the database

#         return {"status": "success", "message": "Leave application submitted successfully", "docname": doc.name}
#     else:
#         return


# # @frappe.whitelist(allow_guest=True)
# # def submit_leave_application(student, from_date, to_date, student_group, document_image=None):
# #     # Convert from_date and to_date directly as datetime objects without specifying a format
# #     # from_date = datetime.strptime(from_date, "%Y-%m-%d")  # Correct format for YYYY-MM-DD
# #     # to_date = datetime.strptime(to_date, "%Y-%m-%d")  # Correct format for YYYY-MM-DD

# #     # Create a new Leave Application document
# #     doc = frappe.new_doc("Leave Application")
# #     doc.student = student
# #     doc.from_date = from_date
# #     doc.to_date = to_date
# #     doc.student_group = student_group
# #     doc.attendance_based_on = "Student Group"
# #     doc.mark_as_present = 1
# #     # Insert the new document
# #     doc.insert(ignore_permissions=True, ignore_mandatory=True)

# #     # Save the document
# #     doc.save()
# #     doc.submit()
# #     frappe.db.commit()  # Ensure data is committed to the database

# #     return {"status": "success", "message": "Leave application submitted successfully"}



# @frappe.whitelist()
# def get_current_enrollment(student, academic_year=None):
# 	current_academic_year = academic_year or frappe.defaults.get_defaults().academic_year
# 	if not current_academic_year:
# 		frappe.throw(_("Please set default Academic Year in Education Settings"))
# 	program_enrollment_list = frappe.db.sql(
# 		"""
# 		select
# 			name as program_enrollment, student_name, program, student_batch_name as student_batch,
# 			student_category, academic_term, academic_year
# 		from
# 			`tabProgram Enrollment`
# 		where
# 			student = %s and academic_year = %s
# 		order by creation""",
# 		(student, current_academic_year),
# 		as_dict=1,
# 	)

# 	if program_enrollment_list:
# 		return program_enrollment_list[0]
# 	else:
# 		return None




# # @frappe.whitelist()
# # def get_student_info():
# #     # Get the student group for the logged-in user
# #     student_group = get_student_group_by_user_id()

# #     # Get the email of the logged-in user
# #     email = frappe.session.user

# #     if email == "Administrator":
# #         return

# #     # Fetch the student information
# #     student_info = frappe.db.get_list(
# #         "Student",
# #         fields=["*"],
# #         filters={"student_email_id": email},
# #     )[0]

# #     # Fetch the current enrollment and student groups
# #     current_program = get_current_enrollment(student_info["name"])
# #     if current_program:
# #         student_groups = get_student_groups(student_info["name"], current_program["program"])
# #         student_info["student_groups"] = student_groups
# #         student_info["current_program"] = current_program

# #     # Inject the student group into the response
# #     student_info["student_group"] = student_group

# #     # Return the complete student information
# #     return student_info


# # from datetime import datetime

# # @frappe.whitelist()
# # def get_student_group_by_user_id():
# #     # Step 1: Get the current year
# #     current_year = str(datetime.now().year)

# #     # Step 2: Get the email of the logged-in user
# #     user_id = frappe.session.user

# #     # Step 3: Fetch the student ID associated with this email
# #     student_info = frappe.get_all(
# #         "Student",
# #         fields=["name"],  # We only need the student ID
# #         filters={"student_email_id": user_id}
# #     )

# #     if student_info:
# #         student_id = student_info[0]["name"]

# #         # Step 4: Fetch all student groups for the student, filtering by the current year's batch
# #         student_group_entries = frappe.get_all(
# #             "Student Group Student",
# #             fields=["parent"],  # Only fetch the group name (parent)
# #             filters={"student": student_id},  # Filter by student ID
# #         )

# #         # Filter the groups by batch year from the parent (Student Group) records
# #         current_year_groups = [
# #             entry["parent"]
# #             for entry in student_group_entries
# #             if frappe.db.get_value("Student Group", entry["parent"], "batch") == current_year
# #         ]

# #         # Check if there is exactly one record
# #         if len(current_year_groups) == 1:
# #             group_name = current_year_groups[0]  # Extract the single group name
# #             return group_name
# #         elif len(current_year_groups) > 1:
# #             return {"status": "error", "message": "Multiple groups found for the given user ID in the current year"}
    
# #     # Return an error if no group or student is found
# #     return {"status": "error", "message": "No group found for the given user ID in the current year"}



# #INSTRUCTOR
# import frappe
# import requests
# import base64
# from io import BytesIO

# @frappe.whitelist()
# def get_leave_application(name):
#     try:
#         # Fetch the Leave Application document based on student group and student
#         leave = frappe.get_doc(
#             "Leave Application",  # The Doctype
#             {   
#                 "name": name,
#                 # "student_group": student_group,
#                 # "mark_as_present": 0,
#                 # "student": student,
#                 # "from_date": from_date,
#                 # "to_date": to_date
#             }
#         )

#         # Extract the required fields
#         leave_data = {
#             "document": leave.document,
#             # "student": leave.student,
#             # "student_name": leave.student_name,
#             # "from_date": leave.from_date,
#             # "to_date": leave.to_date,
#             # "total_leave_days": leave.total_leave_days,
#             # "reason": leave.reason
#         }

#         # If the document exists, convert it to base64
#         if leave.document:
#             leave_data["document_base64"] = convert_image_to_base64(leave.document)

#         return leave_data

#     except frappe.DoesNotExistError:
#         # Handle case where document is not found
#         return {"message": "Leave application not found for the specified student and group."}

# @frappe.whitelist()
# def get_leave_application_list(student_group, student=None):
#     if frappe.session.user:
#         # If a student is specified, return the leave application for that student
#         if student:
#             return get_leave_application(student_group, student)
        
#         # Fetch all leave applications for the given student group
#         leave_list = frappe.get_all(
#             "Leave Application",
#             fields=["name", "student", "student_name", "from_date", "to_date", "total_leave_days", "reason", "document"],
#             filters={"student_group": student_group, "mark_as_present": 0}
#         )
        
#         # Convert image URLs to base64
#         for leave in leave_list:
#             if leave.get("document"):
#                 image_url = leave["document"]
#                 leave["document_base64"] = convert_image_to_base64(image_url)
#         print(leave_list)
#         return leave_list
#     else:
#         return

# def convert_image_to_base64(image_url):
#     # Check if the URL is relative (doesn't contain a scheme like http:// or https://)
#     if not image_url.startswith('http'):
#         base_url = 'http://edu.school:8000'
#         image_url = base_url + image_url
    
#     # Now perform the request
#     response = requests.get(image_url)
    
#     if response.status_code == 200:
#         image_bytes = BytesIO(response.content)
#         base64_image = base64.b64encode(image_bytes.read()).decode('utf-8')
#         return base64_image
#     else:
#         return None


# #student_group, student, from_date, to_date, status
# @frappe.whitelist()
# def update_leave_status(name, status):
#     if frappe.session.user:
#         try:
#             # Get the leave application document for the given student and group
#             leave = frappe.get_doc(
#                 "Leave Application",  # The Doctype
#                 {
#                     "name": name,
#                     # "student_group": student_group,
#                     # "student": student,
#                     # "from_date": from_date,
#                     # "to_date": to_date
#                 }
#             )

#             if not leave:
#                 # Handle case where the document does not exist
#                 return {"message": "Leave application not found for the specified student and group."}

#             # If status is approved, mark the student as present
#             if status == "approved":
#                 leave.mark_as_present = 1
#             elif status == "rejected":
#                 print(leave)
#                 leave.delete()
#                 frappe.db.commit()
#                 print(leave)
#             # Save the changes and commit them to the database
#             leave.save()
#             leave.submit()
#             frappe.db.commit()
            
#             # Return success message
#             return {"message": "Leave status updated successfully."}

#         except Exception as e:
#             # Catch any other exceptions and return the error message
#             return {"message": f"An error occurred: {str(e)}"}
#     else:
#         return

# @frappe.whitelist(allow_guest=True)
# def submit_notice(notice_heading, notice_message, student_group):
#     if frappe.session.user:
#         print(notice_heading, notice_message, student_group)
#         student_list = frappe.get_all(
#             "Student Group Student",
#             fields=["student", "student_name", "group_roll_number"],
#             filters={"parent": student_group, "active": 1},
#             order_by="group_roll_number",
#         )
#         send_notice_notification_to_app(student_list, notice_heading, notice_message)
#         try:
#             if not notice_heading or not notice_message:
#                 return {"status": "error", "message": "Both title and message are required."}

#             # Create a new Leave Application document
#             teacherID = frappe.session.user
#             employee = frappe.get_doc("Employee", {"user_id": teacherID})
#             teacher = frappe.get_doc("Instructor", {"employee": employee.name})
#             doc = frappe.new_doc("Student Notice")
#             doc.notice_heading = notice_heading
#             doc.notice_message = notice_message
#             doc.date = getdate()
#             doc.instructor = teacher.instructor_name
#             doc.student_group = teacher.student_group

#             # Insert the document to generate a valid `name` for linking
#             doc.insert(ignore_permissions=True)
#             # Save the document after attaching the image
#             doc.save()
#             frappe.db.commit()  # Ensure the changes are committed to the database

#             # Ensure the message is a string
#             return {"status": "success", "message": str("Notice created successfully")}
#         except Exception as e:
#             # Return the error message as a string
#             return {"status": "error", "message": str(e)}
#     else:
#         return
    
# def send_notice_notification_to_app(student_list, notice_heading, notice_message):
#     # Loop through the student_list
#     for student in student_list:
#         # Query the student record using the 'student' identifier
#         student_doc = frappe.get_doc("Student", {"name": student["student"]})

#         # Get the student's email or other notification details
#         student_email_id = student_doc.student_email_id

#         # If the student has an email, send a notification
#         if student_email_id:
#             # Check if a device record exists for the student (using student_email_id)
#             existing_device = frappe.get_all(
#                 "User Device", filters={"user": student_email_id}, fields=["name", "device_id"]
#             )
#             print(existing_device)
#             if existing_device:
#                 # Extract the device ID from the first matched record
#                 device_id = existing_device[0].get("device_id")  # Using "device_id" field
#                 msg = f"Dear Parent, a new notice titled '{notice_heading}' has been posted for your child {student_doc.student_name}. {notice_message}"
#                 title = f"Notice: {notice_heading}"  # Use the heading as the title
#                 try:
#                     if device_id:
#                         # Send a personalized and improved message to the parent
#                         from expo_push_notifier.expo_push_notifier.api import send_push_message
#                         send_push_message(device_id, title, msg)
#                         print(device_id)

#                         # Send an email notification to the parent
#                         frappe.sendmail(
#                             recipients=[student_email_id],
#                             subject=f"Notice: {notice_heading}",
#                             message=msg
#                         )

#                         print(f"Push notification and email sent to {student_email_id}")
#                     else:
#                         print(f"No device ID found for {student_email_id}.")
#                 except Exception as e:
#                     print(f"Error sending notifications to {student_email_id}: {e}")
#                     continue  # Continue processing the next student if there's an error

#     return {"status": "success", "message": "Push notifications and emails sent for the notice."}


# @frappe.whitelist()
# def get_notice_list(student_group):
#     if frappe.session.user:
#         # Fetch all leave applications for the given student group
#         notice_list = frappe.get_all(
#             "Student Notice",
#             fields=["name", "notice_heading", "notice_message", "date"],
#             filters={"student_group": student_group}
#         )
#         print(notice_list)
#         return notice_list
#     else:
#         return

# @frappe.whitelist()
# def delete_notice(name):
#     if frappe.session.user:
#         # Fetch all leave applications for the given student group
#         notice = frappe.get_doc(
#             "Student Notice",
#             {"name": name}
#         )
#         notice.delete()
#         frappe.db.commit()
#     else:
#         return
    

