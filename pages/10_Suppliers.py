import streamlit as st
from database import get_supabase

supabase = get_supabase()

st.title("🏭 Suppliers Management")

data = supabase.table("suppliers").select("*").execute().data or []

st.subheader("📋 Supplier List")

if data:
    st.dataframe(data, use_container_width=True)
else:
    st.info("No suppliers found")

st.divider()

st.subheader("➕ Add Supplier")

name = st.text_input("Supplier Name")
phone = st.text_input("Phone")
address = st.text_area("Address")

if st.button("Save Supplier"):
    if not name:
        st.error("Supplier name required")
        st.stop()

    supabase.table("suppliers").insert({
        "name": name,
        "phone": phone,
        "address": address
    }).execute()

    st.success("Supplier added successfully")
    st.rerun()
