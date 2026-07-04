import streamlit as st
from database import get_supabase

supabase = get_supabase()

# =========================
# SESSION INIT
# =========================
def init_session():
    if "user" not in st.session_state:
        st.session_state.user = None

init_session()

# =========================
# SAFE USER FETCH (FIXED)
# =========================
def get_user(username: str):
    try:
        response = (
            supabase.table("users")
            .select("*")
            .eq("username", username)
            .eq("is_active", True)
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

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        # -------------------------
        # VALIDATION
        # -------------------------
        if not username or not password:
            st.error("Please fill all fields")
            st.stop()

        # -------------------------
        # FETCH USER
        # -------------------------
        user = get_user(username)

        if not user:
            st.error("User not found")
            st.stop()

        # -------------------------
        # PASSWORD CHECK
        # -------------------------
        # ⚠️ TEMP SAFE (replace with bcrypt later)
        stored_hash = user.get("password_hash")

        if stored_hash != password:
            st.error("Invalid credentials")
            st.stop()

        # -------------------------
        # SESSION BUILD
        # -------------------------
        st.session_state.user = {
            "id": user.get("id"),
            "username": user.get("username"),
            "full_name": user.get("full_name"),
            "role_id": user.get("role_id")
        }

        st.success(f"Welcome {user.get('full_name')} 👋")
        st.rerun()

# =========================
# LOGOUT
# =========================
def logout():
    st.session_state.user = None
    st.rerun()

# =========================
# AUTH CHECK
# =========================
def is_authenticated():
    user = st.session_state.get("user")
    return user is not None

# =========================
# SIDEBAR STATUS
# =========================
def show_auth_status():
    if is_authenticated():
        st.sidebar.success(f"👤 {st.session_state.user['full_name']}")
        st.sidebar.write(f"Role ID: {st.session_state.user['role_id']}")

        if st.sidebar.button("🚪 Logout"):
            logout()
    else:
        st.sidebar.info("Not logged in")

# =========================
# MAIN APP ROUTER (TEST MODE)
# =========================
if __name__ == "__main__":

    if is_authenticated():
        st.title("🛒 ERP Dashboard Access")

        st.write("Logged in as:")
        st.json(st.session_state.user)

        show_auth_status()

    else:
        login_page()
