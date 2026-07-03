import streamlit as st
from database import get_supabase

supabase = get_supabase()

st.set_page_config(page_title="User Management", layout="wide")

st.title("👥 User Management (Admin Panel)")
st.caption("Control users, roles, and access rights")

# =========================
# LOAD USERS
# =========================
users_resp = supabase.table("users").select("*").execute()
users = users_resp.data or []

# =========================
# SEARCH
# =========================
search = st.text_input("🔍 Search user (name / email / role)")

if search:
    users = [
        u for u in users
        if search.lower() in str(u.get("name", "")).lower()
        or search.lower() in str(u.get("email", "")).lower()
        or search.lower() in str(u.get("role", "")).lower()
    ]

# =========================
# CREATE USER SECTION
# =========================
st.subheader("➕ Create New User")

with st.form("create_user"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["admin", "staff", "cashier"])

    submit = st.form_submit_button("Create User")

    if submit:
        if not name or not email or not password:
            st.error("All fields required")
        else:
            result = supabase.table("users").insert({
                "name": name,
                "email": email,
                "password": password,  # NOTE: ideally hashed in backend
                "role": role
            }).execute()

            if result.data:
                st.success("User created successfully")
                st.rerun()
            else:
                st.error("Failed to create user")

st.divider()

# =========================
# USERS TABLE
# =========================
st.subheader("📋 All Users")

if not users:
    st.warning("No users found")
    st.stop()

for u in users:

    col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 2, 2])

    with col1:
        st.write(f"👤 {u.get('name','-')}")

    with col2:
        st.write(u.get("email", "-"))

    with col3:
        role = u.get("role", "staff")
        st.write(f"🛡 {role}")

    with col4:
        new_role = st.selectbox(
            "Change Role",
            ["admin", "staff", "cashier"],
            index=["admin", "staff", "cashier"].index(role),
            key=f"role_{u['id']}"
        )

        if new_role != role:
            supabase.table("users").update({"role": new_role}).eq("id", u["id"]).execute()
            st.rerun()

    with col5:
        if st.button("🗑 Delete", key=f"del_{u['id']}"):
            supabase.table("users").delete().eq("id", u["id"]).execute()
            st.warning("User deleted")
            st.rerun()

st.divider()

# =========================
# SYSTEM INFO PANEL
# =========================
st.subheader("📊 System Summary")

total_users = len(users)
admins = len([u for u in users if u.get("role") == "admin"])
staff = len([u for u in users if u.get("role") == "staff"])

col1, col2, col3 = st.columns(3)
col1.metric("👥 Total Users", total_users)
col2.metric("🛡 Admins", admins)
col3.metric("🧑‍💼 Staff", staff)

st.success("✔ User management system is active")