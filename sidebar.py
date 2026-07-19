import streamlit as st
from auth import logout
from guards import (
    is_logged_in,
    current_user,
    ROLE_ADMIN,
    ROLE_MANAGER,
    ROLE_CASHIER
)

# ==========================================================
# ERP MENU CONFIGURATION
# ==========================================================
MENU = {
    ROLE_ADMIN: [
        ("🏠", "Dashboard", "3_Admin_Dashboard"),
        ("🛒", "POS", "1_POS"),
        ("📦", "Inventory", "2_Inventory"),
        ("🛍", "Purchase", "7_Purchase"),
        ("🔁", "Transfer", "8_Transfer"),
        ("👥", "Customers", "9_Customers"),
        ("🏭", "Suppliers", "10_Suppliers"),
        ("↩️", "Refund", "5_Refund"),
        ("✅", "Refund Approval", "6_Refund_Approval"),
        ("📊", "Refund Report", "6_Refund_Report"),
        ("🧾", "Receipt Viewer", "6_Receipt_Viewer"),
        ("⚙️", "Settings", "12_Settings"),
    ],
    ROLE_MANAGER: [
        ("🏠", "Dashboard", "3_Admin_Dashboard"),
        ("🛒", "POS", "1_POS"),
        ("📦", "Inventory", "2_Inventory"),
        ("🔁", "Transfer", "8_Transfer"),
        ("↩️", "Refund", "5_Refund"),
        ("✅", "Refund Approval", "6_Refund_Approval"),
        ("📊", "Refund Report", "6_Refund_Report"),
        ("📊", "Reports", "3_Reports"),
    ],
    ROLE_CASHIER: [
        ("🛒", "POS", "1_POS"),
        ("🧾", "Receipt Viewer", "6_Receipt_Viewer"),
        ("↩️", "Refund", "5_Refund"),
    ]
}

# ==========================================================
# ACTIVE PAGE
# ==========================================================
def get_active_page():
    if "active_page" not in st.session_state:
        user = current_user()
        if user.get("role_id") == ROLE_ADMIN:
            st.session_state.active_page = "3_Admin_Dashboard"
        else:
            st.session_state.active_page = "1_POS"
    return st.session_state.active_page

# ==========================================================
# SIDEBAR
# ==========================================================
def show_sidebar():
    if not is_logged_in():
        return

    user = current_user()
    role_id = user.get("role_id")
    # Role display ပြဿနာကို နောက်ဆင့်မှာ auth.py မှာ fix မယ်
    role_display = user.get("role") or user.get("role_name") or "Staff"

    with st.sidebar:
        st.title("🏭 Myanmar ERP")
        st.caption("Enterprise Edition")
        st.divider()

        # USER CARD
        st.success(f"👤 {user.get('full_name', user.get('username', 'User'))}")
        st.caption(f"Username : {user.get('username', '')}")
        st.caption(f"Role : {role_display}")
        st.divider()

        # NAVIGATION
        st.subheader("📂 Navigation")
        active = get_active_page()
        pages = MENU.get(role_id, [])

        for icon, title, page_id in pages:
            label = f"{icon} {title}"
            if active == page_id:
                label = f"✅ {label}"

            if st.button(label, key=f"nav_{page_id}", use_container_width=True):
                st.session_state.active_page = page_id
                st.rerun()

        st.divider()
        if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
            logout()
            st.rerun()
        
