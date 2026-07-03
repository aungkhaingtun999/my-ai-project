import streamlit as st
from database import get_supabase

supabase = get_supabase()

# =========================
# SESSION INIT
# =========================
if "user" not in st.session_state:
    st.session_state.user = None

# =========================
# LOGIN FUNCTION
# =========================
def login_page():

    st.set_page_config(page_title="Login", layout="centered")

    st.title("🔐 Secure Login System")
    st.caption("ERP Access Control Panel")

    username = st.text_input("Username or Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if not username or not password:
            st.error("Please fill all fields")
            return

        # =========================
        # CHECK USER FROM DB
        # =========================
        user_resp = supabase.table("users") \
            .select("*") \
            .or_(f"email.eq.{username},name.eq.{username}") \
            .execute()

        users = user_resp.data or []

        if not users:
            st.error("User not found")
            return

        user = users[0]

        # =========================
        # PASSWORD CHECK
        # =========================
        # NOTE: for production → use hashed password (bcrypt)
        if user.get("password") != password:
            st.error("Invalid password")
            return

        # =========================
        # LOGIN SUCCESS
        # =========================
        st.session_state.user = {
            "id": user["id"],
            "name": user.get("name"),
            "email": user.get("email"),
            "role": user.get("role", "staff")
        }

        st.success(f"Welcome {user.get('name')} ({user.get('role')})")

        st.rerun()

# =========================
# LOGOUT FUNCTION
# =========================
def logout():
    st.session_state.user = None
    st.rerun()

# =========================
# AUTO ROUTING
# =========================
if st.session_state.user:
    st.success(f"Logged in as {st.session_state.user['name']}")

    st.write(f"Role: {st.session_state.user['role']}")

    if st.button("Logout"):
        logout()

else:
    login_page()