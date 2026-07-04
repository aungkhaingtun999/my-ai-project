import streamlit as st
from database import get_supabase

supabase = get_supabase()

st.title("📦 Purchase Management")

products = supabase.table("products").select("*").execute().data or []

if not products:
    st.error("No products available")
    st.stop()

product_map = {p["name"]: p for p in products}

selected = st.selectbox("Select Product", list(product_map.keys()))
qty = st.number_input("Quantity", min_value=1, value=1)

if st.button("Record Purchase"):
    product = product_map[selected]

    price = float(product.get("wholesale_price") or 0)

    supabase.table("purchases").insert({
        "product_id": product["id"],
        "qty": qty,
        "price": price,
        "total": price * qty
    }).execute()

    st.success("Purchase recorded successfully")
    st.rerun()
