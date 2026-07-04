# ==========================================
# app.py (ERP ENTERPRISE CONTROLLER v4)
# ==========================================

import streamlit as st
from auth import login_page, is_authenticated
from sidebar import show_sidebar
from guards import require_login, get_current_user

# ==========================================
# PAGE CONFIG (MUST BE FIRST)
# ==========================================

st.set_page_config(
    page_title="Myanmar ERP Enterprise",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"  # 🔥 IMPORTANT: no leak before login
)

# ==========================================
# SESSION INIT (GLOBAL SAFE STATE)
# ==========================================

def init_state():
    defaults = {
        "user": None,
        "role": None,
        "active_page": "dashboard",
        "cart": [],
        "language": "English",
        "theme": "light"
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


# ==========================================
# ROLE SYNC (TRUST SERVER ONLY)
# ==========================================

def sync_role():
    user = st.session_state.get("user")

    if isinstance(user, dict):
        st.session_state.role = user.get("role", "Cashier")
    else:
        st.session_state.role = "Cashier"


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

    # ================= MODULES =================
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
# MAIN APP CONTROLLER
# ==========================================

def main():

    # 🔐 HARD LOGIN GATE (NO LEAK)
    if not is_authenticated():
        login_page()

        # 🔥 IMPORTANT: STOP EVERYTHING HERE
        st.stop()

    # =========================
    # AUTHORIZED FLOW ONLY
    # =========================

    sync_role()

    # sidebar ONLY after login
    show_sidebar()

    # main page
    page_router()

    # logout
    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()

        st.session_state.update({
            "user": None,
            "role": None,
            "active_page": "dashboard",
            "cart": [],
            "language": "English"
        })

        st.rerun()


# ==========================================
# RUN APP
# ==========================================

main()
