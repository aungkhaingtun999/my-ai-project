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
# AUTH CHECK (STRICT)
# ==========================================
def is_logged_in():
    user = st.session_state.get("user")

    return isinstance(user, dict) and user.get("id") is not None


# ==========================================
# SAFE USER
# ==========================================
def get_username():
    user = st.session_state.get("user")
    if isinstance(user, dict):
        return user.get("name", "Guest")
    return "Guest"


# ==========================================
# SAFE ROLE (NO SPOOF)
# ==========================================
def get_role():
    user = st.session_state.get("user")

    if isinstance(user, dict):
        role = user.get("role", "Cashier")
        return role if role in MENU else "Cashier"

    return "Cashier"


# ==========================================
# SIDEBAR
# ==========================================
def show_sidebar():

    # ❗ IMPORTANT: BLOCK BEFORE RENDER
    if not is_logged_in():
        return

    with st.sidebar:

        st.title("🛒 ERP SYSTEM")
        st.caption("Ultra v3 Controller")

        st.divider()

        username = get_username()
        role = get_role()

        st.markdown(f"👤 **{username}**")
        st.markdown(f"🔐 Role: `{role}`")

        st.divider()

        # =========================
        # LANGUAGE
        # =========================
        lang = st.selectbox(
            "Language",
            ["English", "မြန်မာ"],
            index=0 if st.session_state.get("language", "English") == "English" else 1
        )
        st.session_state.language = lang

        st.divider()

        # =========================
        # NAVIGATION
        # =========================
        st.subheader("📂 Navigation")

        for icon, title, page in MENU.get(role, MENU["Cashier"]):

            label = f"{icon} {title}"

            if st.button(label, key=f"nav_{role}_{page}"):
                st.session_state.active_page = page
                st.switch_page(page)

        st.divider()

        # =========================
        # SYSTEM STATUS
        # =========================
        st.success("🟢 System Online")

        # =========================
        # LOGOUT (CLEAN RESET)
        # =========================
        if st.button("🚪 Logout", use_container_width=True):

            st.session_state.clear()

            # safe re-init only essentials
            st.session_state.update({
                "user": None,
                "role": None,
                "language": "English",
                "active_page": "pages/1_POS.py"
            })

            st.switch_page("app.py")
