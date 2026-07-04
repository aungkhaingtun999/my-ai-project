# ==========================================
# guards.py (Enterprise RBAC Engine v3 - FINAL)
# ==========================================

import streamlit as st
from typing import Optional, Dict, Any, Tuple, Set

# =====================================================
# ROLE CONSTANTS
# =====================================================
ROLE_ADMIN = 1
ROLE_MANAGER = 2
ROLE_CASHIER = 3

ROLE_NAME = {
    ROLE_ADMIN: "Admin",
    ROLE_MANAGER: "Manager",
    ROLE_CASHIER: "Cashier"
}

# =====================================================
# BACKWARD COMPATIBILITY ALIAS (IMPORTANT FIX)
# =====================================================

# 🔥 This prevents your ImportError immediately
def get_current_user():
    return current_user()

# =====================================================
# SAFE USER NORMALIZER
# =====================================================
def current_user() -> Optional[Dict[str, Any]]:
    user = st.session_state.get("user")

    if not isinstance(user, dict):
        return None

    return {
        "id": user.get("id"),
        "full_name": user.get("full_name") or user.get("name") or "Unknown",
        "username": user.get("username"),
        "role_id": safe_int(user.get("role_id"), ROLE_CASHIER),
        "is_active": bool(user.get("is_active", False))
    }


# =====================================================
# SAFE INT HELPER
# =====================================================
def safe_int(value, default=0):
    try:
        return int(value)
    except:
        return default


# =====================================================
# LOGIN CHECK (HARD GATE)
# =====================================================
def is_logged_in() -> bool:
    user = current_user()

    return bool(
        user and
        user.get("id") and
        user.get("is_active") is True
    )


def require_login():
    if not is_logged_in():
        st.warning("🔐 Please login first")
        st.stop()

    return current_user()


# =====================================================
# ROLE ENGINE
# =====================================================
def get_role_id() -> int:
    user = require_login()
    return safe_int(user.get("role_id"), ROLE_CASHIER)


def get_role_name() -> str:
    return ROLE_NAME.get(get_role_id(), "Cashier")


# =====================================================
# ROLE CHECKERS
# =====================================================
def is_admin(): return get_role_id() == ROLE_ADMIN
def is_manager(): return get_role_id() == ROLE_MANAGER
def is_cashier(): return get_role_id() == ROLE_CASHIER


# =====================================================
# CORE GUARDS
# =====================================================
def require_admin():
    user = require_login()

    if get_role_id() != ROLE_ADMIN:
        st.error("⛔ Admin Only")
        st.stop()

    return user


def require_manager():
    user = require_login()

    if get_role_id() not in (ROLE_ADMIN, ROLE_MANAGER):
        st.error("⛔ Manager Required")
        st.stop()

    return user


def require_role(*roles: Tuple[int]):
    user = require_login()

    if get_role_id() not in roles:
        allowed = ", ".join([ROLE_NAME.get(r, str(r)) for r in roles])
        st.error("⛔ Permission Denied")
        st.caption(f"Allowed: {allowed}")
        st.stop()

    return user


# =====================================================
# PERMISSION ENGINE (CACHE + FUTURE DB READY)
# =====================================================
_PERMISSION_CACHE: Dict[int, Set[str]] = {}


def load_permissions(role_id: int) -> Set[str]:

    if role_id in _PERMISSION_CACHE:
        return _PERMISSION_CACHE[role_id]

    default_permissions = {
        ROLE_ADMIN: {
            "sales.create",
            "sales.refund",
            "inventory.edit",
            "users.manage",
            "reports.view",
        },
        ROLE_MANAGER: {
            "sales.create",
            "inventory.view",
            "reports.view",
        },
        ROLE_CASHIER: {
            "sales.create",
        }
    }

    perms = default_permissions.get(role_id, set())
    _PERMISSION_CACHE[role_id] = perms

    return perms


def require_permission(permission: str):
    user = require_login()

    role_id = get_role_id()
    permissions = load_permissions(role_id)

    if permission not in permissions:
        st.error("⛔ Permission Denied")
        st.caption(f"Required: {permission}")
        st.stop()

    return user


# =====================================================
# PAGE HEADER
# =====================================================
def page_header(title: str, icon: str = "📄"):
    user = require_login()

    st.title(f"{icon} {title}")
    st.caption(f"{user.get('full_name')} | {get_role_name()}")


# =====================================================
# DEBUG PANEL
# =====================================================
def debug_user():
    st.subheader("🔍 USER DEBUG")
    st.json(current_user())

    st.subheader("🔐 PERMISSIONS")
    st.write(load_permissions(get_role_id()))
