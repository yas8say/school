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
# ✅ CANCEL + HARD DELETE WITH NO QUEUED JOBS
# =====================================================
def cancel_and_delete_all(doctype):
    print(f"\n🔹 Deleting {doctype}...")

    docs = frappe.get_all(doctype, fields=["name"])
    total = len(docs)

    if total == 0:
        print(f"✅ No records found in {doctype}")
        return

    for i, d in enumerate(docs, start=1):
        name = d.name
        try:
            doc = frappe.get_doc(doctype, name)

            if hasattr(doc, "docstatus") and doc.docstatus == 1:
                try:
                    doc.cancel()
                    doc.db_update()
                except:
                    pass  # Safe fallback for corrupted docs

            hard_delete(doctype, name)
            print(f"   ✅ {i}/{total} deleted: {name}")

        except Exception as e:
            print(f"❌ Error deleting {doctype} {name}: {e}")

    frappe.db.commit()
    print(f"✅ Completed {doctype}")


# =====================================================
# ✅ EDUCATION SETTINGS RESET
# =====================================================
def clear_academic_settings():
    try:
        settings = frappe.get_single("Education Settings")
        settings.current_academic_year = None
        settings.current_academic_term = None
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        print("✅ Cleared Education Settings Year/Term")
    except Exception as e:
        print(f"❌ Could not clear Education Settings: {e}")


# =====================================================
# ✅ DELETE USERS SAFELY
# =====================================================
def safe_delete_user(user_id):
    if not user_id or user_id.lower() == "administrator":
        return

    # Avoid deleting last System Manager
    is_sys_mgr = frappe.db.exists("Has Role", {"parent": user_id, "role": "System Manager"})
    other_mgrs = frappe.get_all("Has Role", filters={
        "role": "System Manager",
        "parent": ["!=", user_id]
    })

    if is_sys_mgr and not other_mgrs:
        print(f"⚠️ Cannot delete {user_id}: last System Manager")
        return

    try:
        frappe.delete_doc("User", user_id, force=True, ignore_permissions=True)
        frappe.db.commit()
        print(f"✅ Deleted linked User: {user_id}")
    except Exception as e:
        print(f"❌ Error deleting User {user_id}: {e}")


# =====================================================
# ✅ DELETE STUDENTS + GR NUMBER HANDLING
# =====================================================
def delete_students_completely():
    print("\n🔹 Deleting Students and linked Users...")

    students = frappe.get_all("Student", fields=["name", "student_email_id", "gr_number"])

    for s in students:
        sid = s.name
        gr = s.gr_number
        email = s.student_email_id

        try:
            # Delete Student
            hard_delete("Student", sid)
            print(f"✅ Deleted Student: {sid}")

            # Delete linked GR-number based user
            if gr and frappe.db.exists("User", gr):
                safe_delete_user(gr)

            # Delete email-based user
            if email:
                for u in frappe.get_all("User", filters={"email": email}):
                    safe_delete_user(u.name)

        except Exception as e:
            print(f"❌ Failed to delete Student {sid}: {e}")

    frappe.db.commit()
    print("✅ Completed Students cleanup")


# =====================================================
# ✅ OPTION C — MENU SYSTEM
# =====================================================
DELETE_SEQUENCE = [
    "Instructor",
    "User Permission",
    "Student Attendance",
    "Student Group",
    "Program Enrollment",
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
# ✅ MAIN ENTRYPOINT FOR BENCH
# =====================================================
def run():
    print("\n========= DATA CLEANUP TOOL =========")
    print("1️⃣  Delete ALL data (full wipe)")
    print("2️⃣  Delete a specific DocType")
    print("3️⃣  Exit")
    print("=====================================\n")

    choice = input("Enter choice (1/2/3): ").strip()

    # ---- FULL DELETE ----
    if choice == "1":
        delete_all_in_order()
        return

    # ---- SINGLE DOCTYPE ----
    elif choice == "2":
        dt = input("\nEnter DocType name to delete: ").strip()
        print(f"\n🚀 Deleting all records of: {dt}\n")

        if dt == "Student":
            delete_students_completely()
        else:
            cancel_and_delete_all(dt)

        print("\n✅ Completed single-doctype delete")
        return

    # ---- EXIT ----
    else:
        print("✅ Exiting. No changes made.")
