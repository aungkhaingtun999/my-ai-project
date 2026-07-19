import streamlit as st
import importlib.util
import os
from auth import login_page, is_authenticated
from sidebar import show_sidebar

# ==========================================
# PAGE CONFIG (MUST BE FIRST)
# ==========================================
st.set_page_config(
    page_title="Myanmar ERP Enterprise",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# SESSION INIT
# ==========================================
def init_state():
    defaults = {
        "user": None,
        "active_page": "1_POS", # Default Landing Page ID
        "language": "English",
        "auth_checked": False
    }
    for k, v in defaults.items():  
        st.session_state.setdefault(k, v)

init_state()

# ==========================================
# DYNAMIC FILE LOADER (PRODUCTION ENGINE)
# ==========================================
def page_router():
    # Security Gate: Login မရှိပါက Page Load မပေးပါ
    if not st.session_state.get("user"):
        st.error("Please login first")
        return

    # Sidebar မှလာသော page_id ကိုရယူခြင်း
    page_id = st.session_state.get("active_page", "1_POS")

    # Dashboard Logic
    if page_id == "dashboard":
        st.title("🏭 ERP Control Dashboard")
        st.info("Welcome to Enterprise Core.")
        return

    # Absolute Path တည်ဆောက်ခြင်း
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "erp_pages", f"{page_id}.py")

    # File တည်ရှိမှု စစ်ဆေးခြင်း
    if not os.path.exists(file_path):
        st.error(f"Page file not found: {file_path}")
        return

    try:
        # Load Module Dynamically
        spec = importlib.util.spec_from_file_location("erp_page", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Execute run()
        if hasattr(module, "run"):
            module.run()
        else:
            st.error(f"{page_id}.py must contain run()")

    except Exception as e:
        st.error(f"Page Load Error: {e}")

# ==========================================
# MAIN CONTROLLER
# ==========================================
def main():
    # 1. Login Gate
    if not is_authenticated():
        login_page()
        st.stop()

    # 2. Render Sidebar
    try:
        show_sidebar()
    except Exception as e:
        st.sidebar.error("Sidebar loading error.")

    # 3. Render Main Page
    page_router()

if __name__ == "__main__":
    main()
