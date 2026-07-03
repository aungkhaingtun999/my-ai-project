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
# INIT STATE SAFE (NO AUTO ROLE HACK)
# ==========================================
def init_sidebar_state():

    if "role" not in st.session_state:
        st.session_state.role = None

    if "language" not in st.session_state:
        st.session_state.language = "English"

    if "active_page" not in st.session_state:
        st.session_state.active_page = "pages/1_POS.py"


# ==========================================
# AUTH GUARD (IMPORTANT FIX)
# ==========================================
def is_logged_in():
    user = st.session_state.get("user")

    if not user:
        return False

    if isinstance(user, dict) and user.get("id"):
        return True

    if isinstance(user, str):
        return True

    return False


# ==========================================
# USER NAME SAFE
# ==========================================
def get_username():
    user = st.session_state.get("user")

    if isinstance(user, dict):
        return user.get("name", "Guest")

    if isinstance(user, str):
        return user

    return "Guest"


# ==========================================
# ROLE SAFE
# ==========================================
def get_role():
    role = st.session_state.get("role")

    if role in MENU:
        return role

    return "Cashier"


# ==========================================
# SIDEBAR UI
# ==========================================
def show_sidebar():

    # ❌ IMPORTANT: BLOCK IF NOT LOGGED IN
    if not is_logged_in():
        return

    init_sidebar_state()

    with st.sidebar:

        st.title("🛒 ERP SYSTEM")
        st.caption("Ultra v3 Controller")

        st.divider()

        # =========================
        # USER INFO
        # =========================
        username = get_username()
        role = get_role()

        st.markdown(f"👤 **{username}**")
        st.markdown(f"🔐 Role: `{role}`")

        st.divider()

        # =========================
        # LANGUAGE
        # =========================
        st.session_state.language = st.selectbox(
            "Language",
            ["English", "မြန်မာ"],
            index=0 if st.session_state.language == "English" else 1
        )

        st.divider()

        # =========================
        # NAVIGATION
        # =========================
        st.subheader("📂 Navigation")

        menu = MENU.get(role, MENU["Cashier"])

        for icon, title, page in menu:

            is_active = (st.session_state.active_page == page)

            label = f"👉 {icon} {title}" if is_active else f"{icon} {title}"

            if st.button(label, key=f"nav_{role}_{page}"):

                st.session_state.active_page = page

                try:
                    st.switch_page(page)
                except Exception:
                    st.warning("Navigation failed - check Streamlit multipage setup")

        st.divider()

        # =========================
        # SYSTEM STATUS
        # =========================
        st.success("🟢 System Online")

        # =========================
        # LOGOUT SAFE RESET
        # =========================
        if st.button("🚪 Logout", use_container_width=True):

            st.session_state.clear()

            st.session_state.update({
                "user": None,
                "role": None,
                "language": "English",
                "active_page": "pages/1_POS.py"
            })

            st.switch_page("app.py")
