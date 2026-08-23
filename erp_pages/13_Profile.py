# ==============================================================================
# erp_pages/13_Profile.py
# ERP ENTERPRISE - MY PROFILE
# ==============================================================================

import streamlit as st
import auth


def run():

    user = auth.get_current_user()

    if not user:
        st.error("Please login first.")
        st.stop()

    st.title("👤 My Profile")

    # ==========================================================================
    # USER INFORMATION
    # ==========================================================================

    st.write(
        f"**Username:** {user.get('username', '')}"
    )

    st.write(
        f"**Full Name:** {user.get('full_name', '')}"
    )

    st.write(
        f"**Role:** {user.get('role', '')}"
    )

    if user.get("shop_name"):
        st.write(
            f"**Shop:** {user.get('shop_name')}"
        )

    if user.get("branch_name"):
        st.write(
            f"**Branch:** {user.get('branch_name')}"
        )

    st.divider()

    # ==========================================================================
    # CHANGE PASSWORD
    # ==========================================================================

    st.subheader("🔐 Change Password")

    old_password = st.text_input(
        "Current Password",
        type="password",
        key="profile_old_password"
    )

    new_password = st.text_input(
        "New Password",
        type="password",
        key="profile_new_password"
    )

    confirm_password = st.text_input(
        "Confirm New Password",
        type="password",
        key="profile_confirm_password"
    )

    if st.button(
        "💾 Change Password",
        use_container_width=True,
        key="profile_change_password"
    ):

        if not old_password:
            st.error("Please enter your current password.")
            return

        if not new_password:
            st.error("Please enter a new password.")
            return

        if not confirm_password:
            st.error("Please confirm your new password.")
            return

        if new_password != confirm_password:
            st.error("Password confirmation does not match.")
            return

        success, message = auth.change_password(
            user["id"],
            old_password,
            new_password
        )

        if success:
            st.success(message)

            # Clear password fields after successful change
            st.session_state["profile_old_password"] = ""
            st.session_state["profile_new_password"] = ""
            st.session_state["profile_confirm_password"] = ""

        else:
            st.error(message)


if __name__ == "__main__":
    run()
