# ==============================================================================
# auth.py
# ERP ENTERPRISE AUTHENTICATION SYSTEM V30
# SECURITY + ROLE + SESSION MANAGEMENT
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

def verify_password(user, password):
    stored = user.get("password_hash")

    if not stored:
        return False

    stored = str(stored).strip()

    # ---------------------------------
    # bcrypt
    # ---------------------------------
    if stored.startswith("$2"):
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"), stored.encode("utf-8")
            )
        except Exception:
            return False

    # ---------------------------------
    # Legacy SHA256 / Plain Migration
    # ---------------------------------
    sha256_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    if hmac.compare_digest(stored, sha256_hash) or hmac.compare_digest(
        stored, password
    ):
        upgrade_password(user["id"], password)
        return True

    return False

def upgrade_password(user_id, password):
    try:
        new_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode()

        supabase.table("users").update({"password_hash": new_hash}).eq(
            "id", user_id
        ).execute()

    except Exception:
        pass

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
    """Build session with user and shop context"""
    
    role_id = int(user.get("role_id", ROLE_CASHIER))
    user_id = user.get("id")
    username = user.get("username") or user.get("email") or "Unknown"
    
    # Extract shop context
    shop_id = user.get("shop_id")
    branch_id = user.get("branch_id")
    tenant_role = user.get("tenant_role", "staff")
    
    st.session_state.user = {
        "id": user_id,
        "username": username,
        "full_name": user.get("full_name", username),
        "role_id": role_id,
        "role": ROLE_MAP.get(role_id, "Cashier"),
        "is_active": bool(user.get("is_active", True)),
        "last_activity": time.time(),
        # Multi-tenant fields
        "shop_id": shop_id,
        "branch_id": branch_id,
        "tenant_role": tenant_role,
        "is_owner": tenant_role in ["owner", "admin"] or role_id == ROLE_ADMIN,
        "is_manager": tenant_role in ["manager", "admin", "owner"] or role_id in [ROLE_ADMIN, ROLE_MANAGER],
    }
    
    # Session state for backward compatibility
    st.session_state["user_id"] = user_id
    st.session_state["username"] = username
    st.session_state["role_id"] = role_id
    st.session_state["id"] = user_id
    
    # Shop context in session
    if shop_id:
        st.session_state["shop_id"] = shop_id
        st.session_state["store_id"] = shop_id
    
    if branch_id:
        st.session_state["branch_id"] = branch_id
    
    if tenant_role:
        st.session_state["tenant_role"] = tenant_role
    
    st.session_state["is_owner"] = (
        tenant_role in ["owner", "admin"] or role_id == ROLE_ADMIN
    )
    st.session_state["is_manager"] = (
        tenant_role in ["manager", "admin", "owner"] 
        or role_id in [ROLE_ADMIN, ROLE_MANAGER]
    )

# ==================================================
# CURRENT USER & ROLE HELPERS
# ==================================================

def get_current_user():
    """Get current user with enhanced context"""
    user = st.session_state.get("user") or {}
    
    # Ensure shop context is available
    if user and not user.get("shop_id"):
        shop_id = st.session_state.get("shop_id")
        if shop_id:
            user["shop_id"] = shop_id
    
    return user

def current_user():
    return get_current_user()

def get_current_role_id():
    user = get_current_user()
    if not user:
        return None
    return user.get("role_id")

# ==================================================
# SHOP/STORE CONTEXT HELPERS (MULTI-TENANT)
# ==================================================

def get_current_shop_id():
    """Get the current shop/store ID from session state"""
    # Check multiple possible session keys for shop ID
    shop_id = (
        st.session_state.get("shop_id") 
        or st.session_state.get("store_id")
        or st.session_state.get("current_shop_id")
    )
    
    # If no shop ID in session, try to get from user data
    if not shop_id:
        user = get_current_user()
        if user:
            shop_id = user.get("shop_id")
            if shop_id:
                st.session_state["shop_id"] = shop_id
    
    return shop_id

def set_current_shop_id(shop_id):
    """Set the current shop/store ID in session state"""
    st.session_state["shop_id"] = shop_id
    st.session_state["store_id"] = shop_id  # For backward compatibility

def get_current_shop():
    """Get the current shop details from database"""
    shop_id = get_current_shop_id()
    if not shop_id:
        return None
    
    try:
        result = (
            supabase.table("shops")
            .select("*")
            .eq("id", shop_id)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception:
        return None

def is_shop_owner():
    """Check if current user is a shop owner or system admin"""
    user = get_current_user()
    
    if not user:
        return False
    
    # System admin (role_id 1) has full access
    if user.get("role_id") == ROLE_ADMIN:
        return True
    
    # Check tenant_role for owner
    tenant_role = user.get("tenant_role", "").lower()
    if tenant_role in ["owner", "admin"]:
        return True
    
    # Check if user has owner role in session
    return st.session_state.get("is_owner", False)

def is_shop_manager():
    """Check if current user is a shop manager or higher"""
    user = get_current_user()
    
    if not user:
        return False
    
    # System admin or owner
    if is_shop_owner():
        return True
    
    # Check tenant_role for manager
    tenant_role = user.get("tenant_role", "").lower()
    if tenant_role in ["manager", "admin", "owner"]:
        return True
    
    return False

def get_user_shops():
    """Get all shops accessible to current user"""
    user = get_current_user()
    
    if not user:
        return []
    
    try:
        if is_shop_owner():
            # Owner/admin can access all shops
            result = supabase.table("shops").select("*").execute()
        else:
            # Regular users can only access their shop
            shop_id = get_current_shop_id()
            if not shop_id:
                return []
            
            result = (
                supabase.table("shops")
                .select("*")
                .eq("id", shop_id)
                .execute()
            )
        
        return result.data or []
    
    except Exception:
        return []

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
# PASSWORD MANAGEMENT
# ==================================================

def change_password(user_id, old_password, new_password):
    try:
        # Current user load
        result = (
            supabase.table("users")
            .select("*")
            .eq("id", user_id)
            .single()
            .execute()
        )

        user = result.data

        if not user:
            return False, "User not found"

        # Verify old password
        if not verify_password(user, old_password):
            return False, "Old password is incorrect"

        # Hash new password
        new_hash = hashlib.sha256(new_password.encode("utf-8")).hexdigest()

        # Update
        (
            supabase.table("users")
            .update({"password_hash": new_hash})
            .eq("id", user_id)
            .execute()
        )

        return True, "Password changed successfully"

    except Exception as e:
        return False, str(e)

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
            
            # Show shop info if available
            shop_id = get_current_shop_id()
            if shop_id:
                shop = get_current_shop()
                if shop:
                    st.caption(f"🏪 Shop: {shop.get('name', 'N/A')}")

            if st.button("🚪 Logout"):
                logout()
