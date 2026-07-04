import streamlit as st
from database import get_supabase

supabase = get_supabase()

st.title("🛒 Sales Module")

products = supabase.table("products").select("*").execute().data or []

product_map = {p["name"]: p for p in products}

selected = st.selectbox("Select Product", list(product_map.keys()))
qty = st.number_input("Quantity", min_value=1, value=1)

if st.button("Sell"):
    product = product_map[selected]

    # insert sale
    supabase.table("sales").insert({
        "product_id": product["id"],
        "qty": qty,
        "price": product.get("wholesale_price", 0)
    }).execute()

    st.success("Sale recorded!")