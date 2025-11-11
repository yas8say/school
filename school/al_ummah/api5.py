import frappe
import json
from education.education.doctype.fee_structure.fee_structure import make_fee_schedule, get_amount_distribution_based_on_fee_plan
from frappe.utils import nowdate

@frappe.whitelist()
def create_and_submit_fee_schedules_with_invoices(fee_structures, student_groups, student_exceptions=None):
    """
    Create and submit fee schedules, then create and submit sales invoices/orders for all students
    Accepts multiple fee structures and handles student fee category exceptions
    """
    try:
        # Validate input parameters
        if not all([fee_structures, student_groups]):
            return {
                "success": False,
                "message": "Fee Structures and Student Groups are required"
            }

        # Parse input parameters
        if isinstance(fee_structures, str):
            fee_structures = json.loads(fee_structures)
        
        if isinstance(student_groups, str):
            student_groups = json.loads(student_groups)
        
        if student_exceptions and isinstance(student_exceptions, str):
            student_exceptions = json.loads(student_exceptions)
        
        if not isinstance(fee_structures, list):
            return {
                "success": False,
                "message": "Fee Structures must be a list"
            }

        if not isinstance(student_groups, list):
            return {
                "success": False,
                "message": "Student Groups must be a list"
            }

        # Validate all fee structures exist and have required fields
        for fs_data in fee_structures:
            if not all([fs_data.get('fee_structure_name'), fs_data.get('fee_plan')]):
                return {
                    "success": False,
                    "message": "Each fee structure must have fee_structure_name and fee_plan"
                }
            
            if not frappe.db.exists("Fee Structure", fs_data['fee_structure_name']):
                return {
                    "success": False,
                    "message": f"Fee Structure {fs_data['fee_structure_name']} not found"
                }

        # Validate all student groups exist
        for student_group in student_groups:
            if not frappe.db.exists("Student Group", student_group):
                return {
                    "success": False,
                    "message": f"Student Group {student_group} not found"
                }

        # Step 1: Create and submit fee schedules for each structure
        all_created_schedules = []
        for fs_data in fee_structures:
            created_schedules = create_and_submit_fee_schedules(
                fs_data['fee_structure_name'], 
                student_groups, 
                fs_data['fee_plan'], 
                fs_data.get('due_dates')
            )
            all_created_schedules.extend(created_schedules)
        
        if not all_created_schedules:
            return {
                "success": False,
                "message": "No fee schedules were created"
            }

        # Step 2: Create and submit sales invoices for all submitted fee schedules with exceptions handling
        invoice_results = []
        for schedule_name in all_created_schedules:
            result = create_and_submit_sales_invoices_for_schedule_with_exceptions(
                schedule_name, 
                student_exceptions
            )
            invoice_results.append({
                "fee_schedule": schedule_name,
                "result": result
            })

        return {
            "success": True,
            "message": f"Successfully created {len(all_created_schedules)} fee schedules and corresponding sales documents",
            "fee_schedules": all_created_schedules,
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


def create_and_submit_sales_invoices_for_schedule_with_exceptions(fee_schedule_name, student_exceptions=None):
    """Create and submit sales invoices for a given fee schedule with student exceptions"""
    try:
        # Get the fee schedule document
        fee_schedule = frappe.get_doc("Fee Schedule", fee_schedule_name)
        
        # Check Education Settings to see if we should create Sales Orders instead
        create_so = frappe.db.get_single_value("Education Settings", "create_so")
        
        if create_so:
            result = create_and_submit_sales_orders_for_schedule_with_exceptions(fee_schedule_name, student_exceptions)
        else:
            result = create_and_submit_sales_invoices_for_schedule_backend_with_exceptions(fee_schedule_name, student_exceptions)
        
        return result
        
    except Exception as e:
        frappe.log_error(f"Sales Document Creation Error for {fee_schedule_name}: {str(e)}")
        return {"success": False, "message": str(e)}


def create_and_submit_sales_invoices_for_schedule_backend_with_exceptions(fee_schedule_name, student_exceptions=None):
    """Backend logic to create and submit sales invoices with fee category exceptions"""
    try:
        # Set status to "In Process"
        frappe.db.set_value("Fee Schedule", fee_schedule_name, "status", "In Process")
        
        # Get all students from the fee schedule's student groups
        fee_schedule = frappe.get_doc("Fee Schedule", fee_schedule_name)
        total_records = sum([int(d.total_students) for d in fee_schedule.student_groups])
        created_records = 0
        submitted_invoices = []
        
        # Get fee structure components to understand available fee categories
        fee_structure = frappe.get_doc("Fee Structure", fee_schedule.fee_structure)
        all_fee_categories = [comp.fees_category for comp in fee_structure.components]
        
        # Process each student group
        for student_group in fee_schedule.student_groups:
            students = get_students_from_group(
                student_group.student_group,
                fee_schedule.academic_year,
                fee_schedule.academic_term,
                fee_schedule.student_category
            )
            
            # Get exceptions for this student group
            group_exceptions = student_exceptions.get(student_group.student_group, {}) if student_exceptions else {}
            
            # Create and submit sales invoice for each student with exceptions handling
            for student in students:
                try:
                    # Get excluded categories for this student
                    excluded_categories = group_exceptions.get(student.student, [])
                    
                    # Create invoice with only selected fee categories
                    invoice_name = create_and_submit_single_sales_invoice_with_exceptions(
                        fee_schedule_name, 
                        student.student, 
                        excluded_categories,
                        all_fee_categories
                    )
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


def create_and_submit_sales_orders_for_schedule_with_exceptions(fee_schedule_name, student_exceptions=None):
    """Create and submit sales orders with fee category exceptions"""
    try:
        fee_schedule = frappe.get_doc("Fee Schedule", fee_schedule_name)
        frappe.db.set_value("Fee Schedule", fee_schedule_name, "status", "In Process")
        
        total_records = sum([int(d.total_students) for d in fee_schedule.student_groups])
        created_records = 0
        submitted_orders = []
        
        # Get fee structure components
        fee_structure = frappe.get_doc("Fee Structure", fee_schedule.fee_structure)
        all_fee_categories = [comp.fees_category for comp in fee_structure.components]
        
        for student_group in fee_schedule.student_groups:
            students = get_students_from_group(
                student_group.student_group,
                fee_schedule.academic_year,
                fee_schedule.academic_term,
                fee_schedule.student_category
            )
            
            # Get exceptions for this student group
            group_exceptions = student_exceptions.get(student_group.student_group, {}) if student_exceptions else {}
            
            for student in students:
                try:
                    # Get excluded categories for this student
                    excluded_categories = group_exceptions.get(student.student, [])
                    
                    # Create order with only selected fee categories
                    order_name = create_and_submit_single_sales_order_with_exceptions(
                        fee_schedule_name, 
                        student.student, 
                        excluded_categories,
                        all_fee_categories
                    )
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


def create_and_submit_single_sales_invoice_with_exceptions(fee_schedule_name, student_id, excluded_categories, all_fee_categories):
    """Create and submit a single sales invoice for a student with fee category exceptions"""
    from education.education.doctype.fee_schedule.fee_schedule import create_sales_invoice
    
    # Create the base sales invoice
    invoice_name = create_sales_invoice(fee_schedule_name, student_id)
    
    if invoice_name and excluded_categories:
        # Modify the invoice to remove excluded fee categories
        invoice_doc = frappe.get_doc("Sales Invoice", invoice_name)
        modified_items = []
        
        for item in invoice_doc.items:
            # Check if this item corresponds to an excluded fee category
            item_fee_category = get_fee_category_from_item(item.item_code, item.item_name)
            
            # Only include items that are not in excluded categories
            if item_fee_category not in excluded_categories:
                modified_items.append(item)
            else:
                frappe.logger().info(f"Excluding fee category {item_fee_category} for student {student_id}")
        
        # Replace items with filtered list
        invoice_doc.set('items', modified_items)
        
        # Recalculate totals
        invoice_doc.calculate_taxes_and_totals()
        
        # Save the modified invoice
        invoice_doc.save()
    
    # Submit the sales invoice
    if invoice_name:
        invoice_doc = frappe.get_doc("Sales Invoice", invoice_name)
        invoice_doc.submit()
    
    return invoice_name


def create_and_submit_single_sales_order_with_exceptions(fee_schedule_name, student_id, excluded_categories, all_fee_categories):
    """Create and submit a single sales order for a student with fee category exceptions"""
    from education.education.doctype.fee_schedule.fee_schedule import create_sales_order
    
    # Create the base sales order
    order_name = create_sales_order(fee_schedule_name, student_id)
    
    if order_name and excluded_categories:
        # Modify the order to remove excluded fee categories
        order_doc = frappe.get_doc("Sales Order", order_name)
        modified_items = []
        
        for item in order_doc.items:
            # Check if this item corresponds to an excluded fee category
            item_fee_category = get_fee_category_from_item(item.item_code, item.item_name)
            
            # Only include items that are not in excluded categories
            if item_fee_category not in excluded_categories:
                modified_items.append(item)
            else:
                frappe.logger().info(f"Excluding fee category {item_fee_category} for student {student_id}")
        
        # Replace items with filtered list
        order_doc.set('items', modified_items)
        
        # Recalculate totals
        order_doc.calculate_taxes_and_totals()
        
        # Save the modified order
        order_doc.save()
    
    # Submit the sales order
    if order_name:
        order_doc = frappe.get_doc("Sales Order", order_name)
        order_doc.submit()
    
    return order_name


def get_fee_category_from_item(item_code, item_name):
    """
    Extract fee category from item code or name
    This function maps sales invoice items back to fee categories
    """
    try:
        # Method 1: Check if item has a fee category field
        if frappe.db.exists("Item", item_code):
            item_doc = frappe.get_doc("Item", item_code)
            if hasattr(item_doc, 'fee_category') and item_doc.fee_category:
                return item_doc.fee_category
        
        # Method 2: Extract from item name (common pattern: "Fee Category - Description")
        if " - " in item_name:
            return item_name.split(" - ")[0]
        
        # Method 3: Use item name as fallback
        return item_name
        
    except Exception:
        # Fallback to item name
        return item_name


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


# Alternative approach: Create custom sales invoice function that handles exceptions from start
# def create_custom_sales_invoice_with_selected_categories(fee_schedule_name, student_id, selected_categories):
#     """
#     Create sales invoice with only selected fee categories
#     This is an alternative approach that builds the invoice from scratch
#     """
#     try:
#         from education.education.doctype.fee_schedule.fee_schedule import get_customer_from_student, get_fees_mapped_doc
        
#         customer = get_customer_from_student(student_id)
#         fee_schedule = frappe.get_doc("Fee Schedule", fee_schedule_name)
        
#         # Create base sales invoice
#         sales_invoice_doc = get_fees_mapped_doc(
#             fee_schedule=fee_schedule_name,
#             doctype="Sales Invoice",
#             student_id=student_id,
#             customer=customer,
#         )
        
#         # Filter items based on selected categories
#         filtered_items = []
#         for item in sales_invoice_doc.items:
#             item_fee_category = get_fee_category_from_item(item.item_code, item.item_name)
#             if item_fee_category in selected_categories:
#                 item.qty = 1
#                 item.cost_center = ""
#                 filtered_items.append(item)
        
#         # Replace items with filtered list
#         sales_invoice_doc.set('items', filtered_items)
        
#         # Set posting time if configured
#         if frappe.db.get_single_value("Education Settings", "sales_invoice_posting_date_fee_schedule"):
#             sales_invoice_doc.set_posting_time = 1
        
#         # Save the invoice
#         sales_invoice_doc.save()
        
#         # Auto-submit if configured
#         if frappe.db.get_single_value("Education Settings", "auto_submit_sales_invoice"):
#             sales_invoice_doc.submit()
        
#         return sales_invoice_doc.name
        
#     except Exception as e:
#         frappe.log_error(f"Custom Sales Invoice Creation Error: {str(e)}")
#         raise e

#____________________________________________

@frappe.whitelist()
def get_fee_structures_for_selection(program=None):
    """Get list of fee structures for frontend selection with fee schedules count"""
    try:
        # Get current academic year
        current_academic_year = frappe.db.get_single_value("Education Settings", "current_academic_year")
        
        if not current_academic_year:
            return {
                "success": False,
                "message": "Current academic year not set in Education Settings",
                "fee_structures": [],
                "fee_schedules_count": 0
            }
        
        # Build filters
        filters = {"docstatus": 1, "academic_year": current_academic_year}
        
        # Add program filter if provided
        if program:
            filters["program"] = program
        
        # Get fee structures
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
        
        # Get fee schedules count in single query
        fee_schedules_count = frappe.db.count("Fee Schedule", filters=filters)
        
        return {
            "success": True,
            "current_academic_year": current_academic_year,
            "fee_structures": fee_structures,
            "fee_schedules_count": fee_schedules_count
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting fee structures: {str(e)}")
        return {
            "success": False,
            "message": str(e),
            "fee_structures": [],
            "fee_schedules_count": 0
        }


@frappe.whitelist()
def get_student_groups(program):
    try:
        # Import required DocTypes
        StudentGroupStudent = frappe.qb.DocType("Student Group Student")
        Student = frappe.qb.DocType("Student")
        
        # First get all student groups for the program
        student_groups = frappe.get_all(
            "Student Group", 
            filters={
                "program": program, 
            },
            fields=["name", "student_group_name", "batch", "program", "academic_year"]
        )
        
        # Add student data for each group
        for group in student_groups:
            # Get student count and student details using frappe.qb
            student_query = (
                frappe.qb.from_(StudentGroupStudent)
                .inner_join(Student)
                .on(StudentGroupStudent.student == Student.name)
                .select(
                    StudentGroupStudent.student,
                    StudentGroupStudent.student_name,
                    StudentGroupStudent.group_roll_number,
                    StudentGroupStudent.active,
                    Student.image.as_("student_image"),
                    Student.student_email_id,
                    Student.student_mobile_number
                )
                .where(
                    (StudentGroupStudent.parent == group["name"])
                    & (StudentGroupStudent.active == 1)
                )
                .orderby(StudentGroupStudent.group_roll_number)
            )
            
            students = student_query.run(as_dict=True)
            
            # Add students data to the group
            group["students"] = students
            group["total_students"] = len(students)
            
            # Ensure student_group_name exists (fallback to name)
            if not group.get("student_group_name"):
                group["student_group_name"] = group["name"]
                
        print(student_groups)
        return {
            "success": True,
            "student_groups": student_groups
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_student_groups: {str(e)}")
        return {
            "success": False,
            "message": str(e),
            "student_groups": []
        }
