import frappe

def search_by_student_name():
    """Search for students and check their enrollments by name"""
    
    student_name = "AAHIRA SAJJAD MOGAR"  # The first student from your list
    
    print("=== SEARCHING BY STUDENT NAME ===")
    print(f"Searching for student: {student_name}")
    
    # 1. Find the student by name
    students = frappe.get_all(
        "Student",
        filters={"student_name": ["like", f"%{student_name}%"]},
        fields=["name", "student_name"]
    )
    
    print(f"\n1. Found {len(students)} students with similar names:")
    for student in students:
        print(f"   - {student['name']}: {student['student_name']}")
    
    if not students:
        print("   No students found with that name!")
        return
    
    # 2. Check course enrollments for each found student (with correct fields)
    target_student = students[0]  # Use the first match
    print(f"\n2. Checking enrollments for: {target_student['student_name']} ({target_student['name']})")
    
    enrollments = frappe.get_all(
        "Course Enrollment",
        filters={"student": target_student["name"], "docstatus": 1},
        fields=["course", "program"]  # Only fields that exist
    )
    
    print(f"   Found {len(enrollments)} enrollments:")
    for enroll in enrollments:
        print(f"     - Course: {enroll['course']}, Program: {enroll['program']}")
    
    # 3. Check ALL enrollments in system to see structure
    print(f"\n3. Checking ALL Course Enrollment records in system...")
    all_enrollments = frappe.get_all(
        "Course Enrollment",
        fields=["name", "student", "course", "program", "docstatus"],
        limit=10
    )
    
    print(f"   Total records found: {len(all_enrollments)}")
    for enroll in all_enrollments:
        student_name = frappe.db.get_value("Student", enroll["student"], "student_name")
        print(f"     - Student: {enroll['student']} ({student_name}), Course: {enroll['course']}, Status: {enroll['docstatus']}")
    
    # 4. Check if there are ANY enrollments with docstatus=0 (draft)
    print(f"\n4. Checking DRAFT enrollments (docstatus=0)...")
    draft_enrollments = frappe.get_all(
        "Course Enrollment", 
        filters={"docstatus": 0},
        fields=["student", "course"],
        limit=5
    )
    print(f"   Draft enrollments found: {len(draft_enrollments)}")
    for enroll in draft_enrollments:
        print(f"     - Student: {enroll['student']}, Course: {enroll['course']}")
    
    # 5. Check what fields actually exist in Course Enrollment
    print(f"\n5. Checking Course Enrollment doctype structure...")
    docfields = frappe.get_meta("Course Enrollment").get("fields")
    field_names = [df.fieldname for df in docfields]
    print(f"   Available fields: {field_names}")

def check_all_student_enrollments():
    """Check enrollments for all students in the 1st-A group"""
    
    student_group = "1st-A (2025-26)"
    
    print(f"\n=== CHECKING ALL STUDENTS IN {student_group} ===")
    
    # Get all students in the group
    students = frappe.get_all(
        "Student Group Student",
        filters={"parent": student_group, "active": 1},
        fields=["student", "student_name", "group_roll_number"],
        order_by="group_roll_number"
    )
    
    print(f"Found {len(students)} students in group")
    
    students_with_enrollments = 0
    
    for student in students[:10]:  # Check first 10 students
        enrollments = frappe.get_all(
            "Course Enrollment",
            filters={"student": student["student"], "docstatus": 1},
            fields=["course"]
        )
        
        if enrollments:
            students_with_enrollments += 1
            print(f"✓ {student['student_name']} (Roll: {student['group_roll_number']}) - {len(enrollments)} enrollments")
            for enroll in enrollments:
                print(f"    - {enroll['course']}")
        else:
            print(f"✗ {student['student_name']} (Roll: {student['group_roll_number']}) - NO enrollments")
    
    print(f"\n=== SUMMARY ===")
    print(f"Students checked: 10")
    print(f"Students with Course Enrollment records: {students_with_enrollments}")
    print(f"Students without Course Enrollment records: {10 - students_with_enrollments}")
    
    if students_with_enrollments == 0:
        print(f"\n🚨 CONFIRMED: NO COURSE ENROLLMENT RECORDS EXIST!")
        print("This is why the 'courses' array is always empty.")
        print("\nSOLUTION: You need to create Course Enrollment records for these students.")
        print("They should be enrolled in: Math (1st), English (1st), Science (1st)")

def create_missing_enrollments():
    """Create Course Enrollment records for students"""
    
    student_group = "1st-A (2025-26)"
    program = "1st"
    
    print("=== CREATING MISSING COURSE ENROLLMENTS ===")
    
    # Get program courses
    program_courses = frappe.get_all(
        "Program Course",
        filters={"parent": program},
        fields=["course", "course_name"]
    )
    
    print(f"Program courses: {[c['course'] for c in program_courses]}")
    
    # Get students in the group
    students = frappe.get_all(
        "Student Group Student",
        filters={"parent": student_group, "active": 1},
        fields=["student", "student_name"]
    )
    
    print(f"Students to enroll: {len(students)}")
    
    created_count = 0
    
    for student in students:
        for course in program_courses:
            # Check if enrollment already exists
            exists = frappe.db.exists("Course Enrollment", {
                "student": student["student"],
                "course": course["course"],
                "program": program,
                "docstatus": 1
            })
            
            if not exists:
                try:
                    # Create new enrollment
                    enrollment = frappe.new_doc("Course Enrollment")
                    enrollment.student = student["student"]
                    enrollment.course = course["course"]
                    enrollment.program = program
                    enrollment.enrollment_date = frappe.utils.nowdate()
                    enrollment.submit()  # This sets docstatus=1
                    
                    created_count += 1
                    print(f"✓ Created: {student['student_name']} -> {course['course_name']}")
                    
                except Exception as e:
                    print(f"✗ Error creating enrollment for {student['student_name']}: {e}")
    
    print(f"\n=== COMPLETED ===")
    print(f"Created {created_count} new Course Enrollment records")
    print(f"Students should now have courses in the Remove Courses page!")

if __name__ == "__main__":
    search_by_student_name()
    check_all_student_enrollments()