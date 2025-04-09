import frappe
from frappe import _
from frappe.utils import nowdate

@frappe.whitelist(allow_guest=False)
def create_employee(
    first_name,
    middle_name=None,
    last_name=None,
    gender=None,
    date_of_birth=None,
    date_of_joining=None,
    cell_number=None,
    personal_email=None,
    company_email=None,
    prefered_contact_email=None,
    status=None,
    company=None,
    employee_number=None,
    department=None,
    designation=None,
    branch=None,
    employment_type=None,
    reports_to=None
):
    # return "I'm under employee..."
    if frappe.session.user == "Guest":
        frappe.throw(_("Unauthorized access"), frappe.PermissionError)

    employee = frappe.new_doc("Employee")

    employee.first_name = first_name
    employee.middle_name = middle_name
    employee.last_name = last_name
    employee.gender = gender
    employee.date_of_birth = date_of_birth or None
    employee.date_of_joining = date_of_joining or nowdate()
    employee.cell_number = cell_number
    employee.personal_email = personal_email
    employee.company_email = company_email
    employee.prefered_contact_email = prefered_contact_email
    employee.status = status or "Active"
    employee.company = company
    employee.employee_number = employee_number
    employee.department = department
    employee.designation = designation
    employee.branch = branch
    employee.employment_type = employment_type
    employee.reports_to = reports_to

    employee.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "status": True,
        "message": "Employee created successfully",
        "employee_id": employee.name
    }
