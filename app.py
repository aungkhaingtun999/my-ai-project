# ==============================================================================
# app.py
# ERP ENTERPRISE APPLICATION CONTROLLER
# SAFE PAGE ROUTER v31.0
#
# FIXES
# ------------------------------------------------------------------------------
# 1. Auth compatibility for change_password
# 2. Dynamic page cache isolation
# 3. Runtime import stability
# 4. Safe page loading
# 5. Existing login / sidebar flow preserved
# ==============================================================================

import os
import sys
import time
import importlib
import importlib.util

import streamlit as st


# ==============================================================================
# PATH
# ==============================================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

if BASE_DIR not in sys.path:
    sys.path.insert(
        0,
        BASE_DIR
    )


# ==============================================================================
# STREAMLIT PAGE CONFIG
# MUST BE BEFORE OTHER STREAMLIT COMMANDS
# ==============================================================================

st.set_page_config(
    page_title="Myanmar ERP Enterprise",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==============================================================================
# ERP CORE INITIALIZE
# ==============================================================================

import erp_core


# ==============================================================================
# AUTH IMPORT
# ==============================================================================
#
# IMPORTANT
# ------------------------------------------------------------------------------
# Import the auth MODULE itself instead of importing change_password directly.
#
# This protects old Profile pages such as:
#
#     from auth import get_current_user, change_password
#
# even if a stale deployed Profile.py is still being loaded.
#
# ==============================================================================

import auth


# ==============================================================================
# CHANGE PASSWORD COMPATIBILITY PATCH
# ==============================================================================
#
# The current auth.py supplied by the project already contains
# change_password().
#
# This block is intentionally defensive.
#
# If the deployed runtime somehow loads an older auth.py without
# change_password, we add a working implementation at runtime.
#
# This prevents:
#
#     ImportError:
#     cannot import name 'change_password' from 'auth'
#
# ==============================================================================

if not hasattr(auth, "change_password"):

    def _runtime_change_password(
        user_id,
        old_password,
        new_password
    ):
        """
        Runtime compatibility implementation.

        Used only if auth.py does not expose change_password.
        """

        try:

            # --------------------------------------------------------------
            # Basic validation
            # --------------------------------------------------------------

            if not user_id:
                return False, "User ID is required"

            if not old_password:
                return False, "Current password is required"

            if not new_password:
                return False, "New password is required"

            if len(new_password) < 6:
                return (
                    False,
                    "New password must be at least 6 characters"
                )

            # --------------------------------------------------------------
            # Get database client
            # --------------------------------------------------------------

            supabase = getattr(
                auth,
                "supabase",
                None
            )

            if supabase is None:

                from erp_core.base_repo import db

                supabase = db()

            # --------------------------------------------------------------
            # Load user
            # --------------------------------------------------------------

            result = (
                supabase
                .table("users")
                .select("*")
                .eq("id", user_id)
                .limit(1)
                .execute()
            )

            if not result.data:
                return False, "User not found"

            user = result.data[0]

            # --------------------------------------------------------------
            # Verify old password
            # --------------------------------------------------------------

            verify_password = getattr(
                auth,
                "verify_password",
                None
            )

            if verify_password is None:
                return False, "Password verification unavailable"

            if not verify_password(
                user,
                old_password
            ):
                return False, "Current password is incorrect"

            # --------------------------------------------------------------
            # Hash new password
            # --------------------------------------------------------------

            hash_password = getattr(
                auth,
                "hash_password",
                None
            )

            if hash_password is None:
                return False, "Password hashing unavailable"

            new_hash = hash_password(
                new_password
            )

            # --------------------------------------------------------------
            # Update password
            # --------------------------------------------------------------

            update_result = (
                supabase
                .table("users")
                .update(
                    {
                        "password_hash": new_hash
                    }
                )
                .eq("id", user_id)
                .execute()
            )

            if not update_result.data:
                return False, "Password update failed"

            # --------------------------------------------------------------
            # Audit log
            # --------------------------------------------------------------

            log_auth_event = getattr(
                auth,
                "log_auth_event",
                None
            )

            if log_auth_event:

                try:

                    log_auth_event(
                        user_id,
                        "password_change",
                        "success"
                    )

                except Exception:
                    pass

            return (
                True,
                "Password changed successfully"
            )

        except Exception as e:

            return (
                False,
                f"Password change error: {e}"
            )

    # ----------------------------------------------------------------------
    # Attach compatibility function to auth module
    # ----------------------------------------------------------------------

    auth.change_password = _runtime_change_password


# ==============================================================================
# AUTH PUBLIC FUNCTIONS
# ==============================================================================

login_page = auth.login_page
is_authenticated = auth.is_authenticated


# ==============================================================================
# SIDEBAR
# ==============================================================================

from sidebar import show_sidebar


# ==============================================================================
# SESSION INITIALIZATION
# ==============================================================================

def init_state():

    defaults = {

        "user": None,

        "active_page": "1_POS",

        "language": "English",

    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


# ==============================================================================
# PAGE LOADER
# ==============================================================================
#
# Uses a unique module name for every page execution.
#
# This avoids stale:
#
#     erp_pages.dynamic_13_Profile
#
# modules remaining in sys.modules.
#
# ==============================================================================

def load_page(page_id):

    page_file = os.path.join(
        BASE_DIR,
        "erp_pages",
        f"{page_id}.py"
    )

    # --------------------------------------------------------------------------
    # PAGE EXISTS
    # --------------------------------------------------------------------------

    if not os.path.exists(page_file):

        st.error(
            f"Page file not found:\n{page_file}"
        )

        return

    try:

        # ----------------------------------------------------------------------
        # Force Python to refresh import metadata
        # ----------------------------------------------------------------------

        importlib.invalidate_caches()

        # ----------------------------------------------------------------------
        # Unique module name
        # ----------------------------------------------------------------------

        module_name = (
            f"erp_pages.dynamic_{page_id}_"
            f"{time.time_ns()}"
        )

        # ----------------------------------------------------------------------
        # Build module specification
        # ----------------------------------------------------------------------

        spec = importlib.util.spec_from_file_location(
            module_name,
            page_file
        )

        if spec is None:

            raise ImportError(
                f"Cannot create module specification for {page_id}"
            )

        # ----------------------------------------------------------------------
        # Create module
        # ----------------------------------------------------------------------

        module = importlib.util.module_from_spec(
            spec
        )

        # ----------------------------------------------------------------------
        # Register temporary module
        # ----------------------------------------------------------------------

        sys.modules[module_name] = module

        try:

            # --------------------------------------------------------------
            # Execute page
            # --------------------------------------------------------------

            spec.loader.exec_module(
                module
            )

        finally:

            # --------------------------------------------------------------
            # Remove temporary dynamic module
            # --------------------------------------------------------------

            sys.modules.pop(
                module_name,
                None
            )

        # ----------------------------------------------------------------------
        # ONE ENTRY POINT
        # ----------------------------------------------------------------------

        if hasattr(
            module,
            "run"
        ):

            module.run()

        elif hasattr(
            module,
            "main"
        ):

            module.main()

        else:

            st.warning(
                f"{page_id}.py has no run() or main()"
            )

    except Exception as e:

        st.error(
            f"Page Load Error : {e}"
        )

        with st.expander(
            "Debug Trace"
        ):

            st.exception(e)


# ==============================================================================
# PAGE ROUTER
# ==============================================================================

def page_router():

    if not st.session_state.get(
        "user"
    ):

        st.warning(
            "Please login first."
        )

        return

    page_id = st.session_state.get(
        "active_page",
        "1_POS"
    )

    load_page(
        page_id
    )


# ==============================================================================
# MAIN
# ==============================================================================

def main():

    # --------------------------------------------------------------------------
    # Session
    # --------------------------------------------------------------------------

    init_state()

    # --------------------------------------------------------------------------
    # Login
    # --------------------------------------------------------------------------

    if not is_authenticated():

        login_page()

        st.stop()

    # --------------------------------------------------------------------------
    # Sidebar
    # --------------------------------------------------------------------------

    try:

        show_sidebar()

    except Exception as e:

        st.sidebar.error(
            f"Sidebar Error : {e}"
        )

    # --------------------------------------------------------------------------
    # Page
    # --------------------------------------------------------------------------

    page_router()


# ==============================================================================
# START APPLICATION
# ==============================================================================

if __name__ == "__main__":

    main()
