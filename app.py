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
        "role": None,
        "active_page": "pages/1_POS.py", # Default Landing Page
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
    """
    Load pages dynamically using file path locations.
    Bypasses Streamlit's default page handling for secure control.
    """
    page_file = st.session_state.get("active_page", "pages/1_POS.py")

    # Handle Custom Logic Pages
    if page_file == "dashboard":
        st.title("🏭 ERP Control Dashboard")
        st.info("Welcome to the Enterprise Core.")
        return

    # Check if file exists
    if not os.path.exists(page_file):
        st.error(f"Page file not found: {page_file}")
        return

    try:
        # Load module from file path
        spec = importlib.util.spec_from_file_location("erp_page", page_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Execute the main function of the module
        if hasattr(module, 'run'):
            module.run()
        else:
            st.error(f"Module '{page_file}' does not contain a 'run()' function.")

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

    # 2. User validation (Security Guard)
    user = st.session_state.get("user")
    if not user or not isinstance(user, dict):
        st.session_state.clear()
        st.rerun()

    # 3. Render Sidebar
    try:
        show_sidebar()
    except Exception as e:
        st.sidebar.error("Sidebar loading error.")

    # 4. Render Main Page
    page_router()

    # 5. Global Logout footer
    st.sidebar.divider()
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

if __name__ == "__main__":
    main()
    
