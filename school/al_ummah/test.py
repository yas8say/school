import frappe
import subprocess

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

    # 2. Generate Site Name without random string
    site_name = f"{email.split('@')[0]}.yourdomain.com"

    # 3. Create New Site
    subprocess.run(
        f"bench new-site {site_name} --mariadb-root-password 123456 --admin-password 1234 --install-app erpnext",
        shell=True,
        check=True
    )

    # 4. Add site to /etc/hosts
    subprocess.run(
        f"echo '127.0.0.1 {site_name}' | sudo tee -a /etc/hosts",
        shell=True,
        check=True
    )

    # 5. Update NGINX and Restart
    subprocess.run("bench setup nginx && sudo service nginx reload", shell=True, check=True)

    # 6. Return New Site URL
    return {"status": "success", "site_url": f"https://{site_name}"}


