import streamlit as st
from auth import login_page
from sidebar import show_sidebar

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="ERP POS System",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# STATE INIT (STRICT)
# ==========================================
def init_state():
    defaults = {
        "user": None,
        "role": None,
        "active_page": None
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ==========================================
# AUTH VALIDATION (CLEAN)
# ==========================================
def is_authenticated() -> bool:
    user = st.session_state.get("user")

    if user is None:
        return False

    if isinstance(user, dict):
        return bool(user.get("id"))

    # if string login legacy
    if isinstance(user, str):
        return len(user.strip()) > 0

    return False

# ==========================================
# LOGOUT (SAFE RESET)
# ==========================================
def logout():
    preserve = {
        "user": None,
        "role": None,
        "active_page": None
    }

    for k in list(st.session_state.keys()):
        del st.session_state[k]

    for k, v in preserve.items():
        st.session_state[k] = v

    st.rerun()

# ==========================================
# MAIN APP CONTROLLER
# ==========================================
def main():

    # --------------------------
    # LOGIN GATE (HARD BLOCK)
    # --------------------------
    if not is_authenticated():
        login_page()
        return

    user = st.session_state.user

    # normalize user
    if isinstance(user, dict):
        username = user.get("name", "User")
        st.session_state.role = user.get("role", "Cashier")
    else:
        username = str(user)
        st.session_state.role = "Cashier"

    # --------------------------
    # SIDEBAR (ONLY IF LOGGED IN)
    # --------------------------
    show_sidebar()

    # =========================
    # DASHBOARD HOME
    # =========================
    st.title("🛒 ERP POS System Dashboard")
    st.subheader(f"Welcome back, {username} 🚀")

    # =========================
    # KPI SECTION
    # =========================
    col1, col2, col3 = st.columns(3)

    col1.metric("System Status", "Active 🟢")
    col2.metric("User Role", st.session_state.role)
    col3.metric("Backend", "Supabase ⚡")

    st.divider()

    # =========================
    # INFO PANEL
    # =========================
    st.info(
        "✔ ERP Controller Active\n"
        "✔ Checkout RPC v2 Ready\n"
        "✔ Secure Session Mode ON"
    )

    # =========================
    # LOGOUT (GLOBAL SAFE BUTTON)
    # =========================
    if st.button("🚪 Logout", use_container_width=True):
        logout()

# ==========================================
# RUN
# ==========================================
main()