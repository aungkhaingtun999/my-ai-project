import streamlit as st
import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import auth module - DO NOT use from auth import
import auth

def run():
    # Use auth.require_login() instead of require_login()
    user = auth.require_login()

    st.title("👤 My Profile")

    st.write(f"Username : {user['username']}")

    st.divider()

    st.subheader("🔐 Change Password")

    old_password = st.text_input("Current Password", type="password")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")

    if st.button("💾 Change Password", use_container_width=True):
        if not old_password or not new_password:
            st.error("Please fill all fields")
        elif new_password != confirm_password:
            st.error("Password confirmation does not match")
        elif len(new_password) < 6:
            st.error("Password must be at least 6 characters")
        else:
            # Use auth.change_password() directly
            success, message = auth.change_password(
                user["id"],
                old_password,
                new_password
            )

            if success:
                st.success(message)
            else:
                st.error(message)

if __name__ == "__main__":
    run()
