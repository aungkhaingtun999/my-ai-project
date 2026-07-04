import streamlit as st
from auth import login_page
from sidebar import show_sidebar

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Myanmar ERP Enterprise",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# SESSION INIT
# ==========================================
def init_state():
    defaults = {
        "user": None,
        "role": "Cashier",
        "active_page": "dashboard",
        "warehouse_id": None,
        "cart": [],
        "theme": "light",
        "language": "English"
    }

    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

init_state()

# ==========================================
# AUTH CHECK
# ==========================================
def is_authenticated():
    user = st.session_state.get("user")
    return isinstance(user, dict) and user.get("id") is not None

# ==========================================
# ROLE SAFE
# ==========================================
def get_role():
    user = st.session_state.get("user")

    if not isinstance(user, dict):
        return "Cashier"

    role = user.get("role", "Cashier")

    allowed_roles = ["Admin", "Manager", "Cashier"]
    return role if role in allowed_roles else "Cashier"

# ==========================================
# LOGOUT
# ==========================================
def logout():
    st.session_state.clear()
    init_state()
    st.rerun()

# ==========================================
# PAGE ROUTER
# ==========================================
def page_router():

    page = st.session_state.get("active_page", "dashboard")
    user = st.session_state.get("user") or {}

    st.markdown("---")

    if page == "dashboard":
        st.title("🏭 ERP Control Dashboard")
        st.subheader(f"Welcome, {user.get('full_name') or user.get('name', 'User')} 🚀")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("System", "ACTIVE 🟢")
        c2.metric("Role", st.session_state.role)
        c3.metric("Mode", "Enterprise ERP")
        c4.metric("Backend", "Supabase ⚡")

        st.info(
            "✔ ERP Core Engine Loaded\n"
            "✔ Warehouse System Ready\n"
            "✔ POS + ERP Hybrid Mode\n"
            "✔ Secure Session Layer Active"
        )

    elif page == "sales":
        st.title("🛒 Sales Module")

    elif page == "purchase":
        st.title("📦 Purchase Module")

    elif page == "transfer":
        st.title("🔁 Warehouse Transfer")

    elif page == "reports":
        st.title("📊 Reports Engine")

    elif page == "settings":
        st.title("⚙️ ERP Settings Hub")

    elif page == "customers":
        st.title("👥 CRM Module")

    elif page == "suppliers":
        st.title("🏭 Supplier Module")

    else:
        st.warning("Page not found")

# ==========================================
# MAIN APP
# ==========================================
def main():

    # 🔐 LOGIN GATE (ABSOLUTE RULE)
    if not is_authenticated():
        login_page()
        st.stop()

    # sync role
    st.session_state.role = get_role()

    # sidebar ONLY after login
    show_sidebar()

    # render page
    page_router()

    # logout button
    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        logout()

# ==========================================
# RUN
# ==========================================
main()
