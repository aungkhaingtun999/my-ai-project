# ==========================================================
# utils/notification.py
# ERP ENTERPRISE NOTIFICATION ENGINE
# ==========================================================

import streamlit as st


def notify_success(message):
    st.session_state["notification"] = {
        "type": "success",
        "message": message
    }


def notify_error(message):
    st.session_state["notification"] = {
        "type": "error",
        "message": message
    }


def notify_warning(message):
    st.session_state["notification"] = {
        "type": "warning",
        "message": message
    }


def show_notification():

    if "notification" not in st.session_state:
        return


    data = st.session_state["notification"]

    msg_type = data.get("type")
    message = data.get("message")


    if msg_type == "success":
        st.success(message)

    elif msg_type == "error":
        st.error(message)

    elif msg_type == "warning":
        st.warning(message)


    del st.session_state["notification"]