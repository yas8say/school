import frappe
import subprocess
from frappe.utils import random_string

@frappe.whitelist(allow_guest=True)
def register_and_create_site(email, password):
    # 1. Register the User
    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": email.split('@')[0],
        "new_password": password
    })
    user.insert(ignore_permissions=True)

    # 2. Generate Unique Site Name
    site_name = f"{email.split('@')[0]}-{random_string(5)}.yourdomain.com"
    # site_name = "test2"
    # 3. Create New Site (replace DB passwords as needed)
    subprocess.run(
        f"bench new-site {site_name} --mariadb-root-password 123456 --admin-password 1234 --install-app erpnext",
        shell=True
    )

    # 4. Update NGINX & Restart
    subprocess.run("bench setup nginx && sudo service nginx reload", shell=True)

    # 5. Return the New Site URL
    return {"status": "success", "site_url": f"https://{site_name}"}
