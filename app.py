import streamlit as st
from auth import login_page
from sidebar import show_sidebar

# ==========================================
# PAGE CONFIG (MUST BE FIRST)
# ==========================================
st.set_page_config(
    page_title="Myanmar ERP Enterprise",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# SESSION INIT (CRASH SAFE ERP STYLE)
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
# AUTH CHECK (STRICT + SAFE)
# ==========================================
def is_authenticated():
    user = st.session_state.get("user")
    return isinstance(user, dict) and user.get("id") is not None

# ==========================================
# ROLE GETTER (SAFE + NO SPOOF)
# ==========================================
def get_role():
    user = st.session_state.get("user")

    if not isinstance(user, dict):
        return "Cashier"

    role = user.get("role", "Cashier")

    # prevent fake roles
    allowed_roles = ["Admin", "Manager", "Cashier"]
    if role not in allowed_roles:
        return "Cashier"

    return role

# ==========================================
# LOGOUT (FULL RESET SAFE)
# ==========================================
def logout():
    st.session_state.clear()
    init_state()
    st.rerun()

# ==========================================
# PAGE ROUTER (ERP ENGINE)
# ==========================================
def page_router():

    page = st.session_state.get("active_page", "dashboard")
    user = st.session_state.get("user") or {}

    st.markdown("---")

    # ================= DASHBOARD =================
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

    # ================= MODULES =================
    elif page == "sales":
        st.title("🛒 Sales Module")
        st.info("POS → ERP Sales Engine Active")

    elif page == "purchase":
        st.title("📦 Purchase Module")
        st.info("Procurement System Active")

    elif page == "transfer":
        st.title("🔁 Warehouse Transfer")
        st.info("Inventory Movement Engine")

    elif page == "reports":
        st.title("📊 Reports Engine")
        st.info("BI + Analytics Module")

    elif page == "settings":
        st.title("⚙️ ERP Settings Hub")
        st.info("System Configuration Center")

    elif page == "customers":
        st.title("👥 CRM Module")
        st.info("Customer Management")

    elif page == "suppliers":
        st.title("🏭 Supplier Module")
        st.info("Supplier Management")

    else:
        st.warning("Page not found")

# ==========================================
# MAIN APP CONTROLLER
# ==========================================
def main():

    # 🔐 LOGIN GATE (ABSOLUTE RULE)
    if not is_authenticated():
        login_page()
        return

    # sync role safely
    st.session_state.role = get_role()

    # =========================
    # SIDEBAR (ONLY AFTER LOGIN)
    # =========================
    show_sidebar()

    # =========================
    # MAIN PAGE RENDER
    # =========================
    page_router()

    # =========================
    # GLOBAL LOGOUT
    # =========================
    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        logout()

# ==========================================
# RUN APP
# ==========================================
main()
