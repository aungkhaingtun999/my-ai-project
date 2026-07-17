import streamlit as st
from database import (
    get_suppliers, get_warehouses, get_products, 
    purchase_receive_rpc, create_audit_log
)
from auth import is_authenticated

st.set_page_config(page_title="Purchase Order", layout="centered", page_icon="📦")

if not is_authenticated():
    st.error("ကျေးဇူးပြု၍ Login အရင်ဝင်ပါ။")
    st.stop()

st.title("📦 Purchase Receive")

# 1. Fetch Data
suppliers = get_suppliers()
warehouses = get_warehouses()
products = get_products()

if not suppliers or not warehouses or not products:
    st.error("Database တွင် Data လိုအပ်နေပါသည်။ (Supplier/Warehouse/Product)")
    st.stop()

# 2. State Management
if "purchase_cart" not in st.session_state:
    st.session_state.purchase_cart = []

# 3. Header Section with Lock Logic
cart_exists = len(st.session_state.purchase_cart) > 0

if cart_exists:
    st.info("⚠️ Cart ရှိနေပါသည်။ Supplier/Warehouse မပြောင်းပါနှင့်။")

selected_supplier = st.selectbox(
    "Supplier", 
    suppliers, 
    format_func=lambda x: x['name'],
    disabled=cart_exists
)
selected_warehouse = st.selectbox(
    "Warehouse", 
    warehouses, 
    format_func=lambda x: f"{x['name']} - {x['branch']}",
    disabled=cart_exists
)

# 4. Product Addition
st.subheader("Add Items")
with st.container(border=True):
    prod = st.selectbox("Product", products, format_func=lambda x: f"{x['name']} (SKU: {x['sku']})")
    
    col1, col2 = st.columns(2)
    qty = col1.number_input("Qty", min_value=1, value=1, step=1)
    cost = col2.number_input("Cost Price", min_value=0.0, value=float(prod.get("purchase_price") or 0.0))
    
    if st.button("➕ Add to Cart", use_container_width=True):
        existing = False
        for item in st.session_state.purchase_cart:
            if item["prod"]["id"] == prod["id"]:
                old_qty = item["qty"]
                old_cost = item["cost"]
                new_qty = old_qty + int(qty)
                item["cost"] = ((old_qty * old_cost) + (int(qty) * cost)) / new_qty
                item["qty"] = new_qty
                existing = True
                break
        
        if not existing:
            st.session_state.purchase_cart.append({"prod": prod, "qty": int(qty), "cost": cost})
        st.rerun()

# 5. Cart & Confirm
if st.session_state.purchase_cart:
    st.divider()
    st.subheader("Purchase Cart")
    
    total_amount = sum(item['qty'] * item['cost'] for item in st.session_state.purchase_cart)
    for item in st.session_state.purchase_cart:
        st.write(f"**{item['prod']['name']}** | Qty: {item['qty']} | Cost: {item['cost']:,.0f}")
    
    st.metric("Total Amount (MMK)", f"{total_amount:,.0f}")
    
    if st.button("✅ Confirm Purchase Receive", type="primary", use_container_width=True):
        user_id = st.session_state.get("user_id")
        errors = []
        success_pos = []
        
        with st.spinner("Processing..."):
            for item in st.session_state.purchase_cart:
                res = purchase_receive_rpc(
                    item['prod']['id'], selected_supplier['id'], selected_warehouse['id'],
                    int(item['qty']), item['cost'], "Mobile Purchase Entry", user_id
                )
                
                if isinstance(res, dict) and res.get("success") is True:
                    po_no = res.get("purchase_no")
                    if po_no:
                        success_pos.append(po_no)
                        create_audit_log(user_id, "PURCHASE_RECEIVE", f"PO: {po_no}, Product: {item['prod']['name']}")
                else:
                    errors.append(f"{item['prod']['name']}: {res.get('message', 'Unknown Error')}")
        
        if success_pos:
            st.success(f"Success! POs: {', '.join(success_pos)}")
            st.session_state.purchase_cart = []
            st.rerun()
        if errors:
            st.error(f"Failed: {', '.join(errors)}")
            
    if st.button("🗑 Clear Cart", use_container_width=True):
        st.session_state.purchase_cart = []
        st.rerun()
