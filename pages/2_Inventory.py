# ==============================================================================
# pages/2_Inventory.py
# ERP ENTERPRISE PRODUCT MASTER v4.2 - PRODUCTION HARDENED
# ==============================================================================

import streamlit as st
import pandas as pd
from database import db, get_inventory_view, get_warehouses

st.set_page_config(page_title="Enterprise Product Master v4.2", layout="wide")

# --- 1. UI Implementation ---
st.title("🏭 Enterprise Product Master v4.2")

# Warehouse Selection
warehouses = get_warehouses()
if not warehouses:
    st.error("No active warehouses found. Please check database.")
    st.stop()

wh_map = {w['name']: w['id'] for w in warehouses}
selected_wh_name = st.selectbox("📍 Select Warehouse", list(wh_map.keys()))
selected_wh_id = wh_map[selected_wh_name]

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 Product Master", "➕ Add Product", "📊 Enterprise Dashboard"])

with tab1:
    search = st.text_input("🔍 Search Products (Name, SKU, Barcode)", key="search_bar")
    
    products = get_inventory_view(warehouse_id=selected_wh_id, search=search)
    
    if products:
        display_df = pd.DataFrame([{
            'Name': p['name'], 'SKU': p['sku'], 'Barcode': p['barcode'], 
            'Qty': p['qty'], 'Cost': p.get('purchase_price', 0), 'Price': p['selling_price']
        } for p in products])
        st.dataframe(display_df, width=None) # Corrected for newer Streamlit
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
            "category_id": 1, # Database FK requirement
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
                
                # Robust RPC response handling
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
        # --- Analytics Calculation ---
        df = pd.DataFrame(products)
        
        # Ensure numeric types
        df['qty'] = pd.to_numeric(df['qty'], errors='coerce').fillna(0)
        df['purchase_price'] = pd.to_numeric(df.get('purchase_price', 0), errors='coerce').fillna(0)
        df['selling_price'] = pd.to_numeric(df.get('selling_price', 0), errors='coerce').fillna(0)
        df['minimum_stock'] = pd.to_numeric(df.get('minimum_stock', 5), errors='coerce').fillna(5)
        
        total_p = len(df)
        total_q = df['qty'].sum()
        
        inventory_cost = (df['qty'] * df['purchase_price']).sum()
        inventory_value = (df['qty'] * df['selling_price']).sum()
        gross_profit = inventory_value - inventory_cost
        
        # Alerts
        low_stock = len(df[df['qty'] <= df['minimum_stock']])
        out_of_stock = len(df[df['qty'] == 0])
        
        # UI Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Products", total_p)
        m2.metric("Stock Qty", total_q)
        m3.metric("Inventory Cost", f"{inventory_cost:,.2f}")
        m4.metric("Gross Profit", f"{gross_profit:,.2f}")
        
        m5, m6 = st.columns(2)
        m5.metric("Low Stock Alert", low_stock)
        m6.metric("Out of Stock", out_of_stock)
    else:
        st.write("No data available for dashboard.")
        
