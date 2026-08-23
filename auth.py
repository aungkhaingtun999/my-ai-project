# ==============================================================================
# auth.py
# ERP ENTERPRISE AUTHENTICATION SYSTEM V30
# SECURITY + ROLE + SESSION MANAGEMENT + MULTI-TENANT
# ==============================================================================

import hashlib
import hmac
import time
from datetime import datetime, timedelta, timezone

import bcrypt
import streamlit as st

# V30 DATABASE CORE
from erp_core.base_repo import db

supabase = db()

# ==================================================
# SECURITY CONSTANTS
# ==================================================

SESSION_IDLE_TIMEOUT = 1800  # 30 Minutes
MAX_FAILED_ATTEMPTS = 5
LOCK_DURATION_MINUTES = 15

# ==================================================
# ROLE CONSTANTS
# ==================================================

ROLE_ADMIN = 1
ROLE_MANAGER = 2
ROLE_CASHIER = 3

ROLE_MAP = {
    ROLE_ADMIN: "Admin",
    ROLE_MANAGER: "Manager",
    ROLE_CASHIER: "Cashier",
}

# ==================================================
# TENANT ROLE CONSTANTS
# ==================================================

TENANT_ROLE_STAFF = "staff"
TENANT_ROLE_MANAGER = "manager"
TENANT_ROLE_ADMIN = "admin"
TENANT_ROLE_OWNER = "owner"

TENANT_ROLE_MAP = {
    TENANT_ROLE_STAFF: "Staff",
    TENANT_ROLE_MANAGER: "Manager",
    TENANT_ROLE_ADMIN: "Admin",
    TENANT_ROLE_OWNER: "Owner",
}

TENANT_ROLE_HIERARCHY = {
    TENANT_ROLE_STAFF: 1,
    TENANT_ROLE_MANAGER: 2,
    TENANT_ROLE_ADMIN: 3,
    TENANT_ROLE_OWNER: 4,
}

# ==================================================
# AUDIT LOGGING
# ==================================================

def log_auth_event(user_id, event_type, status="success"):
    try:
        supabase.table("auth_logs").insert(
            {
                "user_id": user_id,
                "event": event_type,
                "status": status,
                "ip_address": "system",
            }
        ).execute()
    except Exception:
        pass

# ==================================================
# PASSWORD ENGINE
# ==================================================

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(
        password.encode("utf-8"), 
        bcrypt.gensalt()
    ).decode()

def verify_password(user, password):
    stored = user.get("password_hash")

    if not stored:
        return False

    stored = str(stored).strip()

    # bcrypt check
    if stored.startswith("$2"):
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"), stored.encode("utf-8")
            )
        except Exception:
            return False

    # Legacy SHA256 / Plain Migration
    sha256_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    if hmac.compare_digest(stored, sha256_hash) or hmac.compare_digest(
        stored, password
    ):
        upgrade_password(user["id"], password)
        return True

    return False

def upgrade_password(user_id, password):
    try:
        new_hash = hash_password(password)
        supabase.table("users").update({"password_hash": new_hash}).eq(
            "id", user_id
        ).execute()
    except Exception:
        pass

def change_password(user_id, old_password, new_password):
    """Change user password"""
    try:
        if not old_password or not new_password:
            return False, "Old and new passwords are required"
        
        if len(new_password) < 6:
            return False, "New password must be at least 6 characters"
        
        # Get user
        result = (
            supabase.table("users")
            .select("*")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )

        if not result.data:
            return False, "User not found"

        user = result.data[0]

        # Verify old password
        if not verify_password(user, old_password):
            return False, "Old password is incorrect"

        # Hash and update new password
        new_hash = hash_password(new_password)
        
        supabase.table("users").update({"password_hash": new_hash}).eq(
            "id", user_id
        ).execute()

        log_auth_event(user_id, "password_change", "success")
        return True, "Password changed successfully"

    except Exception as e:
        log_auth_event(user_id, "password_change", "failed")
        return False, f"Password change error: {str(e)}"

# ==================================================
# USER QUERY
# ==================================================

def get_user(username):
    try:
        result = (
            supabase.table("users")
            .select("*")
            .eq("username", username.strip())
            .eq("is_active", True)
            .limit(1)
            .execute()
        )

        return result.data[0] if result.data else None

    except Exception:
        st.error("Authentication Database Error")
        return None

# ==================================================
# TENANT CONTEXT BUILDER
# ==================================================

def build_tenant_context(user):
    """Build tenant context from user record"""
    shop_id = user.get("shop_id")
    branch_id = user.get("branch_id")
    tenant_role = user.get("tenant_role", TENANT_ROLE_STAFF)
    
    context = {
        "shop_id": shop_id,
        "branch_id": branch_id,
        "tenant_role": tenant_role,
        "shop_name": None,
        "branch_name": None,
    }
    
    if shop_id:
        try:
            shop_resp = (
                supabase.table("shops")
                .select("name, code")
                .eq("id", shop_id)
                .limit(1)
                .execute()
            )
            
            if shop_resp.data:
                context["shop_name"] = shop_resp.data[0].get("name")
                context["shop_code"] = shop_resp.data[0].get("code")
        except Exception:
            pass
    
    if branch_id:
        try:
            branch_resp = (
                supabase.table("branches")
                .select("name, code")
                .eq("id", branch_id)
                .limit(1)
                .execute()
            )
            
            if branch_resp.data:
                context["branch_name"] = branch_resp.data[0].get("name")
                context["branch_code"] = branch_resp.data[0].get("code")
        except Exception:
            pass
    
    return context

# ==================================================
# LOGIN ENGINE
# ==================================================

def login_user(username, password):
    user = get_user(username)

    if not user:
        return False, "User not found."

    locked_until = user.get("locked_until")

    if locked_until:
        lock_time = datetime.fromisoformat(locked_until.replace("Z", "+00:00"))

        if datetime.now(timezone.utc) < lock_time:
            return False, "Account locked. Try again later."

    if verify_password(user, password):
        supabase.table("users").update(
            {"failed_attempts": 0, "locked_until": None}
        ).eq("id", user["id"]).execute()

        build_session(user)
        log_auth_event(user["id"], "login")
        return True, "Success"

    else:
        attempts = user.get("failed_attempts", 0) + 1
        update_data = {"failed_attempts": attempts}

        if attempts >= MAX_FAILED_ATTEMPTS:
            update_data["locked_until"] = (
                datetime.now(timezone.utc)
                + timedelta(minutes=LOCK_DURATION_MINUTES)
            ).isoformat()

        supabase.table("users").update(update_data).eq(
            "id", user["id"]
        ).execute()

        log_auth_event(user["id"], "login", "failed")
        return False, "Invalid password."

# ==================================================
# SESSION BUILDER
# ==================================================

def build_session(user):
    role_id = int(user.get("role_id", ROLE_CASHIER))
    user_id = user.get("id")
    username = user.get("username") or user.get("email") or "Unknown"
    
    tenant_context = build_tenant_context(user)

    st.session_state.user = {
        "id": user_id,
        "username": username,
        "full_name": user.get("full_name", username),
        "role_id": role_id,
        "role": ROLE_MAP.get(role_id, "Cashier"),
        "is_active": bool(user.get("is_active", True)),
        "last_activity": time.time(),
        "shop_id": tenant_context.get("shop_id"),
        "branch_id": tenant_context.get("branch_id"),
        "tenant_role": tenant_context.get("tenant_role"),
        "shop_name": tenant_context.get("shop_name"),
        "branch_name": tenant_context.get("branch_name"),
    }

    st.session_state["user_id"] = user_id
    st.session_state["username"] = username
    st.session_state["role_id"] = role_id
    st.session_state["shop_id"] = tenant_context.get("shop_id")
    st.session_state["branch_id"] = tenant_context.get("branch_id")
    st.session_state["tenant_role"] = tenant_context.get("tenant_role")
    st.session_state["shop_name"] = tenant_context.get("shop_name")
    st.session_state["branch_name"] = tenant_context.get("branch_name")
    st.session_state["tenant_context"] = tenant_context
    st.session_state["id"] = user_id

# ==================================================
# CURRENT USER & ROLE HELPERS
# ==================================================

def get_current_user():
    return st.session_state.get("user") or {}

def current_user():
    return get_current_user()

def get_current_role_id():
    user = get_current_user()
    if not user:
        return None
    return user.get("role_id")

def get_current_shop_id():
    return st.session_state.get("shop_id")

def get_current_branch_id():
    return st.session_state.get("branch_id")

def get_current_tenant_role():
    return st.session_state.get("tenant_role", TENANT_ROLE_STAFF)

def get_current_tenant_context():
    return st.session_state.get("tenant_context")

def is_shop_owner():
    return get_current_tenant_role() == TENANT_ROLE_OWNER

def is_shop_admin():
    tenant_role = get_current_tenant_role()
    return tenant_role in [TENANT_ROLE_ADMIN, TENANT_ROLE_OWNER]

def is_shop_manager():
    tenant_role = get_current_tenant_role()
    return tenant_role in [TENANT_ROLE_MANAGER, TENANT_ROLE_ADMIN, TENANT_ROLE_OWNER]

# ==================================================
# AUTH GUARDS & PERMISSIONS
# ==================================================

def is_authenticated():
    user = st.session_state.get("user")

    if not user:
        return False

    if not user.get("is_active", False):
        return False

    if (time.time() - user.get("last_activity", 0)) > SESSION_IDLE_TIMEOUT:
        logout()
        return False

    user["last_activity"] = time.time()
    return True

def require_login():
    if not is_authenticated():
        login_page()
        st.stop()
    return current_user()

def require_admin():
    user = require_login()

    if user["role_id"] != ROLE_ADMIN:
        st.error("⛔ Admin privileges required.")
        st.stop()

    return user

def require_role(role_id):
    user = require_login()

    if user["role_id"] != role_id:
        st.error(f"⛔ Requires {ROLE_MAP.get(role_id)}")
        st.stop()

    return user

def require_tenant_role(min_tenant_role):
    user = require_login()
    
    current_tenant_role = user.get("tenant_role", TENANT_ROLE_STAFF)
    current_level = TENANT_ROLE_HIERARCHY.get(current_tenant_role, 0)
    required_level = TENANT_ROLE_HIERARCHY.get(min_tenant_role, 0)
    
    if current_level < required_level:
        st.error(f"⛔ Requires {TENANT_ROLE_MAP.get(min_tenant_role)} or higher.")
        st.stop()
    
    return user

def has_permission(permission_key):
    try:
        role_id = get_current_role_id()

        if not role_id:
            return False

        response = (
            supabase.table("role_permissions")
            .select(
                """
                allowed,
                permissions(
                    permission_key
                )
                """
            )
            .eq("role_id", role_id)
            .execute()
        )

        permissions = response.data or []

        for item in permissions:
            permission = item.get("permissions")

            if permission:
                if permission.get("permission_key") == permission_key:
                    return item.get("allowed", False)

        return False

    except Exception as e:
        st.error(f"Permission check error: {e}")
        return False

# ==================================================
# LOGIN UI
# ==================================================

def login_page():
    st.title("🔐 ERP Enterprise Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        success, msg = login_user(username, password)

        if success:
            st.rerun()
        else:
            st.error(msg)

# ==================================================
# LOGOUT
# ==================================================

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.rerun()

# ==================================================
# SIDEBAR USER PANEL
# ==================================================

def auth_sidebar():
    if is_authenticated():
        user = current_user()

        with st.sidebar:
            st.success(f"👤 {user['full_name']}")
            st.caption(f"Role: {user['role']}")

            tenant_role = user.get("tenant_role")
            shop_name = user.get("shop_name")
            branch_name = user.get("branch_name")

            if tenant_role:
                st.caption(f"Tenant Role: {TENANT_ROLE_MAP.get(tenant_role, tenant_role)}")

            if shop_name:
                st.caption(f"🏪 {shop_name}")

            if branch_name:
                st.caption(f"📍 {branch_name}")

            if st.button("🚪 Logout"):
                logout()
