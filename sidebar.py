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
        ("🧾", "Receipt Viewer", "pages/6_Receipt_Viewer.py"),
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
# AUTH CHECK
# ==========================================
def is_logged_in():
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

    if role not in MENU:
        return "Cashier"

    return role


# ==========================================
# USER NAME SAFE
# ==========================================
def get_username():
    user = st.session_state.get("user")

    if isinstance(user, dict):
        return user.get("name") or user.get("email") or "User"

    return "Guest"


# ==========================================
# SIDEBAR (HARD SECURITY GATE FIXED)
# ==========================================
def show_sidebar():

    # 🔥 CRITICAL FIX (THIS WAS MISSING)
    if not is_logged_in():
        return   # ⛔ STOP EVERYTHING HERE

    user = st.session_state.get("user")

    with st.sidebar:

        st.title("🏭 ERP SYSTEM")
        st.caption("Enterprise Control Center")

        st.divider()

        username = get_username()
        role = get_role()

        st.markdown(f"👤 **{username}**")
        st.markdown(f"🔐 Role: `{role}`")

        st.divider()

        # =========================
        # LANGUAGE
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
        # NAVIGATION
        # =========================
        st.subheader("📂 Navigation")

        for icon, title, page in MENU.get(role, MENU["Cashier"]):

            if st.button(f"{icon} {title}", key=f"{role}_{page}"):

                st.session_state.active_page = page
                st.rerun()

        st.divider()

        st.success("🟢 System Online")

        # =========================
        # LOGOUT (FULL RESET SAFE)
        # =========================
        if st.button("🚪 Logout", use_container_width=True):

            st.session_state.clear()

            st.session_state.update({
                "user": None,
                "role": None,
                "language": "English",
                "active_page": "pages/1_POS.py"
            })

            st.rerun()
