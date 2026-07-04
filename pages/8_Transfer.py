import streamlit as st
from database import get_supabase

supabase = get_supabase()

st.title("🔁 Warehouse Transfer System")

warehouses = supabase.table("warehouses").select("*").execute().data or []
products = supabase.table("products").select("*").execute().data or []

if not warehouses or not products:
    st.error("Missing warehouses or products")
    st.stop()

w_map = {w["name"]: w for w in warehouses}
p_map = {p["name"]: p for p in products}

from_w = st.selectbox("From Warehouse", list(w_map.keys()))
to_w = st.selectbox("To Warehouse", list(w_map.keys()))
product_name = st.selectbox("Product", list(p_map.keys()))
qty = st.number_input("Quantity", min_value=1, value=1)

if from_w == to_w:
    st.error("Source and destination cannot be same")
    st.stop()

if st.button("Execute Transfer"):
    product = p_map[product_name]

    supabase.table("stock_transfers").insert({
        "from_warehouse_id": w_map[from_w]["id"],
        "to_warehouse_id": w_map[to_w]["id"],
        "product_id": product["id"],
        "qty": qty,
        "status": "completed"
    }).execute()

    st.success("Transfer completed successfully")
    st.rerun()
