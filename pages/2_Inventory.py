import streamlit as st
import pandas as pd
from database import db

st.set_page_config(page_title="Enterprise Product Master v4.0", layout="wide")

# --- 1. Data Fetching & Filtering ---
def get_inventory_data(selected_wh_id, search_term=None):
    query = db().table("products").select("""
        id, name, sku, barcode, purchase_price, selling_price, category, unit, minimum_stock,
        warehouse_stock!inner(qty)
    """).eq("warehouse_stock.warehouse_id", selected_wh_id).eq("is_active", True)
    
    if search_term:
        query = query.or_(f"name.ilike.%{search_term}%,sku.ilike.%{search_term}%,barcode.ilike.%{search_term}%")
    
    return query.execute().data or []

# --- 2. Analytics Calculation ---
def get_enterprise_metrics(products):
    df = pd.DataFrame([{
        **p, 
        'qty': p['warehouse_stock'][0]['qty']
    } for p in products])
    
    total_products = len(df)
    total_qty = df['qty'].sum()
    inventory_cost = (df['qty'] * df['purchase_price']).sum()
    inventory_value = (df['qty'] * df['selling_price']).sum()
    gross_profit = inventory_value - inventory_cost
    low_stock = len(df[df['qty'] <= df['minimum_stock']])
    out_of_stock = len(df[df['qty'] == 0])
    
    return total_products, total_qty, inventory_cost, inventory_value, gross_profit, low_stock, out_of_stock

# --- 3. UI Implementation ---
st.title("🏭 Enterprise Product Master v4.0")

# Warehouse Selection
warehouses = db().table("warehouses").select("*").eq("is_active", True).execute().data
wh_map = {w['name']: w['id'] for w in warehouses}
selected_wh_name = st.selectbox("📍 Select Warehouse", list(wh_map.keys()))
selected_wh_id = wh_map[selected_wh_name]

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 Product Master", "➕ Add Product", "📊 Enterprise Dashboard"])

with tab1:
    search = st.text_input("🔍 Search Products (Name, SKU, Barcode)", key="search_bar")
    products = get_inventory_data(selected_wh_id, search)
    
    # Flattened DataFrame
    display_df = pd.DataFrame([{
        'Name': p['name'], 'SKU': p['sku'], 'Barcode': p['barcode'], 
        'Qty': p['warehouse_stock'][0]['qty'], 'Cost': p['purchase_price'], 'Price': p['selling_price']
    } for p in products])
    st.dataframe(display_df, use_container_width=True)

with tab2:
    with st.form("add_product_form"):
        c1, c2 = st.columns(2)
        data = {
            "name": c1.text_input("Product Name*"),
            "sku": c1.text_input("SKU*"),
            "barcode": c2.text_input("Barcode"),
            "purchase_price": c1.number_input("Purchase Price", value=0.0),
            "selling_price": c2.number_input("Selling Price", value=0.0),
            "category": c1.selectbox("Category", ["General", "Electronics", "Stationery"]),
            "unit": c2.selectbox("Unit", ["pcs", "kg", "box"]),
            "minimum_stock": c1.number_input("Minimum Stock", value=5)
        }
        init_qty = st.number_input("Initial Stock", min_value=0)
        
        if st.form_submit_button("Save Product"):
            res = db().rpc("create_product_full", {
                "p_data": data, 
                "p_warehouse_id": selected_wh_id, 
                "p_initial_qty": int(init_qty)
            }).execute()
            
            if res.data[0]['response_json']['status'] == 'success':
                st.success("Product created successfully!")
            else:
                st.error(f"Error: {res.data[0]['response_json']['message']}")

with tab3:
    if products:
        m1, m2, m3, m4 = st.columns(4)
        total_p, total_q, cost, val, profit, low, out = get_enterprise_metrics(products)
        m1.metric("Total Products", total_p)
        m2.metric("Stock Qty", total_q)
        m3.metric("Inventory Cost", f"${cost:,.2f}")
        m4.metric("Gross Profit", f"${profit:,.2f}")
        
        m5, m6 = st.columns(2)
        m5.metric("Low Stock Alert", low, delta_color="inverse")
        m6.metric("Out of Stock", out, delta_color="inverse")
