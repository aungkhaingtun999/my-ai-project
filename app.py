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
# SESSION STATE INIT (STRICT ERP STYLE)
# ==========================================
def init_state():
    defaults = {
        "user": None,
        "role": None,
        "active_page": "dashboard",
        "warehouse_id": None,
        "cart": [],
        "theme": "light"
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ==========================================
# AUTH CHECK (SAFE + SCALABLE)
# ==========================================
def is_authenticated() -> bool:
    user = st.session_state.get("user")

    if not user:
        return False

    if isinstance(user, dict):
        return bool(user.get("id"))

    if isinstance(user, str):
        return len(user.strip()) > 0

    return False

# ==========================================
# ROLE HELPER (ERP READY)
# ==========================================
def get_role():
    user = st.session_state.get("user")

    if isinstance(user, dict):
        return user.get("role", "Cashier")

    return "Cashier"

# ==========================================
# LOGOUT (FULL RESET SAFE)
# ==========================================
def logout():
    keys_to_keep = {}

    st.session_state.clear()

    # restore clean session
    for k, v in {
        "user": None,
        "role": None,
        "active_page": "dashboard",
        "warehouse_id": None,
        "cart": [],
        "theme": "light"
    }.items():
        st.session_state[k] = v

    st.rerun()

# ==========================================
# PAGE ROUTER (ERP CORE ENGINE)
# ==========================================
def page_router():
    page = st.session_state.get("active_page", "dashboard")

    st.markdown("---")

    if page == "dashboard":
        st.title("🏭 ERP Control Dashboard")
        st.subheader(f"Welcome, {st.session_state.user.get('name','User') if isinstance(st.session_state.user, dict) else 'User'} 🚀")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("System", "ACTIVE 🟢")
        col2.metric("Role", st.session_state.role)
        col3.metric("Mode", "Enterprise ERP")
        col4.metric("Backend", "Supabase ⚡")

        st.info("✔ ERP Core Engine Loaded\n✔ Warehouse System Ready\n✔ RPC Checkout Enabled\n✔ Multi-module Architecture Active")

    elif page == "sales":
        st.title("🛒 Sales Module Loaded")
        st.info("Sales engine connected (POS → ERP mode)")

    elif page == "purchase":
        st.title("📦 Purchase Module Loaded")
        st.info("Procurement system active")

    elif page == "transfer":
        st.title("🔁 Warehouse Transfer Module")
        st.info("Inventory movement system ready")

    elif page == "reports":
        st.title("📊 Reports Engine")
        st.info("BI + AI analytics module")

    elif page == "settings":
        st.title("⚙️ ERP Settings Hub")
        st.info("System configuration center")

    elif page == "customers":
        st.title("👥 CRM Module")
        st.info("Customer management system")

    elif page == "suppliers":
        st.title("🏭 Supplier Module")
        st.info("Supplier management system")

    else:
        st.warning("Page not found")

# ==========================================
# MAIN APP
# ==========================================
def main():

    # --------------------------
    # LOGIN GATE
    # --------------------------
    if not is_authenticated():
        login_page()
        return

    # role sync
    st.session_state.role = get_role()

    # --------------------------
    # SIDEBAR (ERP NAVIGATION)
    # --------------------------
    show_sidebar()

    # --------------------------
    # ACTIVE PAGE RENDER
    # --------------------------
    page_router()

    # --------------------------
    # GLOBAL LOGOUT
    # --------------------------
    st.divider()

    col1, col2, col3 = st.columns([6, 2, 2])

    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            logout()

# ==========================================
# RUN APP
# ==========================================
main()
