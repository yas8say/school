import frappe
import json
from education.education.doctype.fee_structure.fee_structure import make_fee_schedule, get_amount_distribution_based_on_fee_plan
from frappe.utils import nowdate

@frappe.whitelist()
def create_and_submit_fee_schedules_with_invoices(fee_structure_name, student_groups, fee_plan, due_dates=None):
    """
    Create and submit fee schedules, then create and submit sales invoices/orders for all students
    Accepts lists of student groups and optional due dates
    """
    try:
        # Validate input parameters
        if not all([fee_structure_name, student_groups, fee_plan]):
            return {
                "success": False,
                "message": "Fee Structure Name, Student Groups, and Fee Plan are required"
            }

        # Validate student_groups is a list
        if isinstance(student_groups, str):
            student_groups = json.loads(student_groups)
        
        if not isinstance(student_groups, list):
            return {
                "success": False,
                "message": "Student Groups must be a list"
            }

        # Validate due_dates if provided
        if due_dates and isinstance(due_dates, str):
            due_dates = json.loads(due_dates)
        
        if due_dates and not isinstance(due_dates, list):
            return {
                "success": False,
                "message": "Due Dates must be a list"
            }

        # Validate fee plan
        valid_fee_plans = ["Monthly", "Quarterly", "Semi-Annually", "Annually", "Term-Wise"]
        if fee_plan not in valid_fee_plans:
            return {
                "success": False,
                "message": f"Invalid fee plan. Must be one of: {', '.join(valid_fee_plans)}"
            }

        # Validate fee structure exists
        if not frappe.db.exists("Fee Structure", fee_structure_name):
            return {
                "success": False,
                "message": f"Fee Structure {fee_structure_name} not found"
            }

        # Validate all student groups exist
        for student_group in student_groups:
            if not frappe.db.exists("Student Group", student_group):
                return {
                    "success": False,
                    "message": f"Student Group {student_group} not found"
                }

        # Step 1: Create and submit fee schedules
        created_schedules = create_and_submit_fee_schedules(fee_structure_name, student_groups, fee_plan, due_dates)
        
        if not created_schedules:
            return {
                "success": False,
                "message": "No fee schedules were created"
            }

        # Step 2: Create and submit sales invoices for all submitted fee schedules
        invoice_results = []
        for schedule_name in created_schedules:
            result = create_and_submit_sales_invoices_for_schedule(schedule_name)
            invoice_results.append({
                "fee_schedule": schedule_name,
                "result": result
            })

        return {
            "success": True,
            "message": f"Successfully created {len(created_schedules)} fee schedules and corresponding sales documents",
            "fee_plan": fee_plan,
            "fee_schedules": created_schedules,
            "invoice_results": invoice_results
        }

    except Exception as e:
        frappe.log_error(f"Fee Schedule and Invoice Creation Error: {str(e)}")
        return {
            "success": False,
            "message": f"Process failed: {str(e)}"
        }


def create_and_submit_fee_schedules(fee_structure_name, student_groups, fee_plan, due_dates=None):
    """Create fee schedules and return list of created schedule names"""
    try:
        fs = frappe.get_doc("Fee Structure", fee_structure_name)

        components_json = json.dumps([
            {
                "fees_category": comp.fees_category,
                "total": comp.total,
                "amount": comp.amount,
                "discount": comp.discount
            }
            for comp in fs.components
        ])

        distribution_data = get_amount_distribution_based_on_fee_plan(
            components=components_json,
            total_amount=fs.total_amount,
            fee_plan=fee_plan,
            academic_year=fs.academic_year
        )

        # Prepare student groups in required format
        student_groups_formatted = [{"student_group": sg} for sg in student_groups]
        
        # If custom due dates are provided, use them instead of the distribution data
        if due_dates:
            # Validate due dates match distribution count
            if len(due_dates) != len(distribution_data["distribution"]):
                frappe.throw(f"Number of due dates ({len(due_dates)}) must match number of distributions ({len(distribution_data['distribution'])})")
            
            # Replace due dates in distribution
            for i, distribution in enumerate(distribution_data["distribution"]):
                if i < len(due_dates):
                    distribution["due_date"] = due_dates[i]

        result = make_fee_schedule(
            source_name=fee_structure_name,
            dialog_values=json.dumps({
                "fee_plan": fee_plan,
                "distribution": distribution_data["distribution"],
                "student_groups": student_groups_formatted
            }),
            per_component_amount=json.dumps(distribution_data["per_component_amount"]),
            total_amount=fs.total_amount
        )
        
        # Submit and return the created schedule names
        submitted_schedules = submit_recent_fee_schedules(fee_structure_name, result)
        return submitted_schedules

    except Exception as e:
        frappe.log_error(f"Fee Schedule Creation Error: {str(e)}")
        return []


def submit_recent_fee_schedules(fee_structure_name, expected_count):
    """Submit fee schedules and return list of submitted schedule names"""
    schedules = frappe.get_all(
        "Fee Schedule",
        filters={"fee_structure": fee_structure_name, "docstatus": 0},
        order_by="creation DESC",
        limit=expected_count
    )

    submitted_schedules = []
    for sc in schedules:
        try:
            doc = frappe.get_doc("Fee Schedule", sc.name)
            doc.submit()
            submitted_schedules.append(sc.name)
        except Exception as e:
            frappe.log_error(f"Failed to submit Fee Schedule {sc.name}: {str(e)}")
    
    return submitted_schedules


def create_and_submit_sales_invoices_for_schedule(fee_schedule_name):
    """Create and submit sales invoices for a given fee schedule"""
    try:
        # Get the fee schedule document
        fee_schedule = frappe.get_doc("Fee Schedule", fee_schedule_name)
        
        # Check Education Settings to see if we should create Sales Orders instead
        create_so = frappe.db.get_single_value("Education Settings", "create_so")
        
        if create_so:
            result = create_and_submit_sales_orders_for_schedule(fee_schedule_name)
        else:
            result = create_and_submit_sales_invoices_for_schedule_backend(fee_schedule_name)
        
        return result
        
    except Exception as e:
        frappe.log_error(f"Sales Document Creation Error for {fee_schedule_name}: {str(e)}")
        return {"success": False, "message": str(e)}


def create_and_submit_sales_invoices_for_schedule_backend(fee_schedule_name):
    """Backend logic to create and submit sales invoices"""
    try:
        # Set status to "In Process"
        frappe.db.set_value("Fee Schedule", fee_schedule_name, "status", "In Process")
        
        # Get all students from the fee schedule's student groups
        fee_schedule = frappe.get_doc("Fee Schedule", fee_schedule_name)
        total_records = sum([int(d.total_students) for d in fee_schedule.student_groups])
        created_records = 0
        submitted_invoices = []
        
        # Process each student group
        for student_group in fee_schedule.student_groups:
            students = get_students_from_group(
                student_group.student_group,
                fee_schedule.academic_year,
                fee_schedule.academic_term,
                fee_schedule.student_category
            )
            
            # Create and submit sales invoice for each student
            for student in students:
                try:
                    invoice_name = create_and_submit_single_sales_invoice(fee_schedule_name, student.student)
                    created_records += 1
                    submitted_invoices.append(invoice_name)
                except Exception as e:
                    frappe.log_error(f"Failed to create invoice for student {student.student}: {str(e)}")
        
        # Update fee schedule status
        frappe.db.set_value("Fee Schedule", fee_schedule_name, "status", "Invoice Created")
        
        return {
            "success": True,
            "created_count": created_records,
            "total_students": total_records,
            "submitted_invoices": submitted_invoices
        }
        
    except Exception as e:
        # Mark as failed in case of error
        frappe.db.set_value("Fee Schedule", fee_schedule_name, "status", "Failed")
        frappe.db.set_value("Fee Schedule", fee_schedule_name, "error_log", str(e))
        return {"success": False, "message": str(e)}


def create_and_submit_sales_orders_for_schedule(fee_schedule_name):
    """Create and submit sales orders instead of invoices"""
    try:
        fee_schedule = frappe.get_doc("Fee Schedule", fee_schedule_name)
        frappe.db.set_value("Fee Schedule", fee_schedule_name, "status", "In Process")
        
        total_records = sum([int(d.total_students) for d in fee_schedule.student_groups])
        created_records = 0
        submitted_orders = []
        
        for student_group in fee_schedule.student_groups:
            students = get_students_from_group(
                student_group.student_group,
                fee_schedule.academic_year,
                fee_schedule.academic_term,
                fee_schedule.student_category
            )
            
            for student in students:
                try:
                    order_name = create_and_submit_single_sales_order(fee_schedule_name, student.student)
                    created_records += 1
                    submitted_orders.append(order_name)
                except Exception as e:
                    frappe.log_error(f"Failed to create sales order for {student.student}: {str(e)}")
        
        frappe.db.set_value("Fee Schedule", fee_schedule_name, "status", "Order Created")
        
        return {
            "success": True,
            "created_count": created_records,
            "total_students": total_records,
            "submitted_orders": submitted_orders
        }
        
    except Exception as e:
        frappe.db.set_value("Fee Schedule", fee_schedule_name, "status", "Failed")
        frappe.db.set_value("Fee Schedule", fee_schedule_name, "error_log", str(e))
        return {"success": False, "message": str(e)}


def create_and_submit_single_sales_invoice(fee_schedule_name, student_id):
    """Create and submit a single sales invoice for a student"""
    from education.education.doctype.fee_schedule.fee_schedule import create_sales_invoice
    
    # Create the sales invoice
    invoice_name = create_sales_invoice(fee_schedule_name, student_id)
    
    # Submit the sales invoice
    if invoice_name:
        invoice_doc = frappe.get_doc("Sales Invoice", invoice_name)
        invoice_doc.submit()
    
    return invoice_name


def create_and_submit_single_sales_order(fee_schedule_name, student_id):
    """Create and submit a single sales order for a student"""
    from education.education.doctype.fee_schedule.fee_schedule import create_sales_order
    
    # Create the sales order
    order_name = create_sales_order(fee_schedule_name, student_id)
    
    # Submit the sales order
    if order_name:
        order_doc = frappe.get_doc("Sales Order", order_name)
        order_doc.submit()
    
    return order_name


def get_students_from_group(student_group, academic_year, academic_term=None, student_category=None):
    """Get students from a student group"""
    conditions = ""
    if student_category:
        conditions = f" and pe.student_category={frappe.db.escape(student_category)}"
    if academic_term:
        conditions += f" and pe.academic_term={frappe.db.escape(academic_term)}"
    
    students = frappe.db.sql(f"""
        select pe.student, pe.student_name, pe.program, pe.student_batch_name, pe.name as enrollment
        from `tabStudent Group Student` sgs, `tabProgram Enrollment` pe
        where
            pe.docstatus = 1 and pe.student = sgs.student and pe.academic_year = %s
            and sgs.parent = %s and sgs.active = 1
            {conditions}
        """, (academic_year, student_group), as_dict=1)
    
    return students

#____________________________________________

@frappe.whitelist()
def get_fee_structures_for_selection(program=None):
    """Get list of fee structures for frontend selection, optionally filtered by program"""
    try:
        # Build filters
        filters = {"docstatus": 1}
        
        # Add program filter if provided
        if program:
            filters["program"] = program
        
        fee_structures = frappe.get_all(
            "Fee Structure",
            filters=filters,
            fields=["name", "academic_year", "academic_term", "program", "total_amount"],
            order_by="academic_year desc, creation desc"
        )
        
        # Get components for each fee structure
        for structure in fee_structures:
            components = frappe.get_all(
                "Fee Component",
                filters={"parent": structure.name},
                fields=["fees_category", "amount", "discount", "total"],
                order_by="idx"
            )
            structure["components"] = components
        
        return {
            "success": True,
            "fee_structures": fee_structures
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "fee_structures": []
        }


@frappe.whitelist()
def get_student_groups_for_fee_structure(fee_structure_name):
    """Get student groups associated with a fee structure's program"""
    try:
        # Get the fee structure to extract program
        fee_structure = frappe.get_doc("Fee Structure", fee_structure_name)
        program = fee_structure.program
        
        # Get current academic year from Education Settings
        edu_settings = frappe.get_single("Education Settings")
        year = edu_settings.current_academic_year
        
        # Get student groups for the program and current academic year
        # Include all fields that frontend expects
        student_groups = frappe.get_all(
            "Student Group", 
            filters={
                "program": program, 
                "academic_year": year
            },
            fields=["name", "student_group_name", "batch", "program", "academic_year"]
        )
        
        # Add total_students field that frontend expects
        for group in student_groups:
            # Get student count from Student Group Student table
            student_count = frappe.db.count("Student Group Student", {
                "parent": group["name"],
                "active": 1
            })
            group["total_students"] = student_count
            
            # Ensure student_group_name exists (fallback to name)
            if not group.get("student_group_name"):
                group["student_group_name"] = group["name"]
        print(student_groups)
        return {
            "success": True,
            "student_groups": student_groups
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "student_groups": []
        }

