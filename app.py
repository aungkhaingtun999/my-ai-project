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
# SESSION DEFAULT SAFETY
# =========================
if "user" not in st.session_state:
    st.session_state.user = None

if "role" not in st.session_state:
    st.session_state.role = "Cashier"

if "active_page" not in st.session_state:
    st.session_state.active_page = None

# =========================
# AUTH GUARD (IMPORTANT)
# =========================
def is_authenticated():
    user = st.session_state.get("user")

    if not user:
        return False

    # extra safety check
    if isinstance(user, dict):
        return "id" in user

    return False

# =========================
# MAIN APP CONTROLLER
# =========================
def main():

    # -------------------------
    # NOT LOGGED IN
    # -------------------------
    if not is_authenticated():
        login_page()
        return

    # -------------------------
    # LOGGED IN
    # -------------------------
    user = st.session_state.user

    # role sync safety
    if isinstance(user, dict):
        st.session_state.role = user.get("role", "Cashier")

    # sidebar render
    show_sidebar()

    # =========================
    # DASHBOARD HOME
    # =========================
    st.title("🛒 ERP POS System Dashboard")
    st.subheader(f"Welcome back, {user.get('name', 'User')} 🚀")

    # =========================
    # QUICK STATS PLACEHOLDER
    # =========================
    col1, col2, col3 = st.columns(3)

    col1.metric("Status", "Active")
    col2.metric("User Role", st.session_state.role)
    col3.metric("System", "Online")

    st.divider()

    st.info("✔ System is running in production mode (ERP Controller Active)")

# =========================
# RUN APP
# =========================
main()