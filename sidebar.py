import streamlit as st
from auth import logout
from guards import (
    is_logged_in,
    current_user,
    ROLE_ADMIN,
    ROLE_MANAGER,
    ROLE_CASHIER
)

# 1) Menu Structure များကို အပြည့်အစုံပြင်ဆင်ခြင်း
MENU = {
    ROLE_ADMIN: [
        ("🏠", "Dashboard", "3_Admin_Dashboard"),
        ("🛒", "POS", "1_POS"),
        ("📦", "Inventory", "2_Inventory"),
        ("🛍", "Purchase", "7_Purchase"),
        ("🔁", "Transfer", "8_Transfer"),
        ("↩️", "Refund", "5_Refund"),
        ("✅", "Refund Approval", "6_Refund_Approval"),
        ("📊", "Refund Report", "6_Refund_Report"),
        ("⚙️", "Settings", "12_Settings"),
    ],
    ROLE_MANAGER: [
        ("🏠", "Dashboard", "3_Admin_Dashboard"),
        ("🛒", "POS", "1_POS"),
        ("📦", "Inventory", "2_Inventory"),
        ("✅", "Refund Approval", "6_Refund_Approval"),
        ("📊", "Refund Report", "6_Refund_Report"),
        ("📈", "Reports", "2_Reports"),
    ],
    ROLE_CASHIER: [
        ("🛒", "POS", "1_POS"),
    ]
}

# 2) Role-based Default Page Logic
def get_active_page():
    if "active_page" not in st.session_state:
        user = current_user()
        # Admin ဆိုလျှင် Dashboard၊ ကျန်သူများအတွက် POS
        if user.get("role_id") == ROLE_ADMIN:
            st.session_state.active_page = "3_Admin_Dashboard"
        else:
            st.session_state.active_page = "1_POS"
            
    return st.session_state.active_page

def show_sidebar():
    if not is_logged_in():
        return

    user = current_user()
    role_display = user.get('role', 'Staff') 
    
    with st.sidebar:
        st.title("🏭 Myanmar ERP")
        st.caption("Enterprise Edition")
        st.info(f"👤 {user.get('username', 'User')}\n🔑 Role: {role_display}")
        st.divider()

        st.subheader("📂 Navigation")
        active = get_active_page()

        role_id = user.get("role_id")
        pages = MENU.get(role_id, [])
        
        # 3) Menu Key Duplicate မဖြစ်စေရန် စစ်ဆေးခြင်း
        # page_id သည် သီးသန့်ဖြစ်နေသောကြောင့် button key အတွက် စိတ်ချရသည်
        for icon, title, page_id in pages:
            label = f"{icon} {title}"
            if active == page_id:
                label = f"✅ {label}"
            
            if st.button(label, key=page_id, use_container_width=True):
                if st.session_state.active_page != page_id:
                    st.session_state.active_page = page_id
                    st.rerun()

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
            
