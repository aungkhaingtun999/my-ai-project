import streamlit as st
from database import get_supabase

supabase = get_supabase()

st.title("🔁 Warehouse Transfer")

warehouses = supabase.table("warehouses").select("*").execute().data or []
products = supabase.table("products").select("*").execute().data or []

w_map = {w["name"]: w for w in warehouses}
p_map = {p["name"]: p for p in products}

from_w = st.selectbox("From Warehouse", list(w_map.keys()))
to_w = st.selectbox("To Warehouse", list(w_map.keys()))
product = st.selectbox("Product", list(p_map.keys()))
qty = st.number_input("Qty", min_value=1, value=1)

if st.button("Transfer"):
    supabase.table("stock_transfers").insert({
        "from_warehouse_id": w_map[from_w]["id"],
        "to_warehouse_id": w_map[to_w]["id"],
        "product_id": p_map[product]["id"],
        "qty": qty,
        "status": "done"
    }).execute()

    st.success("Transfer completed!")