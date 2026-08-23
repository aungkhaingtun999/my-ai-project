# ==============================================================================
# models/user.py
# USER MODEL + MULTI-TENANT FILTER + BADGE
# ==============================================================================

import pandas as pd
import streamlit as st

# Import hash_password directly from auth to keep bcrypt standard consistent
from auth import (
    require_admin,
    get_current_shop_id,
    is_shop_owner,
    get_current_user,
    get_current_tenant_role,
    hash_password,
)
from database import get_supabase
from utils.notification import (
    notify_error,
    notify_success,
    show_notification,
)


# ==============================================================================
# TENANT ROLE BADGES
# ==============================================================================

TENANT_ROLE_BADGES = {
    "owner": "👑 Owner",
    "admin": "🛡 Admin",
    "manager": "📊 Manager",
    "staff": "👤 Staff",
}


def get_tenant_role_badge(tenant_role):
    return TENANT_ROLE_BADGES.get(tenant_role, tenant_role)


# ==============================================================================
# PAGE
# ==============================================================================

def run():

    # Notification
    show_notification()

    # Admin Guard
    require_admin()

    st.title("👥 User Management (Admin Panel)")
    st.caption("Control users, roles and access rights")

    supabase = get_supabase()

    # Get current user and shop info
    current_user = get_current_user()
    current_shop_id = get_current_shop_id()
    is_owner = is_shop_owner()

    # --------------------------------------------------------------------------
    # ACTIVITY LOG
    # --------------------------------------------------------------------------

    def create_activity_log(user_id, action, description):
        try:
            supabase.table("user_activity_logs").insert(
                {
                    "user_id": user_id,
                    "action": action,
                    "description": description,
                }
            ).execute()
        except Exception:
            pass

    # --------------------------------------------------------------------------
    # LOAD ROLES
    # --------------------------------------------------------------------------

    try:
        roles_resp = (
            supabase.table("roles")
            .select("id,name")
            .execute()
        )
        roles = roles_resp.data or []
    except Exception as e:
        st.error(f"Role loading failed: {e}")
        return

    if not roles:
        st.warning("Roles table is empty. Please create roles first.")
        return

    role_map = {r["name"]: r["id"] for r in roles}
    role_names = list(role_map.keys())

    # --------------------------------------------------------------------------
    # LOAD SHOPS (for shop selection)
    # --------------------------------------------------------------------------

    try:
        if is_owner:
            shops_resp = supabase.table("shops").select("id,name,code").execute()
        else:
            shops_resp = supabase.table("shops").select("id,name,code").eq("id", current_shop_id).execute()

        shops = shops_resp.data or []
    except Exception:
        shops = []

    shop_map = {s["name"]: s["id"] for s in shops}
    shop_names = list(shop_map.keys())

    # --------------------------------------------------------------------------
    # LOAD BRANCHES
    # --------------------------------------------------------------------------

    try:
        if is_owner:
            branches_resp = supabase.table("branches").select("id,name,shop_id,code").execute()
        else:
            branches_resp = supabase.table("branches").select("id,name,shop_id,code").eq("shop_id", current_shop_id).execute()

        branches = branches_resp.data or []
    except Exception:
        branches = []

    # --------------------------------------------------------------------------
    # LOAD USERS (Multi-Tenant with Isolation)
    # --------------------------------------------------------------------------

    try:
        query = supabase.table("users").select(
            "id, username, full_name, role_id, is_active, shop_id, branch_id, tenant_role"
        )

        is_system_admin = bool(current_user.get("is_system_admin", False))

        if not is_system_admin:
            if current_shop_id:
                query = query.eq(
                    "shop_id",
                    current_shop_id
                )
            else:
                query = query.eq(
                    "id",
                    "00000000-0000-0000-0000-000000000000"
                )

        users_resp = query.execute()
        users = users_resp.data or []

    except Exception as e:
        st.error(f"User loading failed: {e}")
        return

    # --------------------------------------------------------------------------
    # MULTI-TENANT FILTERS
    # --------------------------------------------------------------------------

    st.divider()

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        if is_owner and len(shops) > 1:
            filter_shop_options = ["All Shops"] + shop_names
            selected_filter_shop = st.selectbox(
                "🏪 Filter by Shop",
                filter_shop_options,
            )
        else:
            selected_filter_shop = shops[0]["name"] if shops else "All Shops"

    with filter_col2:
        if selected_filter_shop != "All Shops":
            filter_shop_id = shop_map.get(selected_filter_shop)
            filter_branch_options = [
                b for b in branches
                if b.get("shop_id") == filter_shop_id
            ]
        else:
            filter_branch_options = branches

        branch_filter_names = ["All Branches"] + [b["name"] for b in filter_branch_options]
        selected_filter_branch = st.selectbox(
            "📍 Filter by Branch",
            branch_filter_names,
        )

    with filter_col3:
        tenant_role_filter_options = ["All Roles", "👑 Owner", "🛡 Admin", "📊 Manager", "👤 Staff"]
        selected_filter_tenant_role = st.selectbox(
            "🛡 Filter by Tenant Role",
            tenant_role_filter_options,
        )

    filtered_users = users.copy()

    if selected_filter_shop != "All Shops":
        filter_shop_id = shop_map.get(selected_filter_shop)
        filtered_users = [
            u for u in filtered_users
            if u.get("shop_id") == filter_shop_id
        ]

    if selected_filter_branch != "All Branches":
        filtered_users = [
            u for u in filtered_users
            if u.get("branch_id") in [
                b["id"] for b in filter_branch_options
                if b["name"] == selected_filter_branch
            ]
        ]

    if selected_filter_tenant_role != "All Roles":
        role_key = selected_filter_tenant_role.split(" ")[-1].lower()
        filtered_users = [
            u for u in filtered_users
            if u.get("tenant_role", "staff") == role_key
        ]

    # --------------------------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------------------------

    search = st.text_input("🔍 Search User")

    if search:
        search = search.lower()
        filtered_users = [
            u
            for u in filtered_users
            if search in str(u.get("username", "")).lower()
            or search in str(u.get("full_name", "")).lower()
        ]

    st.divider()

    # --------------------------------------------------------------------------
    # CREATE USER (Multi-Tenant with Duplicate Check)
    # --------------------------------------------------------------------------

    with st.expander("➕ Create New User"):

        with st.form("create_user_form"):

            username = st.text_input("Username")
            full_name = st.text_input("Full Name")
            password = st.text_input("Password", type="password")

            if len(shops) > 1 and is_owner:
                selected_shop = st.selectbox("Shop", shop_names)
                selected_shop_id = shop_map[selected_shop]
            else:
                selected_shop_id = shops[0]["id"] if shops else None
                if shops:
                    st.info(f"🏪 Shop: {shops[0]['name']}")

            if selected_shop_id:
                branch_options = [b for b in branches if b.get("shop_id") == selected_shop_id]
            else:
                branch_options = []

            branch_names = [b["name"] for b in branch_options] if branch_options else ["No Branch"]
            selected_branch = st.selectbox("Branch", branch_names)
            selected_branch_index = branch_names.index(selected_branch)
            selected_branch_id = branch_options[selected_branch_index]["id"] if branch_options and selected_branch != "No Branch" else None

            tenant_role = st.selectbox(
                "Tenant Role",
                ["staff", "manager", "admin", "owner"],
                help="staff=Normal user, manager=Can manage team, admin=Can manage shop, owner=Full access"
            )

            selected_role = st.selectbox("Role", role_names)
            active = st.checkbox("Active", value=True)

            submit = st.form_submit_button("Create User")

            if submit:

                if not username or not password:
                    notify_error("Username and password required")
                else:
                    try:
                        existing = supabase.table("users").select("id").eq("username", username).execute()

                        if existing.data and len(existing.data) > 0:
                            notify_error(f"❌ Username '{username}' already exists. Please choose a different username.")
                        else:
                            # Use auth.hash_password (bcrypt) instead of sha256
                            supabase.table("users").insert(
                                {
                                    "username": username,
                                    "full_name": full_name,
                                    "password_hash": hash_password(password),
                                    "role_id": role_map[selected_role],
                                    "shop_id": selected_shop_id,
                                    "branch_id": selected_branch_id,
                                    "tenant_role": tenant_role,
                                    "is_active": active,
                                }
                            ).execute()

                            notify_success(f"✅ User '{username}' created successfully")
                            st.rerun()

                    except Exception as e:
                        error_msg = str(e)
                        if "duplicate key value violates unique constraint" in error_msg:
                            notify_error(f"❌ Username '{username}' already exists. Please choose a different username.")
                        else:
                            notify_error(f"❌ Create user failed: {e}")

    st.divider()

    # ==============================================================================
    # USER TABLE (Multi-Tenant with Badges)
    # ==============================================================================

    st.subheader("📋 Users")

    if is_owner:
        st.caption(
            f"Showing: {selected_filter_shop} → {selected_filter_branch} → {selected_filter_tenant_role}"
        )

    if not filtered_users:
        st.info("No users found with current filters")
    else:
        table_rows = []

        for u in filtered_users:
            role_name = next(
                (
                    r["name"]
                    for r in roles
                    if r["id"] == u["role_id"]
                ),
                "Unknown",
            )

            shop_name = next(
                (s["name"] for s in shops if s["id"] == u.get("shop_id")),
                "N/A",
            )

            branch_name = next(
                (b["name"] for b in branches if b["id"] == u.get("branch_id")),
                "N/A",
            )

            tenant_role = u.get("tenant_role", "staff")
            tenant_role_badge = get_tenant_role_badge(tenant_role)

            is_cross_shop = (
                is_owner
                and u.get("shop_id")
                and u.get("shop_id") != current_shop_id
            )

            table_rows.append(
                {
                    "Username": u.get("username"),
                    "Full Name": u.get("full_name"),
                    "Shop": shop_name,
                    "Branch": branch_name,
                    "Tenant Role": tenant_role_badge,
                    "Role": role_name,
                    "Status": (
                        "🟢 Active"
                        if u.get("is_active")
                        else "🔴 Disabled"
                    ),
                    "Scope": (
                        "⚠️ Other Shop"
                        if is_cross_shop
                        else "✅ Current Shop"
                    ),
                }
            )

        df_users = pd.DataFrame(table_rows)

        st.dataframe(
            df_users,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        # ----------------------------------------------------------------------
        # EDIT USER (Multi-Tenant)
        # ----------------------------------------------------------------------

        st.subheader("✏ Edit User")

        user_options = {
            str(u["id"]): f"{u['username']} - {u['full_name']}"
            for u in filtered_users
        }

        selected_user_id = st.selectbox(
            "Select User",
            options=list(user_options.keys()),
            format_func=lambda x: user_options[x],
        )

        selected_user = next(
            (
                u
                for u in filtered_users
                if str(u["id"]) == selected_user_id
            ),
            None,
        )

        if selected_user:
            selected_shop_name = next(
                (s["name"] for s in shops if s["id"] == selected_user.get("shop_id")),
                "N/A",
            )
            selected_branch_name = next(
                (b["name"] for b in branches if b["id"] == selected_user.get("branch_id")),
                "N/A",
            )

            info_col1, info_col2, info_col3 = st.columns(3)
            info_col1.info(f"🏪 Shop: {selected_shop_name}")
            info_col2.info(f"📍 Branch: {selected_branch_name}")
            info_col3.info(f"🛡 Tenant Role: {get_tenant_role_badge(selected_user.get('tenant_role', 'staff'))}")

            if is_owner and selected_user.get("shop_id") != current_shop_id:
                st.warning("⚠️ This user belongs to another shop. Changes will affect that shop only.")

            current_role_name = next(
                (
                    r["name"]
                    for r in roles
                    if r["id"] == selected_user["role_id"]
                ),
                role_names[0],
            )

            new_full_name = st.text_input(
                "Full Name",
                value=selected_user.get("full_name", ""),
            )

            new_role = st.selectbox(
                "Role",
                role_names,
                index=role_names.index(current_role_name),
            )

            if is_owner and len(shops) > 1:
                current_shop_name = next(
                    (s["name"] for s in shops if s["id"] == selected_user.get("shop_id")),
                    shop_names[0] if shop_names else ""
                )
                new_shop = st.selectbox(
                    "Shop",
                    shop_names,
                    index=shop_names.index(current_shop_name) if current_shop_name in shop_names else 0
                )
                new_shop_id = shop_map[new_shop]
            else:
                new_shop_id = selected_user.get("shop_id") or current_shop_id

            if new_shop_id:
                branch_options = [b for b in branches if b.get("shop_id") == new_shop_id]
            else:
                branch_options = []

            branch_names = [b["name"] for b in branch_options] if branch_options else ["No Branch"]
            current_branch_name = next(
                (b["name"] for b in branches if b["id"] == selected_user.get("branch_id")),
                branch_names[0] if branch_names else "No Branch"
            )

            if branch_names:
                new_branch = st.selectbox(
                    "Branch",
                    branch_names,
                    index=branch_names.index(current_branch_name) if current_branch_name in branch_names else 0
                )
                new_branch_index = branch_names.index(new_branch)
                new_branch_id = branch_options[new_branch_index]["id"] if branch_options else None
            else:
                new_branch_id = None
                st.info("No branches available")

            current_tenant_role = selected_user.get("tenant_role", "staff")
            tenant_role_options = ["staff", "manager", "admin", "owner"]
            new_tenant_role = st.selectbox(
                "Tenant Role",
                tenant_role_options,
                index=tenant_role_options.index(current_tenant_role) if current_tenant_role in tenant_role_options else 0,
                help="staff=Normal user, manager=Can manage team, admin=Can manage shop, owner=Full access"
            )

            new_active = st.toggle("Active", value=selected_user.get("is_active", True))

            col1, col2 = st.columns(2)

            with col1:
                if st.button("💾 Update User", use_container_width=True):
                    try:
                        update_data = {
                            "full_name": new_full_name,
                            "role_id": role_map[new_role],
                            "shop_id": new_shop_id,
                            "branch_id": new_branch_id,
                            "tenant_role": new_tenant_role,
                            "is_active": new_active,
                        }

                        supabase.table("users").update(update_data).eq("id", selected_user_id).execute()

                        create_activity_log(
                            st.session_state.get("user_id"),
                            "UPDATE_USER",
                            f"Updated user {selected_user['username']}",
                        )

                        notify_success(f"✅ User '{selected_user['username']}' updated successfully")
                        st.rerun()

                    except Exception as e:
                        notify_error(f"❌ Update user failed: {e}")

            with col2:
                if st.button("🗑 Delete User", use_container_width=True):
                    try:
                        if str(selected_user_id) == str(st.session_state.get("user_id")):
                            notify_error("❌ You cannot delete your own account")
                        else:
                            supabase.table("users").delete().eq("id", selected_user_id).execute()

                            create_activity_log(
                                st.session_state.get("user_id"),
                                "DELETE_USER",
                                f"Deleted user {selected_user['username']}",
                            )

                            notify_success(f"✅ User '{selected_user['username']}' deleted successfully")
                            st.rerun()

                    except Exception as e:
                        notify_error(f"❌ Delete user failed: {e}")
