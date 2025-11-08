import frappe
import uuid

def create_single_fee_structure():
    """
    Create a single fee structure with forced random name
    """
    try:
        program_name = "1st"
        academic_year = "2025-26"
        
        # Generate random UUID name
        random_name = f"FS-{uuid.uuid4().hex[:12].upper()}"
        print(f"🎯 Target name: {random_name}")
        
        # Method 1: Try using frappe.rename_doc after creation
        print("🔄 Creating Fee Structure...")
        
        # First create with auto name
        fee_structure = frappe.new_doc("Fee Structure")
        fee_structure.program = program_name
        fee_structure.academic_year = academic_year
        
        # Add Admission Fee component
        fee_structure.append("components", {
            "fees_category": "Admission Fee", 
            "amount": 200, 
            "discount": 0, 
            "total": 200
        })
        
        fee_structure.total_amount = 200
        
        # Insert with auto-generated name
        fee_structure.insert(ignore_permissions=True)
        auto_name = fee_structure.name
        print(f"📝 Auto-created name: {auto_name}")
        fee_structure.submit()
        # Now rename it
        print(f"🔄 Renaming {auto_name} to {random_name}...")
        frappe.rename_doc("Fee Structure", auto_name, random_name, force=True)
        # frappe.db.commit()
        
        # Reload the document
        # fee_structure = frappe.get_doc("Fee Structure", random_name)
        # print(f"✅ Renamed to: {fee_structure.name}")
        
        # Submit

        
        return fee_structure.name
        
    except Exception as e:
        frappe.db.rollback()
        print(f"❌ Failed: {str(e)}")
        return None

# Run the function
created_structure = create_single_fee_structure()

if created_structure:
    print(f"🎉 Successfully created: {created_structure}")
else:
    print("💀 Failed to create fee structure")