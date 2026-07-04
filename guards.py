import streamlit as st

# =====================================================
# ROLE CONSTANTS
# =====================================================
ROLE_ADMIN = 1
ROLE_MANAGER = 2
ROLE_CASHIER = 3

ROLE_NAME = {
    1: "Admin",
    2: "Manager",
    3: "Cashier"
}

# =====================================================
# CURRENT USER
# =====================================================
def current_user():
    return st.session_state.get("user")


# =====================================================
# LOGIN CHECK
# =====================================================
def is_logged_in():

    user = current_user()

    if not isinstance(user, dict):
        return False

    if not user.get("id"):
        return False

    if not user.get("is_active", False):
        return False

    return True


# =====================================================
# REQUIRE LOGIN
# =====================================================
def require_login():

    if not is_logged_in():

        st.warning("🔐 Please login first")
        st.stop()

    return current_user()


# =====================================================
# ROLE HELPERS
# =====================================================
def get_role_id():

    user = require_login()

    return int(user.get("role_id", ROLE_CASHIER))


def get_role_name():

    return ROLE_NAME.get(
        get_role_id(),
        "Cashier"
    )


# =====================================================
# ROLE CHECKERS
# =====================================================
def is_admin():

    return get_role_id() == ROLE_ADMIN


def is_manager():

    return get_role_id() == ROLE_MANAGER


def is_cashier():

    return get_role_id() == ROLE_CASHIER


# =====================================================
# ADMIN GUARD
# =====================================================
def require_admin():

    user = require_login()

    if user["role_id"] != ROLE_ADMIN:

        st.error("⛔ Access Denied")

        st.info("Administrator permission required.")

        st.stop()

    return user


# =====================================================
# MANAGER GUARD
# =====================================================
def require_manager():

    user = require_login()

    if user["role_id"] not in (
        ROLE_ADMIN,
        ROLE_MANAGER
    ):

        st.error("⛔ Manager permission required.")

        st.stop()

    return user


# =====================================================
# CASHIER GUARD
# =====================================================
def require_cashier():

    user = require_login()

    if user["role_id"] not in (
        ROLE_ADMIN,
        ROLE_MANAGER,
        ROLE_CASHIER
    ):

        st.error("⛔ Access Denied")

        st.stop()

    return user


# =====================================================
# GENERIC ROLE GUARD
# =====================================================
def require_role(*roles):

    user = require_login()

    if user["role_id"] not in roles:

        allowed = ", ".join(
            ROLE_NAME.get(r, str(r))
            for r in roles
        )

        st.error("⛔ Permission denied")

        st.caption(f"Allowed Roles : {allowed}")

        st.stop()

    return user


# =====================================================
# PERMISSION ENGINE (Future RBAC)
# =====================================================
def require_permission(permission_name):

    """
    Future RBAC Hook

    Example:

    require_permission("sales.create")

    require_permission("inventory.edit")

    require_permission("users.delete")

    """

    user = require_login()

    # -----------------------------------
    # FUTURE DATABASE LOOKUP
    # -----------------------------------
    # role_permissions table
    #
    # role_id
    # permission_name
    #
    # TODO
    #
    # if permission not found:
    #     deny
    #
    # -----------------------------------

    return user


# =====================================================
# PAGE TITLE HELPER
# =====================================================
def page_header(title, icon="📄"):

    require_login()

    st.title(f"{icon} {title}")

    st.caption(
        f"Logged in as {current_user()['full_name']} "
        f"({get_role_name()})"
    )


# =====================================================
# DEBUG PANEL
# =====================================================
def debug_user():

    user = current_user()

    st.write("Current User")

    st.json(user)
