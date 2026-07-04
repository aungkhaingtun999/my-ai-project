import streamlit as st

# ==========================================
# MENU CONFIG (ROLE BASED ERP)
# ==========================================
MENU = {
    "Admin": [
        ("🏠", "Dashboard", "pages/3_Admin_Dashboard.py"),
        ("🛒", "POS", "pages/1_POS.py"),
        ("📦", "Inventory", "pages/2_Inventory.py"),
        ("🧾", "Reports", "pages/3_Reports.py"),
        ("👥", "Users", "pages/4_Users.py"),
        ("↩️", "Refund", "pages/5_Refund.py"),
        ("⚙️", "Settings", "pages/12_Settings.py"),
    ],
    "Manager": [
        ("🛒", "POS", "pages/1_POS.py"),
        ("📦", "Inventory", "pages/2_Inventory.py"),
        ("🧾", "Reports", "pages/3_Reports.py"),
    ],
    "Cashier": [
        ("🛒", "POS", "pages/1_POS.py"),
    ]
}

# ==========================================
# SAFE AUTH CHECK
# ==========================================
def is_logged_in():
    user = st.session_state.get("user")
    return isinstance(user, dict) and user.get("id") is not None


# ==========================================
# SAFE ROLE (SERVER-TRUSTED ONLY)
# ==========================================
def get_role():
    user = st.session_state.get("user")

    if not isinstance(user, dict):
        return "Cashier"

    role = user.get("role", "Cashier")

    # prevent fake role injection
    if role not in MENU:
        return "Cashier"

    return role


# ==========================================
# SAFE USER NAME
# ==========================================
def get_username():
    user = st.session_state.get("user")

    if isinstance(user, dict):
        return user.get("name") or user.get("email") or "User"

    return "Guest"


# ==========================================
# SIDEBAR (SECURE CORE)
# ==========================================
def show_sidebar():

    user = st.session_state.get("user")

    if not isinstance(user, dict):
        return   # safe exit only

    with st.sidebar:
        st.title("ERP SYSTEM")

        
        st.caption("Enterprise Control Center")

        st.divider()

        username = get_username()
        role = get_role()

        st.markdown(f"👤 **{username}**")
        st.markdown(f"🔐 Role: `{role}`")

        st.divider()

        # =========================
        # LANGUAGE SAFE STORE
        # =========================
        if "language" not in st.session_state:
            st.session_state.language = "English"

        lang = st.radio(
            "Language",
            ["English", "မြန်မာ"],
            index=0 if st.session_state.language == "English" else 1
        )
        st.session_state.language = lang

        st.divider()

        # =========================
        # NAVIGATION (SAFE SWITCH)
        # =========================
        st.subheader("📂 Navigation")

        for icon, title, page in MENU.get(role, MENU["Cashier"]):

            if st.button(f"{icon} {title}", key=f"nav_{role}_{page}"):

                # IMPORTANT: only set state, not direct switch conflict
                st.session_state.active_page = page
                st.rerun()

        st.divider()

        # =========================
        # SYSTEM STATUS
        # =========================
        st.success("🟢 System Online")

        # =========================
        # LOGOUT (FULL RESET SAFE)
        # =========================
        if st.button("🚪 Logout", use_container_width=True):

            # FULL CLEAN RESET (NO DATA LEAK)
            for key in list(st.session_state.keys()):
                del st.session_state[key]

            st.session_state.update({
                "user": None,
                "role": None,
                "language": "English",
                "active_page": "pages/1_POS.py"
            })

            st.rerun()
