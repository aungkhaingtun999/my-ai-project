import streamlit as st
from auth import login_page
from sidebar import show_sidebar

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="ERP POS System",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# SAFE SESSION INIT
# =========================
def init_session():
    defaults = {
        "user": None,
        "role": "Cashier",
        "active_page": "dashboard"
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# =========================
# AUTH CHECK
# =========================
def is_authenticated():
    user = st.session_state.get("user")

    if not user:
        return False

    # support dict user
    if isinstance(user, dict):
        return "id" in user

    # support string user (legacy login)
    if isinstance(user, str):
        return True

    return False

# =========================
# LOGOUT SAFE RESET
# =========================
def safe_logout():
    keep = {"role": "Cashier"}

    st.session_state.clear()

    for k, v in keep.items():
        st.session_state[k] = v

# =========================
# MAIN CONTROLLER
# =========================
def main():

    # -------------------------
    # LOGIN FLOW
    # -------------------------
    if not is_authenticated():
        login_page()
        return

    user = st.session_state.user

    # role sync
    if isinstance(user, dict):
        st.session_state.role = user.get("role", "Cashier")
        username = user.get("name", "User")
    else:
        username = str(user)

    # -------------------------
    # SIDEBAR
    # -------------------------
    show_sidebar()

    # =========================
    # DASHBOARD HOME
    # =========================
    st.title("🛒 ERP POS System Dashboard")
    st.subheader(f"Welcome back, {username} 🚀")

    # =========================
    # QUICK KPIs
    # =========================
    col1, col2, col3 = st.columns(3)

    col1.metric("Status", "Active 🟢")
    col2.metric("Role", st.session_state.role)
    col3.metric("System", "Online ⚡")

    st.divider()

    # =========================
    # SYSTEM INFO PANEL
    # =========================
    st.info("✔ ERP Controller Active | Checkout RPC v2 Ready | Supabase Connected")

    # =========================
    # LOGOUT BUTTON
    # =========================
    if st.sidebar.button("🚪 Logout"):
        safe_logout()
        st.rerun()

# =========================
# RUN
# =========================
main()