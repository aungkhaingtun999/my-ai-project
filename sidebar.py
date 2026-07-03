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
# SAFE INIT STATE
# ==========================================

def init_sidebar_state():
    defaults = {
        "role": "Cashier",
        "language": "English",
        "active_page": "pages/1_POS.py"
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ==========================================
# SAFE USER HANDLER
# ==========================================

def get_user():
    user = st.session_state.get("user")

    if isinstance(user, dict):
        return user.get("name", "Guest")
    elif isinstance(user, str):
        return user
    return "Guest"

# ==========================================
# ROLE VALIDATION (ANTI HACK)
# ==========================================

def safe_role():
    role = st.session_state.get("role", "Cashier")

    if role not in MENU:
        return "Cashier"

    return role

# ==========================================
# SIDEBAR UI
# ==========================================

def show_sidebar():

    init_sidebar_state()

    with st.sidebar:

        st.title("🛒 ERP SYSTEM")
        st.caption("Ultra v3 Controller")

        st.divider()

        # =========================
        # USER INFO PANEL
        # =========================
        username = get_user()
        role = safe_role()

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

            if is_active:
                label = f"👉 {icon} {title}"
            else:
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
        # LOGOUT (HARD RESET)
        # =========================
        if st.button("🚪 Logout", use_container_width=True):

            # keep only language
            lang = st.session_state.get("language", "English")

            st.session_state.clear()

            st.session_state["language"] = lang
            st.session_state["role"] = "Cashier"
            st.session_state["active_page"] = "pages/1_POS.py"

            st.switch_page("app.py")