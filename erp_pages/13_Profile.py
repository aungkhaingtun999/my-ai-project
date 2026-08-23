import streamlit as st
import sys
import os
import importlib

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import auth module
import auth

# Force reload to get latest version
importlib.reload(auth)

# Get functions directly from module
require_login = auth.require_login
change_password = auth.change_password

def run():
    user = require_login()

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
            success, message = change_password(
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
