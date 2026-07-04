import streamlit as st
from database import get_supabase

supabase = get_supabase()

# =========================
# SESSION INIT (SAFE)
# =========================
def init_session():
    if "user" not in st.session_state:
        st.session_state.user = None

init_session()

# =========================
# SAFE LOGIN QUERY WRAPPER
# =========================
def get_user(username: str):
    try:
        response = (
            supabase.table("users")
            .select("*")
            .or_(f"email.eq.{username},name.eq.{username}")
            .limit(1)
            .execute()
        )

        return response.data[0] if response.data else None

    except Exception as e:
        st.error("Database connection error")
        st.caption(str(e))
        return None

# =========================
# LOGIN PAGE
# =========================
def login_page():

    st.set_page_config(page_title="ERP Login", layout="centered")

    st.title("🔐 ERP Secure Login System")
    st.caption("Enterprise Access Control Layer")

    username = st.text_input("Username or Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        # -------------------------
        # INPUT VALIDATION
        # -------------------------
        if not username or not password:
            st.error("Please fill all fields")
            st.stop()

        # -------------------------
        # FETCH USER SAFELY
        # -------------------------
        user = get_user(username)

        if not user:
            st.error("User not found")
            st.stop()

        # -------------------------
        # PASSWORD CHECK (TEMP SAFE VERSION)
        # -------------------------
        # ⚠️ Production: replace with bcrypt later
        stored_password = user.get("password")

        if stored_password != password:
            st.error("Invalid credentials")
            st.stop()

        # -------------------------
        # SUCCESS LOGIN
        # -------------------------
        st.session_state.user = {
            "id": user.get("id"),
            "name": user.get("name"),
            "email": user.get("email"),
            "role": user.get("role", "staff")
        }

        st.success(f"Welcome {user.get('name')} 👋")
        st.rerun()

# =========================
# LOGOUT
# =========================
def logout():
    st.session_state.user = None
    st.rerun()

# =========================
# AUTH GUARD (USE IN MAIN APP)
# =========================
def is_authenticated():
    user = st.session_state.get("user")
    return user is not None and isinstance(user, dict)

# =========================
# OPTIONAL: LOGIN STATE VIEW
# =========================
def show_auth_status():
    if is_authenticated():
        st.sidebar.success(f"👤 {st.session_state.user['name']}")
        st.sidebar.write(f"Role: {st.session_state.user['role']}")

        if st.sidebar.button("🚪 Logout"):
            logout()
    else:
        st.sidebar.info("Not logged in")

# =========================
# AUTO ROUTING (FOR TEST ONLY)
# =========================
if __name__ == "__main__":

    if is_authenticated():
        st.success(f"Logged in as {st.session_state.user['name']}")

        show_auth_status()

    else:
        login_page()
