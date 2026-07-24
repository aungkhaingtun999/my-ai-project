import streamlit as st
from database import get_supabase
from auth import require_admin  # Admin Security Guard ထည့်သွင်းခြင်း
import hashlib
from utils.ui import show_table
from utils.notification import (
    notify_success,
    notify_error,
    show_notification
)
def run():

    show_notification()

    require_admin()

    st.title("👥 User Management")
def run():
    # 2) Admin Security Guard
    require_admin()

    st.title("👥 User Management (Admin Panel)")
    st.caption("Control users, roles and access rights")

    supabase = get_supabase()

    def hash_password(password):
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    # User Activity Log Helper Function
    def create_activity_log(user_id, action, description):
        try:
            supabase.table("user_activity_logs").insert({
                "user_id": user_id,
                "action": action,
                "description": description
            }).execute()
        except Exception as e:
            st.warning(f"Activity log failed: {e}")

    # 3) Optimized Data Fetching (select id, name)
    try:
        roles_resp = supabase.table("roles").select("id,name").execute()
        roles = roles_resp.data or []
    except Exception as e:
        st.error(f"Role loading failed: {e}")
        return

    if not roles:
        st.warning("Roles table is empty. Please create roles first.")
        return

    role_map = {r["name"]: r["id"] for r in roles}
    role_names = list(role_map.keys())

    try:
        users_resp = supabase.table("users").select("id, username, full_name, role_id, is_active").execute()
        users = users_resp.data or []
    except Exception as e:
        st.error(f"User loading failed: {e}")
        return

    # Search
    search = st.text_input("🔍 Search User")
    if search:
        search = search.lower()
        users = [u for u in users if search in str(u.get("username","")).lower() or search in str(u.get("full_name","")).lower()]

    # Create User
    with st.expander("➕ Create New User"):
        with st.form("create_user_form"):
            username = st.text_input("Username")
            full_name = st.text_input("Full Name")
            password = st.text_input("Password", type="password")
            selected_role = st.selectbox("Role", role_names)
            active = st.checkbox("Active", value=True)
            submit = st.form_submit_button("Create User")

            if submit:
                if not username or not password:
                    st.error("Username and password required")
                else:
                    try:
                        res = supabase.table("users").insert({
                            "username": username,
                            "full_name": full_name,
                            "password_hash": hash_password(password),
                            "role_id": role_map[selected_role],
                            "is_active": active
                        }).execute()
                        
                        st.success("User created successfully")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Create user failed: {e}")

    st.divider()

    # User List
    st.subheader("📋 Users")
    if not users:
        st.info("No users found")
    else:
        for u in users:
            role_name = next((r["name"] for r in roles if r["id"] == u["role_id"]), "Unknown")
            
            # Column ကို (6) ခု အဖြစ် ပြောင်းလဲထားခြင်း
            c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 2, 2, 1, 1])
            
            with c1: 
                st.write(f"👤 {u.get('username', '-')}")
            
            with c2: 
                st.write(u.get('full_name', '-'))
            
            with c3: 
                st.write(f"🛡 {role_name}")
            
            with c4:
                new_role = st.selectbox(
                    "Role", 
                    role_names, 
                    index=role_names.index(role_name) if role_name in role_names else 0, 
                    key=f"role_{u['id']}"
                )
                
                # Role Update with Try/Except
                if new_role != role_name:
                    try:
                        supabase.table("users").update({
                            "role_id": role_map[new_role]
                        }).eq("id", u["id"]).execute()
                        st.success("Role updated")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Role update failed: {e}")

            with c5:
                # Reset Password Button
                if st.button("🔐", key=f"reset_{u['id']}", help="Reset Password"):
                    st.session_state[f"reset_user_{u['id']}"] = True

            with c6:
                if u.get("username") != "admin":
                    if u.get("is_active"):
                        if st.button("🚫", key=f"disable_{u['id']}", help="Disable User"):
                            try:
                                supabase.table("users").update({"is_active": False}).eq("id", u["id"]).execute()
                                
                                # Log Activity
                                create_activity_log(
                                    st.session_state.get("user_id"),
                                    "DISABLE_USER",
                                    f"Disabled user {u['username']}"
                                )
                                
                                st.success("User disabled")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Disable failed: {e}")
                    else:
                        if st.button("🔄", key=f"restore_{u['id']}", help="Restore User"):
                            try:
                                supabase.table("users").update({"is_active": True}).eq("id", u["id"]).execute()
                                
                                # Log Activity
                                create_activity_log(
                                    st.session_state.get("user_id"),
                                    "RESTORE_USER",
                                    f"Restored user {u['username']}"
                                )
                                
                                st.success("User restored")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Restore failed: {e}")
                else:
                    st.caption("🔒 Protected")

            # Reset Password Input Dialog
            if st.session_state.get(f"reset_user_{u['id']}", False):
                with st.expander(f"🔐 Reset Password : {u['username']}", expanded=True):
                    new_password = st.text_input("New Password", type="password", key=f"newpass_{u['id']}")
                    if st.button("💾 Save Password", key=f"savepass_{u['id']}"):
                        if not new_password:
                            st.error("Password required")
                        else:
                            try:
                                supabase.table("users").update({
                                    "password_hash": hash_password(new_password)
                                }).eq("id", u["id"]).execute()
                                
                                # Log Activity
                                create_activity_log(
                                    st.session_state.get("user_id"),
                                    "RESET_PASSWORD",
                                    f"Reset password for {u['username']}"
                                )
                                
                                st.success("Password reset successfully")
                                st.session_state[f"reset_user_{u['id']}"] = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Reset password failed: {e}")

    # Summary
    st.divider()
    st.subheader("📊 System Summary")
    total = len(users)
    active_count = len([u for u in users if u.get("is_active")])
    c1, c2, c3 = st.columns(3)
    c1.metric("👥 Total Users", total)
    c2.metric("✅ Active", active_count)
    c3.metric("⛔ Disabled", total - active_count)

    # Activity Log Viewer
    st.divider()
    st.subheader("📝 User Activity Log")
    try:
        logs = (
            supabase
            .table("user_activity_logs")
            .select("*")
            .order("created_at", desc=True)
            .limit(100)
            .execute()
        )
        activity_logs = logs.data or []
        if activity_logs:
            st.dataframe(activity_logs, use_container_width=True)
        else:
            st.info("No activity logs found")
    except Exception as e:
        st.error(f"Activity log loading failed: {e}")

    # Permission Matrix
    st.divider()
    st.subheader("👑 Permission Matrix")
    try:
        permissions = (
            supabase
            .table("permissions")
            .select("*")
            .execute()
            .data
            or []
        )

        if permissions:
            for role in roles:
                st.markdown(f"### 🛡 {role['name']}")

                for perm in permissions:
                    current = (
                        supabase
                        .table("role_permissions")
                        .select("allowed")
                        .eq("role_id", role["id"])
                        .eq("permission_id", perm["id"])
                        .execute()
                    )

                    allowed = False
                    if current.data:
                        allowed = current.data[0]["allowed"]

                    new_value = st.checkbox(
                        perm["permission_name"],
                        value=allowed,
                        key=f"{role['id']}_{perm['id']}"
                    )

                    if new_value != allowed:
                        exists = current.data

                        if exists:
                            supabase.table("role_permissions").update({
                                "allowed": new_value
                            }).eq("role_id", role["id"]).eq("permission_id", perm["id"]).execute()
                        else:
                            supabase.table("role_permissions").insert({
                                "role_id": role["id"],
                                "permission_id": perm["id"],
                                "allowed": new_value
                            }).execute()

                        st.rerun()
        else:
            st.info("No permissions found in database.")

    except Exception as e:
        st.error(f"Permission Matrix Error: {e}")

if __name__ == "__main__":
    run()
