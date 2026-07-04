# ==========================================
# guards.py (Enterprise RBAC Engine v2)
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
# SESSION SAFE USER NORMALIZER
# =====================================================
def current_user() -> Optional[Dict[str, Any]]:
    user = st.session_state.get("user")

    if not isinstance(user, dict):
        return None

    # normalize missing keys
    return {
        "id": user.get("id"),
        "full_name": user.get("full_name", "Unknown"),
        "username": user.get("username"),
        "role_id": user.get("role_id"),
        "is_active": user.get("is_active", False)
    }


# =====================================================
# LOGIN CHECK (HARD GATE)
# =====================================================
def is_logged_in() -> bool:
    user = current_user()

    if not user:
        return False

    if not user.get("id"):
        return False

    if user.get("is_active") is not True:
        return False

    return True


def require_login():
    if not is_logged_in():
        st.warning("🔐 Login required")
        st.stop()

    return current_user()


# =====================================================
# ROLE RESOLUTION (SAFE)
# =====================================================
def get_role_id() -> int:
    user = require_login()

    try:
        return int(user.get("role_id") or ROLE_CASHIER)
    except:
        return ROLE_CASHIER


def get_role_name() -> str:
    return ROLE_NAME.get(get_role_id(), "Cashier")


# =====================================================
# ROLE CHECKERS
# =====================================================
def is_admin() -> bool:
    return get_role_id() == ROLE_ADMIN


def is_manager() -> bool:
    return get_role_id() == ROLE_MANAGER


def is_cashier() -> bool:
    return get_role_id() == ROLE_CASHIER


# =====================================================
# CORE GUARDS
# =====================================================
def require_admin():
    user = require_login()

    if get_role_id() != ROLE_ADMIN:
        st.error("⛔ Admin Only Access")
        st.stop()

    return user


def require_manager():
    user = require_login()

    if get_role_id() not in (ROLE_ADMIN, ROLE_MANAGER):
        st.error("⛔ Manager Access Required")
        st.stop()

    return user


def require_cashier():
    return require_login()


def require_role(*roles: Tuple[int]):
    user = require_login()

    if get_role_id() not in roles:
        allowed = ", ".join([ROLE_NAME.get(r, str(r)) for r in roles])

        st.error("⛔ Permission Denied")
        st.caption(f"Allowed: {allowed}")
        st.stop()

    return user


# =====================================================
# PERMISSION ENGINE (FUTURE RBAC READY)
# =====================================================

# in-memory cache (fast ERP performance)
_PERMISSION_CACHE: Dict[int, Set[str]] = {}


def load_permissions(role_id: int) -> Set[str]:
    """
    FUTURE: replace with DB lookup
    """
    if role_id in _PERMISSION_CACHE:
        return _PERMISSION_CACHE[role_id]

    # default static permissions (MVP fallback)
    default = {
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

    perms = default.get(role_id, set())
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
# SAFE PAGE HEADER
# =====================================================
def page_header(title: str, icon: str = "📄"):
    user = require_login()

    st.title(f"{icon} {title}")

    st.caption(
        f"User: {user.get('full_name')} | Role: {get_role_name()}"
    )


# =====================================================
# DEBUG PANEL
# =====================================================
def debug_user():
    st.subheader("🔍 DEBUG USER")
    st.json(current_user())

    st.subheader("🔐 PERMISSIONS")
    st.write(load_permissions(get_role_id()))
