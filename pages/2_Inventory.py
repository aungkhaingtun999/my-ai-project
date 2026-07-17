import streamlit as st
from database import db
from datetime import datetime

st.set_page_config(page_title="Inventory Management", layout="wide")
st.title("📦 Inventory Management v2.0")

# --- Warehouse Selector ---
warehouses = db().table("warehouses").select("*").eq("is_active", True).execute().data or []
if not warehouses:
    st.error("No active warehouse found. Please create one first.")
    st.stop()

wh_map = {w['name']: w['id'] for w in warehouses}
selected_wh_name = st.selectbox("📍 Select Warehouse", list(wh_map.keys()))
selected_wh_id = wh_map[selected_wh_name]

# --- 1. Add Product with Stock Protection ---
with st.expander("➕ Add New Product"):
    c1, c2 = st.columns(2)
    name = c1.text_input("Name")
    sku = c1.text_input("SKU")
    init_stock = c2.number_input("Initial Stock", min_value=0, step=1)
    
    if st.button("Save New Product", type="primary"):
        if not name: 
            st.error("Name required")
        else:
            # 1. SKU Duplicate Protection
            dup = db().table("products").select("id").eq("sku", sku).execute()
            if dup.data:
                st.error("SKU already exists")
            else:
                # 2. Transaction Handling (Atomic Operation)
                # Suggestion: Use Supabase RPC 'create_product_with_stock' here
                res = db().table("products").insert({"name": name, "sku": sku, "is_active": True}).execute()
                
                if not res.data:
                    st.error("Product creation failed")
                else:
                    new_prod = res.data[0]
                    # Insert Stock
                    db().table("warehouse_stock").insert({
                        "product_id": new_prod['id'],
                        "warehouse_id": selected_wh_id,
                        "qty": int(init_stock)
                    }).execute()
                    
                    # Insert Log with Timestamp
                    if int(init_stock) > 0:
                        db().table("inventory_logs").insert({
                            "product_id": new_prod['id'],
                            "warehouse_id": selected_wh_id,
                            "qty_before": 0,
                            "qty_change": int(init_stock),
                            "qty_after": int(init_stock),
                            "transaction_type": "INITIAL",
                            "reason": "Opening Stock",
                            "created_at": datetime.now().isoformat()
                        }).execute()
                    st.success("Product created successfully!")
                    st.rerun()

# --- 2. Inventory Listing (Nested Select Fix) ---
st.divider()
products = (
    db()
    .table("products")
    .select("""
        id, name, sku,
        warehouse_stock!inner(qty, warehouse_id)
    """)
    .eq("warehouse_stock.warehouse_id", selected_wh_id)
    .eq("is_active", True)
    .order("id")
    .execute()
    .data or []
)

# Dashboard Metrics
total_qty = sum(p['warehouse_stock'][0]['qty'] for p in products)
st.metric("Total Items", total_qty)

for p in products:
    curr_stock = p['warehouse_stock'][0]['qty']
    cols = st.columns([3, 1, 1, 1])
    cols[0].write(f"🛒 {p.get('name')}")
    cols[1].write(f"SKU: {p.get('sku')}")
    cols[2].write(f"Qty: **{curr_stock}**")
    
    with cols[3]:
        if st.button("❌ Delete", key=f"d_{p['id']}"):
            if curr_stock > 0:
                st.error("Cannot delete: Stock exists!")
            else:
                db().table("products").update({"is_active": False}).eq("id", p['id']).execute()
                st.rerun()
