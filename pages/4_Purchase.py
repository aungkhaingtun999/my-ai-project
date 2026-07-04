import streamlit as st
from database import get_supabase

supabase = get_supabase()

st.title("📦 Purchase Module")

products = supabase.table("products").select("*").execute().data or []

product_map = {p["name"]: p for p in products}

selected = st.selectbox("Product", list(product_map.keys()))
qty = st.number_input("Qty", min_value=1, value=1)

if st.button("Purchase"):
    product = product_map[selected]

    supabase.table("purchases").insert({
        "product_id": product["id"],
        "qty": qty,
        "price": product.get("wholesale_price", 0)
    }).execute()

    st.success("Purchase recorded!")