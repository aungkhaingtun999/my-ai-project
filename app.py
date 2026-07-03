import streamlit as st
from auth import login_page

st.set_page_config(page_title="POS System", layout="wide")

if "user" not in st.session_state:
    login_page()
else:
    st.sidebar.title("POS MENU")
    st.write("Welcome to POS System 🚀")