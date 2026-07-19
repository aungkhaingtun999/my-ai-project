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

# ... (MENU dictionary သည် သင်ပေးထားသည့်အတိုင်း အပြည့်အစုံထားရှိပါ) ...

# ==========================================================
# ACTIVE PAGE (Default Page Logic အသစ်)
# ==========================================================
def get_active_page():
    if "active_page" not in st.session_state:
        user = current_user()
        # Admin ဆိုလျှင် Dashboard၊ ကျန်သူများအတွက် POS
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

    # Role Field အမှန်ဖြစ်စေရန် ပြင်ဆင်ထားသည့် Logic
    role_display = (
        user.get("role")
        or user.get("role_name")
        or (get_role_name(role_id) if 'get_role_name' in globals() else None)
        or "Staff"
    )

    with st.sidebar:
        st.title("🏭 Myanmar ERP")
        st.caption("Enterprise Edition")
        st.divider()

        # USER CARD
        st.success(f"👤 {user.get('full_name', user.get('username', 'User'))}")
        st.caption(f"Username : {user.get('username', '')}")
        st.caption(f"Role : {role_display}") # ပြင်ဆင်ထားသော Role display

        st.divider()

        # LANGUAGE (ယခင်အတိုင်း)
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
        pages = MENU.get(role_id, [])

        for icon, title, page_id in pages:
            label = f"{icon} {title}"
            if active == page_id:
                label = f"✅ {label}"

            if st.button(label, key=f"nav_{page_id}", use_container_width=True):
                st.session_state.active_page = page_id
                st.rerun()

        st.divider()
        # STATUS & LOGOUT (ယခင်အတိုင်း)
        st.success("🟢 System Online")
        st.caption("Database : Connected")
        st.caption("Session : Active")
        st.caption("ERP Version : Enterprise")
        st.divider()

        if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
            logout()
            st.rerun()
            
