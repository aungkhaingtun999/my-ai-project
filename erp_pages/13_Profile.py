import streamlit as st
import auth


def run():

    user = auth.get_current_user()

    if not user:
        st.error("Please login first")
        st.stop()

    st.title("👤 My Profile")

    st.write(f"Username : {user.get('username', '')}")
    st.write(f"Full Name : {user.get('full_name', '')}")
    st.write(f"Role : {user.get('role', '')}")

    st.divider()

    st.subheader("🔐 Change Password")

    old_password = st.text_input(
        "Current Password",
        type="password"
    )

    new_password = st.text_input(
        "New Password",
        type="password"
    )

    confirm_password = st.text_input(
        "Confirm New Password",
        type="password"
    )

    if st.button(
        "💾 Change Password",
        use_container_width=True
    ):

        if not old_password or not new_password:
            st.error("Please fill all fields")

        elif new_password != confirm_password:
            st.error("Password confirmation does not match")

        else:

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
