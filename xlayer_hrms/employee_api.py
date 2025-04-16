
import frappe
from frappe import _
from frappe.utils import nowdate
@frappe.whitelist(allow_guest=False)
def create_employee(**kwargs):
    if frappe.session.user == "Guest":
        frappe.throw(_("Unauthorized access"), frappe.PermissionError)

    try:
        # Uniqueness Checks
        if kwargs.get("personal_email") and frappe.db.exists("Employee", {"personal_email": kwargs.get("personal_email")}):
            frappe.response["status"] = False
            frappe.response["message"] = "Duplicate entry not allowed: personal_email already exists"
            frappe.response["data"] = None
            return

        if kwargs.get("company_email") and frappe.db.exists("Employee", {"company_email": kwargs.get("company_email")}):
            frappe.response["status"] = False
            frappe.response["message"] = "Duplicate entry not allowed: company_email already exists"
            frappe.response["data"] = None
            return

        if kwargs.get("employee_number") and frappe.db.exists("Employee", {"employee_number": kwargs.get("employee_number")}):
            frappe.response["status"] = False
            frappe.response["message"] = "Duplicate entry not allowed: employee_number already exists"
            frappe.response["data"] = None
            return

        # Create Employee
        employee = frappe.new_doc("Employee")

        for key, value in kwargs.items():
            if hasattr(employee, key):
                setattr(employee, key, value)

        if not employee.date_of_joining:
            employee.date_of_joining = nowdate()
        if not employee.status:
            employee.status = "Active"

        employee.insert(ignore_permissions=True)
        frappe.db.commit()

        frappe.response["status"] = True
        frappe.response["message"] = "Employee created successfully"
        frappe.response["data"] = employee.as_dict()

    except Exception as e:
        frappe.response["status"] = False
        frappe.response["message"] = str(e)
        frappe.response["data"] = None


@frappe.whitelist(allow_guest=False)
def get_all_employees():
    if frappe.session.user == "Guest":
        frappe.throw(_("Unauthorized access"), frappe.PermissionError)

    try:
        employees = frappe.get_all("Employee", fields=["name", "employee_name", "employee_number", "status", "company", "branch", "department", "designation"])

        frappe.response["status"] = True
        frappe.response["message"] = "Employees fetched successfully"
        frappe.response["data"] = employees
    except Exception as e:
        frappe.response["status"] = False
        frappe.response["message"] = str(e)
        frappe.response["data"] = None

@frappe.whitelist(allow_guest=False)
def update_employee(name, **kwargs):
    if frappe.session.user == "Guest":
        frappe.throw(_("Unauthorized access"), frappe.PermissionError)

    try:
        if not frappe.db.exists("Employee", name):
            frappe.response["status"] = False
            frappe.response["message"] = "Employee not found"
            frappe.response["data"] = None
            return

        doc = frappe.get_doc("Employee", name)

        for key, value in kwargs.items():
            if hasattr(doc, key):
                setattr(doc, key, value)

        doc.save(ignore_permissions=True)
        frappe.db.commit()

        frappe.response["status"] = True
        frappe.response["message"] = "Employee updated successfully"
        frappe.response["data"] = doc.as_dict()
    except Exception as e:
        frappe.response["status"] = False
        frappe.response["message"] = str(e)
        frappe.response["data"] = None

@frappe.whitelist(allow_guest=False)
def delete_employee(name):
    if frappe.session.user == "Guest":
        frappe.throw(_("Unauthorized access"), frappe.PermissionError)

    try:
        if not frappe.db.exists("Employee", name):
            frappe.response["status"] = False
            frappe.response["message"] = "Employee not found"
            frappe.response["data"] = None
            return
        employee = frappe.get_doc("Employee", name)
        linked_user = employee.user_id if hasattr(employee, "user_id") else None

        if linked_user:
            employee.user_id = None
            employee.save(ignore_permissions=True)
            frappe.db.commit()
            user_permissions = frappe.get_all("User Permission", filters={"for_value": name, "allow": "Employee"})
            for perm in user_permissions:
                frappe.delete_doc("User Permission", perm.name, ignore_permissions=True)
            if frappe.db.exists("User", linked_user):
                frappe.delete_doc("User", linked_user, ignore_permissions=True)
                frappe.db.commit()

        frappe.delete_doc("Employee", name, ignore_permissions=True)
        frappe.db.commit()

        frappe.response["status"] = True
        frappe.response["message"] = "Employee and linked user deleted successfully"
        frappe.response["data"] = {"employee": name, "user": linked_user}

    except Exception as e:
        frappe.response["status"] = False
        frappe.response["message"] = str(e)
        frappe.response["data"] = None
