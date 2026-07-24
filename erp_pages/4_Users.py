import streamlit as st
from database import get_supabase
from auth import require_admin  # Admin Security Guard ထည့်သွင်းခြင်း
import hashlib
from utils.ui import show_table

def run():
    # 2) Admin Security Guard
    require_admin()

    st.title("👥 User Management (Admin Panel)")
    st.caption("Control users, roles and access rights")

    supabase = get_supabase()

    def hash_password(password):
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

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
                        supabase.table("users").insert({
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
            
            c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 2, 1])
            with c1: st.write(f"👤 {u.get('username', '-')}")
            with c2: st.write(u.get('full_name', '-'))
            with c3: st.write(f"🛡 {role_name}")
            with c4:
                new_role = st.selectbox("Role", role_names, index=role_names.index(role_name) if role_name in role_names else 0, key=f"role_{u['id']}")
                
                # 1) Role Update with Try/Except
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

                # Active / Disable Toggle
                status_icon = "✅" if u.get("is_active") else "⛔"

                if st.button(
                    status_icon,
                    key=f"toggle_{u['id']}",
                    help="Toggle Active Status"
                ):

                    try:

                        supabase.table(
                            "users"
                        ).update(
                            {
                                "is_active": not u.get("is_active")
                            }
                        ).eq(
                            "id",
                            u["id"]
                        ).execute()

                        st.rerun()


                    except Exception as e:

                        st.error(
                            f"Status update failed: {e}"
                        )


                # ==========================================
                # HARD DELETE USER
                # ==========================================

                if u.get("username") != "admin":

                    if st.button(
                        "🗑",
                        key=f"delete_{u['id']}",
                        help="Delete User Permanently"
                    ):

                        st.session_state[
                            f"confirm_delete_{u['id']}"
                        ] = True



                    if st.session_state.get(
                        f"confirm_delete_{u['id']}",
                        False
                    ):

                        st.warning(
                            f"Delete {u.get('username')} permanently?"
                        )


                        col_a, col_b = st.columns(2)


                        with col_a:

                            if st.button(
                                "✅ Confirm",
                                key=f"confirm_yes_{u['id']}"
                            ):

                                try:

                                    supabase.table(
                                        "users"
                                    ).delete().eq(
                                        "id",
                                        u["id"]
                                    ).execute()


                                    st.success(
                                        "User deleted successfully"
                                    )


                                    st.session_state[
                                        f"confirm_delete_{u['id']}"
                                    ] = False


                                    st.rerun()


                                except Exception as e:

                                    st.error(
                                        f"Delete failed: {e}"
                                    )


                        with col_b:

                            if st.button(
                                "❌ Cancel",
                                key=f"confirm_no_{u['id']}"
                            ):

                                st.session_state[
                                    f"confirm_delete_{u['id']}"
                                ] = False

                                st.rerun()


                else:

                    st.caption(
                        "🔒 Protected"
                    )
