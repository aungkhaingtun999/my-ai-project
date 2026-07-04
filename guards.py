import streamlit as st

def require_login():
    user = st.session_state.get("user")

    if not user:
        st.error("⛔ Please login first")
        st.stop()

    return user


def require_admin():
    user = require_login()

    if user.get("role_id") != 1:
        st.error("⛔ Admin only module")
        st.stop()

    return user