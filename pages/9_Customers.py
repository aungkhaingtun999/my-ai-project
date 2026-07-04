import streamlit as st
from database import get_supabase

supabase = get_supabase()

st.title("👥 Customers Management")

data = supabase.table("customers").select("*").execute().data or []

st.subheader("Customer List")

if data:
    st.dataframe(data, use_container_width=True)
else:
    st.info("No customers found")

st.divider()

st.subheader("➕ Add Customer")

name = st.text_input("Customer Name")
phone = st.text_input("Phone")
address = st.text_area("Address")

if st.button("Save Customer"):
    if not name:
        st.error("Name required")
        st.stop()

    supabase.table("customers").insert({
        "name": name,
        "phone": phone,
        "address": address
    }).execute()

    st.success("Customer added successfully")
    st.rerun()
