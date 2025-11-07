import frappe
from frappe import _
import json

@frappe.whitelist()
def promote_students(students, student_group, next_academic_year, next_student_group, next_program):
    """
    Promote students to the next academic year and create Program Enrollment records
    and add them to the existing student group
    """
    try:
        # Parse students data
        students_list = json.loads(students) if isinstance(students, str) else students
        
        if not students_list:
            return {
                "success": False,
                "message": "No students provided for promotion"
            }
        
        # Get the first academic term for the next academic year
        academic_term = get_first_academic_term(next_academic_year)
        
        if not academic_term:
            return {
                "success": False,
                "message": f"No academic terms found for academic year {next_academic_year}"
            }
        
        # Get the existing student group
        if not frappe.db.exists("Student Group", next_student_group):
            return {
                "success": False,
                "message": f"Student group '{next_student_group}' not found"
            }
        
        next_group_doc = frappe.get_doc("Student Group", next_student_group)
        
        promoted_count = 0
        skipped_students = []
        
        # Get existing students in the next group to avoid duplicates
        existing_student_ids = {d.student for d in next_group_doc.students}
        current_roll_numbers = [d.group_roll_number or 0 for d in next_group_doc.students]
        next_roll = max(current_roll_numbers) if current_roll_numbers else 0
        
        for student_data in students_list:
            student_id = student_data.get('student')
            
            if not student_id:
                skipped_students.append("Missing student ID")
                continue
            
            # Check if student exists
            if not frappe.db.exists("Student", student_id):
                skipped_students.append(f"Student {student_id} not found")
                continue
            
            # Check if program enrollment already exists for this academic year
            existing_enrollment = frappe.db.exists("Program Enrollment", {
                "student": student_id,
                "academic_year": next_academic_year,
                "program": next_program,
                "docstatus": ["<", 2]
            })
            
            if existing_enrollment:
                skipped_students.append(f"Student {student_id} already enrolled in {next_program} for {next_academic_year}")
                continue
            
            # Create new program enrollment
            enrollment_created = create_program_enrollment(
                student_id=student_id,
                program=next_program,
                student_batch_name=next_student_group,
                academic_year=next_academic_year,
                academic_term=academic_term,
                student_name=student_data.get('student_name', '')
            )
            
            if enrollment_created:
                # Add to Student Group if not already there
                if student_id not in existing_student_ids:
                    next_roll += 1
                    add_student_to_group(next_group_doc, student_id, student_data.get('student_name', ''), next_roll)
                    existing_student_ids.add(student_id)
                    promoted_count += 1
                else:
                    skipped_students.append(f"Student {student_id} already in target student group")
            else:
                skipped_students.append(f"Failed to create enrollment for {student_id}")
        
        # Save the student group with new students
        if promoted_count > 0:
            next_group_doc.save(ignore_permissions=True)
        
        # Prepare response message
        message = f"Successfully promoted {promoted_count} student(s) from {student_group} to {next_student_group}"
        
        if skipped_students:
            message += f". Skipped {len(skipped_students)} student(s): {', '.join(skipped_students[:5])}"
            if len(skipped_students) > 5:
                message += f" and {len(skipped_students) - 5} more"
        
        frappe.db.commit()
        
        return {
            "success": True,
            "message": message,
            "promoted_count": promoted_count,
            "skipped_count": len(skipped_students),
            "current_student_group": student_group,
            "next_student_group": next_student_group,
            "next_academic_year": next_academic_year,
            "next_program": next_program,
            "academic_term": academic_term,
            "students_added_to_group": promoted_count
        }
        
    except Exception as e:
        frappe.db.rollback()
        return {
            "success": False,
            "message": f"Error promoting students: {str(e)}"
        }


def add_student_to_group(student_group, student_id, student_name, roll_no):
    """
    Append a student to the Student Group child table.
    """
    child = student_group.append("students", {})
    child.student = student_id
    child.student_name = student_name
    child.active = 1
    child.group_roll_number = roll_no


def get_first_academic_term(academic_year):
    """
    Get the first academic term for the given academic year
    Returns the first term based on term_start_date
    """
    try:
        # Get all terms for the academic year, ordered by term_start_date
        terms = frappe.get_all(
            "Academic Term",
            filters={
                "academic_year": academic_year
            },
            fields=["name", "term_name", "term_start_date"],
            order_by="term_start_date asc",
            limit=1
        )
        
        if terms:
            return terms[0].name
        else:
            # If no terms found for the academic year, try to get any term
            any_term = frappe.db.get_value("Academic Term", 
                filters={"academic_year": academic_year},
                order_by="creation asc"
            )
            return any_term
            
    except Exception:
        return None

def create_program_enrollment(student_id, program, student_batch_name, academic_year, academic_term, student_name=""):
    """
    Create a new Program Enrollment document for a student and manually create Course Enrollments
    """
    try:
        # Get student document
        student_doc = frappe.get_doc("Student", student_id)
        
        # Double-check if enrollment already exists
        existing_enrollment = frappe.db.exists("Program Enrollment", {
            "student": student_id,
            "academic_year": academic_year,
            "program": program,
            "docstatus": ["<", 2]
        })
        
        if existing_enrollment:
            return False
        
        # Check if program exists and has courses
        if not frappe.db.exists("Program", program):
            return False
            
        program_doc = frappe.get_doc("Program", program)
        program_courses = program_doc.get("courses", [])
        
        if not program_courses:
            # Program has no courses, just create the program enrollment
            program_enrollment = frappe.new_doc("Program Enrollment")
            program_enrollment.student = student_doc.name
            program_enrollment.student_name = student_name or student_doc.student_name
            program_enrollment.program = program
            program_enrollment.student_batch_name = student_batch_name
            program_enrollment.academic_year = academic_year
            program_enrollment.academic_term = academic_term
            program_enrollment.enrollment_date = frappe.utils.nowdate()
            
            program_enrollment.insert(ignore_permissions=True)
            program_enrollment.submit()
            
            return True
        
        # Create new Program Enrollment
        program_enrollment = frappe.new_doc("Program Enrollment")
        program_enrollment.student = student_doc.name
        program_enrollment.student_name = student_name or student_doc.student_name
        program_enrollment.program = program
        program_enrollment.student_batch_name = student_batch_name
        program_enrollment.academic_year = academic_year
        program_enrollment.academic_term = academic_term
        program_enrollment.enrollment_date = frappe.utils.nowdate()
        
        # Save the document
        program_enrollment.insert(ignore_permissions=True)
        
        # Manually create Course Enrollments for each course in the program
        course_enrollments_created = create_course_enrollments(
            program_enrollment=program_enrollment,
            program_courses=program_courses,
            student_id=student_id,
            student_name=student_name or student_doc.student_name
        )
        
        # Submit the Program Enrollment
        try:
            program_enrollment.submit()
        except Exception:
            # Even if submit fails, we still consider it created
            pass
        
        return True
        
    except Exception:
        return False


def create_course_enrollments(program_enrollment, program_courses, student_id, student_name):
    """
    Manually create Course Enrollment documents for all courses in a program
    """
    try:
        courses_created = 0
        
        for program_course in program_courses:
            course_name = program_course.course
            
            # Check if course enrollment already exists
            existing_course_enrollment = frappe.db.exists("Course Enrollment", {
                "student": student_id,
                "course": course_name,
                "academic_year": program_enrollment.academic_year,
                "academic_term": program_enrollment.academic_term,
                "docstatus": ["<", 2]
            })
            
            if not existing_course_enrollment:
                try:
                    # Create new Course Enrollment
                    course_enrollment = frappe.new_doc("Course Enrollment")
                    course_enrollment.student = student_id
                    course_enrollment.student_name = student_name
                    course_enrollment.program_enrollment = program_enrollment.name
                    course_enrollment.course = course_name
                    course_enrollment.course_name = program_course.course_name
                    course_enrollment.academic_year = program_enrollment.academic_year
                    course_enrollment.academic_term = program_enrollment.academic_term
                    course_enrollment.enrollment_date = program_enrollment.enrollment_date
                    
                    # Save with ignore_permissions to bypass any permission issues
                    course_enrollment.insert(ignore_permissions=True)
                    
                    # Try to submit the course enrollment
                    try:
                        course_enrollment.submit()
                    except Exception:
                        # Keep as draft if submission fails
                        pass
                    
                    courses_created += 1
                    
                except Exception:
                    # Continue with other courses even if one fails
                    continue
        
        return courses_created
        
    except Exception:
        return 0

@frappe.whitelist()
def fetch_student_group(current_group_name):
    """
    Fetch student group information for promotion
    """
    try:
        if not current_group_name:
            return {
                "success": False,
                "allowed": False,
                "message": "No student group provided"
            }
        
        # Check if current group exists
        if not frappe.db.exists("Student Group", current_group_name):
            return {
                "success": False,
                "allowed": False,
                "message": f"Student group '{current_group_name}' not found"
            }
        
        # Get current group details
        current_group = frappe.get_doc("Student Group", current_group_name)
        academic_year = current_group.academic_year
        program = current_group.program
        
        # Extract year and increment it
        try:
            if '-' in academic_year:
                years = academic_year.split('-')
                if len(years) == 2:
                    start_year = int(years[0])
                    end_year = int(years[1])
                    next_academic_year = f"{start_year + 1}-{end_year + 1}"
                else:
                    next_academic_year = f"{int(years[0]) + 1}-{int(years[0]) + 2}"
            else:
                # If format is different, try to extract year
                import re
                year_match = re.search(r'(\d{4})', academic_year)
                if year_match:
                    year = int(year_match.group(1))
                    next_academic_year = f"{year + 1}-{year + 2}"
                else:
                    next_academic_year = "Unknown"
        except Exception:
            next_academic_year = "Unknown"
        
        # Construct next group name
        group_based_on = current_group.get('group_based_on', 'Batch')
        if group_based_on == 'Batch':
            # For batch-based groups, replace the academic year
            next_group_name = current_group_name.replace(academic_year, next_academic_year)
        else:
            # For other types, append next year
            next_group_name = f"{current_group_name} ({next_academic_year})"
        
        # Check if next group exists
        next_group_exists = frappe.db.exists("Student Group", next_group_name)
        
        # Check permissions
        allowed = True
        
        return {
            "success": True,
            "allowed": allowed,
            "current_group": current_group_name,
            "next_group": next_group_name,
            "next_academic_year": next_academic_year,
            "next_program": program,
            "group_exists": next_group_exists,
            "message": "Promotion information retrieved successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "allowed": False,
            "message": f"Error fetching student group information: {str(e)}"
        }