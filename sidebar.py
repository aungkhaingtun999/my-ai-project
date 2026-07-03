import streamlit as st

# ==========================================
# MENU CONFIG (ERP LEVEL)
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
# INIT STATE
# ==========================================

def init_sidebar_state():

    if "role" not in st.session_state:
        st.session_state.role = "Cashier"

    if "language" not in st.session_state:
        st.session_state.language = "English"

    if "active_page" not in st.session_state:
        st.session_state.active_page = None


# ==========================================
# SIDEBAR UI
# ==========================================

def show_sidebar():

    init_sidebar_state()

    with st.sidebar:

        st.title("🛒 ERP SYSTEM")

        st.divider()

        # =========================
        # USER INFO
        # =========================
        user = st.session_state.get("user", {})
        username = user.get("name", "Guest")
        role = st.session_state.get("role", "Cashier")

        st.write(f"👤 **{username}**")
        st.write(f"🔑 Role: {role}")

        st.divider()

        # =========================
        # LANGUAGE SWITCH
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

        menu = MENU.get(role, [])

        for icon, title, page in menu:

            is_active = (st.session_state.active_page == page)

            label = f"{icon} {title}"

            if is_active:
                label = f"👉 {label}"

            if st.button(label, use_container_width=True, key=page):

                st.session_state.active_page = page
                st.switch_page(page)

        st.divider()

        # =========================
        # LOGOUT SAFE
        # =========================
        if st.button("🚪 Logout", use_container_width=True):

            keep_keys = ["language"]

            for k in list(st.session_state.keys()):
                if k not in keep_keys:
                    del st.session_state[k]

            st.session_state.role = "Cashier"
            st.session_state.active_page = None

            st.switch_page("app.py")