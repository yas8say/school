# school/al_ummah/delete_all.py

import frappe

# =====================================================
# ✅ FAST DELETE (NO background jobs)
# =====================================================
def hard_delete(doctype, name):
    try:
        frappe.db.delete(doctype, {"name": name})
        return True
    except Exception as e:
        print(f"❌ Failed {doctype} {name}: {e}")
        return False


# =====================================================
# ✅ DELETE ALL CHILD TABLE ROWS FOR A DOCUMENT
# =====================================================
def delete_child_tables(doctype, parent_name):
    """Auto-detect & delete child tables for any DocType"""
    try:
        meta = frappe.get_meta(doctype)
    except Exception:
        return

    for df in meta.fields:
        if df.fieldtype == "Table":
            child_dt = df.options
            if not child_dt:
                continue
            try:
                frappe.db.delete(child_dt, {"parent": parent_name})
                print(f"      🧹 Cleaned child table: {child_dt}")
            except Exception as e:
                print(f"      ⚠️ Failed to delete child table {child_dt}: {e}")


# =====================================================
# ✅ CANCEL + DELETE ANY DOCTYPE COMPLETELY
# =====================================================
def cancel_and_delete_all(doctype):
    print(f"\n🔹 Deleting {doctype}...")

    try:
        docs = frappe.get_all(doctype, fields=["name"])
    except Exception as e:
        print(f"⚠️ Skipping {doctype}: {e}")
        return

    total = len(docs)
    if total == 0:
        print(f"✅ No records found in {doctype}")
        return

    for i, d in enumerate(docs, start=1):
        name = d.name
        try:
            doc = frappe.get_doc(doctype, name)

            # Cancel submitted docs
            if getattr(doc, "docstatus", None) == 1:
                try:
                    doc.cancel()
                    doc.db_update()
                except:
                    pass

            # ✅ Delete child tables first
            delete_child_tables(doctype, name)

            # ✅ Hard delete parent row
            hard_delete(doctype, name)

            print(f"   ✅ {i}/{total} deleted: {name}")

        except Exception as e:
            print(f"❌ Error deleting {doctype} {name}: {e}")

    frappe.db.commit()
    print(f"✅ Completed {doctype}")


# =====================================================
# ✅ CLEAR EDUCATION SETTINGS
# =====================================================
def clear_academic_settings():
    try:
        s = frappe.get_single("Education Settings")
        s.current_academic_year = None
        s.current_academic_term = None
        s.save(ignore_permissions=True)
        frappe.db.commit()
        print("✅ Cleared Education Settings")
    except Exception as e:
        print(f"❌ Could not clear Education Settings: {e}")


# =====================================================
# ✅ SAFE USER DELETE
# =====================================================
def safe_delete_user(user_id):
    if not user_id or user_id.lower() == "administrator":
        return

    is_sys_mgr = frappe.db.exists("Has Role", {"parent": user_id, "role": "System Manager"})
    other_mgrs = frappe.get_all("Has Role",
                                filters={"role": "System Manager", "parent": ["!=", user_id]})

    # Avoid deleting the last system manager
    if is_sys_mgr and not other_mgrs:
        print(f"⚠️ Cannot delete {user_id}: last System Manager")
        return

    try:
        # Remove child tables under user
        delete_child_tables("User", user_id)

        frappe.delete_doc("User", user_id, force=True, ignore_permissions=True)
        frappe.db.commit()
        print(f"✅ Deleted User: {user_id}")
    except Exception as e:
        print(f"❌ Error deleting User {user_id}: {e}")


# =====================================================
# ✅ DELETE STUDENTS + THEIR USERS + CHILD TABLES
# =====================================================
def delete_students_completely():
    print("\n🔹 Deleting Students and linked Users...")

    students = frappe.get_all("Student", fields=["name", "student_email_id", "name"])

    for s in students:
        sid = s.name
        email = s.student_email_id
        gr = s.name

        try:
            # ✅ Delete all Student child tables
            delete_child_tables("Student", sid)

            # ✅ Delete Student
            hard_delete("Student", sid)
            print(f"✅ Deleted Student: {sid}")

            # ✅ Delete user by GR-Number (if exists)
            if gr and frappe.db.exists("User", gr):
                safe_delete_user(gr)

            # ✅ Delete user by student email
            if email:
                for u in frappe.get_all("User", filters={"email": email}):
                    safe_delete_user(u.name)

        except Exception as e:
            print(f"❌ Failed to delete Student {sid}: {e}")

    frappe.db.commit()
    print("✅ Completed Students cleanup")


# =====================================================
# ✅ DELETE ORDER (Top → Bottom)
# =====================================================
DELETE_SEQUENCE = [
    "Instructor",
    "User Permission",
    "Student Attendance",
    "Student Group",
    "Student Batch Name",
    "Program Enrollment",
    "Course Enrollment",
    "Academic Year",
    "Academic Term",
    "Course",
    "Program",
    "Customer",
    "Sales Invoice",
    "Payment Entry",
    "Payment Ledger Entry",
    "Fee Structure",
    "Fee Category",
    "Fee Schedule",
    "User Device",
    "Guardian",
    "Employee",
    "Student"
]


# =====================================================
# ✅ FULL CLEANUP (WIPE EVERYTHING)
# =====================================================
def delete_all_in_order():
    print("\n🚀 Starting FULL Cleanup...\n")

    for dt in DELETE_SEQUENCE:
        if dt == "Student":
            delete_students_completely()
        else:
            cancel_and_delete_all(dt)

    clear_academic_settings()
    print("\n✅✅ FULL Cleanup COMPLETE ✅✅")


# =====================================================
# ✅ MAIN ENTRY
# =====================================================
def run():
    print("\n========= DATA CLEANUP TOOL =========")
    print("1️⃣  Delete ALL data (full wipe)")
    print("2️⃣  Delete a specific DocType")
    print("3️⃣  Exit")
    print("=====================================\n")

    choice = input("Enter choice (1/2/3): ").strip()

    if choice == "1":
        delete_all_in_order()

    elif choice == "2":
        dt = input("\nEnter DocType name to delete: ").strip()
        print(f"\n🚀 Deleting all records of: {dt}\n")

        if dt == "Student":
            delete_students_completely()
        else:
            cancel_and_delete_all(dt)

        print("\n✅ Completed single-doctype delete")

    else:
        print("✅ Exiting. No changes made.")
