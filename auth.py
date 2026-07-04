import streamlit as st
from database import get_supabase

supabase = get_supabase()

# ==================================================
# SESSION INITIALIZER
# ==================================================
def init_auth():
    if "user" not in st.session_state:
        st.session_state.user = None


init_auth()

# ==================================================
# ROLE MAP
# ==================================================
ROLE_MAP = {
    1: "Admin",
    2: "Manager",
    3: "Cashier"
}

# ==================================================
# SAFE USER FETCH
# ==================================================
def get_user(username: str):

    try:

        response = (
            supabase
            .table("users")
            .select("*")
            .eq("username", username.strip())
            .eq("is_active", True)
            .limit(1)
            .execute()
        )

        data = response.data or []

        if len(data) == 0:
            return None

        return data[0]

    except Exception as e:

        st.error("Database Error")
        st.exception(e)
        return None


# ==================================================
# PASSWORD VERIFY
# ==================================================
def verify_password(user, password):

    stored = str(user.get("password_hash", ""))

    # Future
    # bcrypt.checkpw(...)

    return stored == password


# ==================================================
# BUILD SESSION
# ==================================================
def build_session(user):

    role_id = int(user.get("role_id", 3))

    role_name = ROLE_MAP.get(role_id, "Cashier")

    st.session_state.user = {

        "id": user["id"],

        "username": user["username"],

        "full_name": user.get(
            "full_name",
            user["username"]
        ),

        "role_id": role_id,

        "role": role_name,

        "is_active": bool(user.get("is_active", True))
    }


# ==================================================
# LOGIN PAGE
# ==================================================
def login_page():

    st.title("🔐 ERP Enterprise Login")

    st.caption("Secure Authentication Layer")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    login = st.button(
        "Login",
        use_container_width=True
    )

    if not login:
        return

    if username.strip() == "" or password == "":

        st.warning("Please enter username and password.")

        return

    user = get_user(username)

    if user is None:

        st.error("User not found.")

        return

    if not verify_password(user, password):

        st.error("Invalid password.")

        return

    build_session(user)

    st.success(
        f"Welcome {st.session_state.user['full_name']}"
    )

    st.rerun()


# ==================================================
# LOGOUT
# ==================================================
def logout():

    keep = {}

    st.session_state.clear()

    st.session_state.user = None

    st.rerun()


# ==================================================
# LOGIN CHECK
# ==================================================
def is_authenticated():

    user = st.session_state.get("user")

    if not isinstance(user, dict):
        return False

    if not user.get("id"):
        return False

    if not user.get("is_active", False):
        return False

    return True


# ==================================================
# REQUIRE LOGIN
# ==================================================
def require_login():

    if not is_authenticated():

        login_page()

        st.stop()

    return st.session_state.user


# ==================================================
# REQUIRE ADMIN
# ==================================================
def require_admin():

    user = require_login()

    if user["role_id"] != 1:

        st.error("⛔ Admin Only")

        st.stop()

    return user


# ==================================================
# CURRENT USER
# ==================================================
def current_user():

    return st.session_state.get("user")


# ==================================================
# CURRENT ROLE
# ==================================================
def current_role():

    user = current_user()

    if not user:
        return "Guest"

    return user["role"]


# ==================================================
# SIDEBAR USER CARD
# ==================================================
def auth_sidebar():

    if not is_authenticated():
        return

    user = current_user()

    with st.sidebar:

        st.success(
            f"👤 {user['full_name']}"
        )

        st.caption(
            f"Role : {user['role']}"
        )

        st.caption(
            f"Username : {user['username']}"
        )

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            logout()
