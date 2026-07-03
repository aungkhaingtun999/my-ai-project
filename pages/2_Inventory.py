import streamlit as st

st.title("Inventory Management")

name = st.text_input("Product Name")
price = st.number_input("Price")

if st.button("Add"):
    st.success("Product added (connect DB later)")