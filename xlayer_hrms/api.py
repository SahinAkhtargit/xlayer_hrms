import frappe
from frappe import auth

@frappe.whitelist( allow_guest=True )
def login(usr, pwd):
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()

        frappe.get_doc({
            "doctype": "Activity Log",
            "subject": "Logged In",
            "user": frappe.session.user,
            "operation": "Login",
            "activity_type": "Login",
            "reference_doctype": "User",
            "reference_name": frappe.session.user
        }).insert(ignore_permissions=True)

    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.response["status"] = False
        frappe.response["message"] = "Authentication Error!"
        # frappe.local.response["message"] = {
        #     "success_key": 0,
        #     "message": "Authentication Error!"
        # }
        return

    api_key, api_secret = generate_keys(frappe.session.user)
    user = frappe.get_doc('User', frappe.session.user)

    frappe.response["status"] = True
    frappe.response["message"] = "Authentication Success"
    frappe.response["data"] = {
        "s_id": frappe.session.sid,
        "api_key": api_key,
        "api_secret": api_secret,  # ← Use the fresh value, not user.api_secret
        "user": {
            "username": user.username,
            "email": user.email,
            "full_name": frappe.utils.get_fullname(user.username)
        },
        "home_page": "/app"
    }
def generate_keys(user):
    user_details = frappe.get_doc('User', user)

    if not user_details.api_key:
        user_details.api_key = frappe.generate_hash(length=15)

    api_secret = frappe.generate_hash(length=21)
    user_details.api_secret = api_secret
    user_details.save(ignore_permissions=True)

    return user_details.api_key, api_secret  # Return the unmasked secret


# def login(usr, pwd):
#     try:
#         login_manager = frappe.auth.LoginManager()
#         login_manager.authenticate(user=usr, pwd=pwd)
#         login_manager.post_login()
#         frappe.get_doc({
#             "doctype": "Activity Log",
#             "subject": "Logged In",
#             "user": frappe.session.user,
#             "operation": "Login",
#             "activity_type": "Login",
#             "reference_doctype": "User",
#             "reference_name": frappe.session.user
#         }).insert(ignore_permissions=True)
#     except frappe.exceptions.AuthenticationError:
#         frappe.clear_messages()
#         frappe.local.response["message"] = {
#             "success_key":0,
#             "message":"Authentication Error!"
#         }

#         return

#     api_generate = generate_keys(frappe.session.user)
#     user = frappe.get_doc('User', frappe.session.user)
#     frappe.response["status"] = True
#     frappe.response["message"] = "Authentication Success"
#     frappe.response["data"] = {
#         "s_id": frappe.session.sid,
#         "api_key": user.api_key,
#         "api_secret": api_generate,
#         "user": {
#             "username": user.username,
#             "email": user.email,
#             "full_name": frappe.utils.get_fullname(user.username)
#         },
#         "home_page": "/app",
        
#     }
#     frappe.response.pop("home_page", None)
#     frappe.response.pop("full_name", None)




# def generate_keys(user):
#     user_details = frappe.get_doc('User', user)
#     api_secret = frappe.generate_hash(length=15)

#     if not user_details.api_key:
#         api_key = frappe.generate_hash(length=15)
#         user_details.api_key = api_key

#     user_details.api_secret = api_secret
#     user_details.save()

#     return api_secret

@frappe.whitelist( allow_guest=True )
def logout():
    user = frappe.session.user

    if user == "Guest":
        frappe.response["status"] = False
        frappe.response["message"] = "No active session found"
        return
        # frappe.response["message"] = {
        #     "success_key": 0,
        #     "message": "No active session found"
        # }
        # return

    # Log the logout activity
    frappe.get_doc({
        "doctype": "Activity Log",
        "subject": "Logged Out",
        "user": user,
        "operation": "Logout",
        "activity_type": "Logout",
        "reference_doctype": "User",
        "reference_name": user
    }).insert(ignore_permissions=True)

    # Destroy the session
    frappe.local.login_manager.logout()
    frappe.db.commit()
    frappe.response["status"] = True
    frappe.response["message"] = "Successfully logged out"
    frappe.response.pop("home_page", None)
    frappe.response.pop("full_name", None)

    # frappe.response["message"] = {
    #     "success_key": 1,
    #     "message": "Successfully logged out"
    # }