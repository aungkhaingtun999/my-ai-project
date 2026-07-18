# ==============================================================================
# pages/2_Inventory.py
# ERP ENTERPRISE PRODUCT MASTER v4.3 - PRODUCTION HARDENED
# ==============================================================================

import streamlit as st
import pandas as pd
from database import db, get_inventory_view, get_warehouses

st.set_page_config(page_title="Enterprise Product Master v4.3", layout="wide")

st.title("🏭 Enterprise Product Master v4.3")

# Warehouse Selection
warehouses = get_warehouses()
if not warehouses:
    st.error("No active warehouses found. Please check database.")
    st.stop()

wh_map = {w['name']: w['id'] for w in warehouses}
selected_wh_name = st.selectbox("📍 Select Warehouse", list(wh_map.keys()))
selected_wh_id = wh_map[selected_wh_name]

tab1, tab2, tab3 = st.tabs(["📋 Product Master", "➕ Add Product", "📊 Enterprise Dashboard"])

with tab1:
    search = st.text_input("🔍 Search Products (Name, SKU, Barcode)", key="search_bar")
    products = get_inventory_view(warehouse_id=selected_wh_id, search=search)
    
    if products:
        # HARDENING: Use .get() for safe dictionary access to avoid KeyError
        display_df = pd.DataFrame([{
            'Name': p.get('name', ''),
            'SKU': p.get('sku', ''),
            'Barcode': p.get('barcode', ''),
            'Qty': p.get('qty', 0),
            'Cost': p.get('purchase_price', 0),
            'Price': p.get('selling_price', 0)
        } for p in products])
        
        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True
        )
    else:
        st.info("No products found in this warehouse.")

with tab2:
    with st.form("add_product_form"):
        c1, c2 = st.columns(2)
        data = {
            "name": c1.text_input("Product Name*"),
            "sku": c1.text_input("SKU*"),
            "barcode": c2.text_input("Barcode"),
            "purchase_price": c1.number_input("Purchase Price", value=0.0),
            "selling_price": c2.number_input("Selling Price", value=0.0),
            "category_id": 1,
            "unit": c2.selectbox("Unit", ["pcs", "kg", "box"]),
            "minimum_stock": c1.number_input("Minimum Stock", value=5)
        }
        init_qty = st.number_input("Initial Stock", min_value=0)
        
        if st.form_submit_button("Save Product"):
            try:
                res = db().rpc("create_product_full", {
                    "p_data": data, 
                    "p_warehouse_id": int(selected_wh_id), 
                    "p_initial_qty": int(init_qty)
                }).execute()
                
                result = res.data
                if isinstance(result, list): result = result[0]
                
                if result and result.get('status') == 'success':
                    st.success("Product created successfully!")
                else:
                    st.error(f"Error: {result.get('message', 'Unknown Error')}")
            except Exception as e:
                st.error(f"Transaction failed: {str(e)}")

with tab3:
    if products:
        df = pd.DataFrame(products)
        
        # HARDENING: Ensure columns exist before processing
        if 'purchase_price' not in df.columns: df['purchase_price'] = 0
        if 'minimum_stock' not in df.columns: df['minimum_stock'] = 5
        if 'qty' not in df.columns: df['qty'] = 0
        if 'selling_price' not in df.columns: df['selling_price'] = 0

        # Analytics Calculation
        df['qty'] = pd.to_numeric(df['qty'], errors='coerce').fillna(0)
        df['purchase_price'] = pd.to_numeric(df['purchase_price'], errors='coerce').fillna(0)
        df['selling_price'] = pd.to_numeric(df['selling_price'], errors='coerce').fillna(0)
        df['minimum_stock'] = pd.to_numeric(df['minimum_stock'], errors='coerce').fillna(5)
        
        inventory_cost = (df['qty'] * df['purchase_price']).sum()
        inventory_value = (df['qty'] * df['selling_price']).sum()
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Products", len(df))
        m2.metric("Stock Qty", df['qty'].sum())
        m3.metric("Inventory Cost", f"{inventory_cost:,.2f}")
        m4.metric("Gross Profit", f"{(inventory_value - inventory_cost):,.2f}")
        
        m5, m6 = st.columns(2)
        m5.metric("Low Stock Alert", len(df[df['qty'] <= df['minimum_stock']]))
        m6.metric("Out of Stock", len(df[df['qty'] == 0]))
    else:
        st.write("No data available for dashboard.")

