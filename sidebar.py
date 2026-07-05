import streamlit as st
from auth import logout
from guards import (
    is_logged_in,
    current_user,
    get_role_name,
    ROLE_ADMIN,
    ROLE_MANAGER,
    ROLE_CASHIER
)

# ==========================================================
# ERP MENU CONFIGURATION
# ==========================================================
MENU = {
    ROLE_ADMIN: [
        ("🏠", "Dashboard", "pages/3_Admin_Dashboard.py"),
        ("🛒", "POS", "pages/1_POS.py"),
        ("📦", "Inventory", "pages/2_Inventory.py"),
        ("🛍", "Purchase", "pages/7_Purchase.py"),
        ("🔁", "Transfer", "pages/8_Transfer.py"),
        ("👥", "Customers", "pages/9_Customers.py"),
        ("🏭", "Suppliers", "pages/10_Suppliers.py"),
        ("📊", "Reports", "pages/3_Reports.py"),
        ("🧾", "Receipt Viewer", "pages/6_Receipt_Viewer.py"),
        ("👤", "Users", "pages/4_Users.py"),
        ("↩️", "Refund", "pages/5_Refund.py"),
        ("⚙️", "Settings", "pages/12_Settings.py"),
    ],
    ROLE_MANAGER: [
        ("🏠", "Dashboard", "pages/3_Admin_Dashboard.py"),
        ("🛒", "POS", "pages/1_POS.py"),
        ("📦", "Inventory", "pages/2_Inventory.py"),
        ("🛍", "Purchase", "pages/7_Purchase.py"),
        ("🔁", "Transfer", "pages/8_Transfer.py"),
        ("👥", "Customers", "pages/9_Customers.py"),
        ("🏭", "Suppliers", "pages/10_Suppliers.py"),
        ("📊", "Reports", "pages/3_Reports.py"),
        ("🧾", "Receipt Viewer", "pages/6_Receipt_Viewer.py"),
    ],
    ROLE_CASHIER: [
        ("🛒", "POS", "pages/1_POS.py"),
        ("🧾", "Receipt Viewer", "pages/6_Receipt_Viewer.py"),
    ]
}

# ==========================================================
# ACTIVE PAGE
# ==========================================================
def get_active_page():
    return st.session_state.get("active_page", "pages/1_POS.py")

# ==========================================================
# SIDEBAR
# ==========================================================
def show_sidebar():
    # --------------------------------------------------
    # HARD SECURITY: Login မဝင်ထားရင် Sidebar လုံးဝမပြပါ
    # --------------------------------------------------
    if not is_logged_in():
        return

    user = current_user()
    role_id = user.get("role_id")

    with st.sidebar:
        st.title("🏭 Myanmar ERP")
        st.caption("Enterprise Edition")
        st.divider()

        # USER CARD
        st.success(f"👤 {user.get('full_name', 'User')}")
        st.caption(f"Username : {user.get('username', '')}")
        st.caption(f"Role : {get_role_name()}")
        st.divider()

        # LANGUAGE
        if "language" not in st.session_state:
            st.session_state.language = "English"

        st.session_state.language = st.selectbox(
            "Language",
            ["English", "မြန်မာ"],
            index=0 if st.session_state.language == "English" else 1
        )
        st.divider()

        # NAVIGATION
        st.subheader("📂 Navigation")
        active = get_active_page()

        for icon, title, page in MENU.get(role_id, []):
            label = f"{icon} {title}"
            if active == page:
                label = f"✅ {icon} {title}"

            if st.button(label, key=page, use_container_width=True):
                st.session_state.active_page = page
                st.switch_page(page)

        st.divider()

        # SYSTEM STATUS
        st.success("🟢 System Online")
        st.caption("Database : Connected")
        st.caption("Session : Active")
        st.caption("ERP Version : Enterprise")
        st.divider()

        # LOGOUT
        if st.button("🚪 Logout", use_container_width=True):
            logout()  # Session ရှင်းထုတ်ခြင်း
            st.rerun() # Logout ဖြစ်ကြောင်း ချက်ချင်း update လုပ်ပေးခြင်း
