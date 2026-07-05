# ==========================================
# app.py (ERP ENTERPRISE CONTROLLER v5)
# ==========================================

import streamlit as st
from auth import login_page, is_authenticated
from sidebar import show_sidebar
from guards impoimport streamlit as st
from auth import login_page, is_authenticated
from sidebar import show_sidebar
from guards import get_current_user

st.set_page_config(
    page_title="Myanmar ERP Enterprise",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def init_state():
    defaults = {
        "user": None,
        "role": "Cashier",
        "active_page": "dashboard",
        "cart": [],
        "language": "English",
        "theme": "light",
        "auth_checked": False
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

init_state()

def sync_role():
    user = st.session_state.get("user")
    st.session_state.role = user.get("role", "Cashier") if isinstance(user, dict) else "Cashier"

def ensure_user_object():
    user = st.session_state.get("user")
    if not isinstance(user, dict) or not user.get("id"):
        st.session_state.user = None
        return False
    return True

def page_router():
    page = st.session_state.get("active_page", "dashboard")
    user = st.session_state.get("user") or {}
    st.markdown("---")
    
    if page == "dashboard":
        st.title("🏭 ERP Control Dashboard")
        st.subheader(f"Welcome, {user.get('full_name') or user.get('username') or 'User'} 🚀")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("System", "ACTIVE 🟢")
        c2.metric("Role", st.session_state.role)
        c3.metric("Mode", "Enterprise ERP")
        c4.metric("Backend", "Supabase ⚡")
    # ... (ကျန်တဲ့ modules များ)
    else:
        st.warning("Page not found")

def main():
    if not is_authenticated():
        login_page()
        st.stop()

    if not ensure_user_object():
        st.error("Invalid session. Please login again.")
        st.stop()

    sync_role()
    try:
        show_sidebar()
    except Exception as e:
        st.error("Sidebar error")
    
    page_router()
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        init_state()
        st.rerun()

main()rrent_user

# ==========================================
# PAGE CONFIG (MUST BE FIRST)
# ==========================================

st.set_page_config(
    page_title="Myanmar ERP Enterprise",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# SESSION INIT (SAFE STATE ENGINE)
# ==========================================

def init_state():
    defaults = {
        "user": None,
        "role": "Cashier",
        "active_page": "dashboard",
        "cart": [],
        "language": "English",
        "theme": "light",
        "auth_checked": False   # 🔥 NEW: prevent rerun loop bug
    }

    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


init_state()

# ==========================================
# ROLE SYNC (SECURE SERVER TRUTH)
# ==========================================

def sync_role():
    user = st.session_state.get("user")

    if isinstance(user, dict):
        st.session_state.role = user.get("role", "Cashier")
    else:
        st.session_state.role = "Cashier"


# ==========================================
# GLOBAL SAFETY CHECK
# ==========================================

def ensure_user_object():
    """
    🔥 FIX: prevent sidebar / page crash if user structure breaks
    """
    user = st.session_state.get("user")

    if not isinstance(user, dict):
        st.session_state.user = None
        return False

    if not user.get("id"):
        st.session_state.user = None
        return False

    return True


# ==========================================
# PAGE ROUTER (CLEAN ERP ENGINE)
# ==========================================

def page_router():

    page = st.session_state.get("active_page", "dashboard")
    user = st.session_state.get("user") or {}

    st.markdown("---")

    # ================= DASHBOARD =================
    if page == "dashboard":
        st.title("🏭 ERP Control Dashboard")

        st.subheader(
            f"Welcome, {user.get('full_name') or user.get('username') or 'User'} 🚀"
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("System", "ACTIVE 🟢")
        c2.metric("Role", st.session_state.role)
        c3.metric("Mode", "Enterprise ERP")
        c4.metric("Backend", "Supabase ⚡")

        st.info(
            "✔ ERP Core Engine Active\n"
            "✔ Auth Layer Secured\n"
            "✔ Sidebar Controlled\n"
            "✔ DB Layer Connected"
        )

    elif page == "sales":
        st.title("🛒 Sales Module")

    elif page == "purchase":
        st.title("📦 Purchase Module")

    elif page == "inventory":
        st.title("📦 Inventory Module")

    elif page == "transfer":
        st.title("🔁 Warehouse Transfer")

    elif page == "reports":
        st.title("📊 Reports Engine")

    elif page == "settings":
        st.title("⚙️ Settings Hub")

    elif page == "customers":
        st.title("👥 CRM Module")

    elif page == "suppliers":
        st.title("🏭 Supplier Module")

    else:
        st.warning("Page not found")


# ==========================================
# MAIN CONTROLLER
# ==========================================

def main():

    # 🔐 HARD LOGIN GATE (NO LEAK, NO SIDEBAR)
    if not is_authenticated():
        login_page()
        st.stop()

    # 🔥 VALIDATE USER OBJECT
    if not ensure_user_object():
        st.error("Invalid session. Please login again.")
        st.stop()

    # =========================
    # AUTH FLOW
    # =========================

    sync_role()

    # =========================
    # SAFE SIDEBAR LOAD
    # =========================
    try:
        show_sidebar()
    except Exception as e:
        st.error("Sidebar error")
        st.caption(str(e))

    # =========================
    # MAIN PAGE
    # =========================
    page_router()

    # =========================
    # GLOBAL LOGOUT
    # =========================
    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()

        # safe reset
        init_state()

        st.rerun()


# ==========================================
# RUN APP
# ==========================================

main()
