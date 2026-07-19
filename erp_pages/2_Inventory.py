# ==============================================================================
# pages/2_Inventory.py
# ERP ENTERPRISE PRODUCT MASTER v4.3 - PRODUCTION HARDENED
# ==============================================================================

import streamlit as st
import pandas as pd
from database import db, get_inventory_view, get_warehouses

def run():
    # Page configuration must be set at the top of the function
    # Note: If this is a page inside 'pages/' folder, set_page_config is already 
    # handled by the main app, but we can include it for safety.
    
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
            display_df = pd.DataFrame([{
                'Name': p.get('name', ''),
                'SKU': p.get('sku', ''),
                'Barcode': p.get('barcode', ''),
                'Qty': p.get('qty', 0),
                'Cost': p.get('purchase_price', 0),
                'Price': p.get('selling_price', 0)
            } for p in products])
            
            st.dataframe(display_df, width=None, hide_index=True) # width="stretch" deprecated in some versions, replaced with None or default
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
        # Re-fetch or use existing products logic
        products = get_inventory_view(warehouse_id=selected_wh_id)
        if products:
            df = pd.DataFrame(products)
            # HARDENING: Ensure columns exist
            for col in ['purchase_price', 'minimum_stock', 'qty', 'selling_price']:
                if col not in df.columns: df[col] = 0
            
            df['qty'] = pd.to_numeric(df['qty'], errors='coerce').fillna(0)
            # ... (rest of the dashboard logic)
            
            inventory_cost = (df['qty'] * df['purchase_price']).sum()
            inventory_value = (df['qty'] * df['selling_price']).sum()
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Products", len(df))
            m2.metric("Stock Qty", df['qty'].sum())
            m3.metric("Inventory Cost", f"{inventory_cost:,.2f}")
            m4.metric("Gross Profit", f"{(inventory_value - inventory_cost):,.2f}")
        else:
            st.write("No data available for dashboard.")

if __name__ == "__main__":
    run()
                    
