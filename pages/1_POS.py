import streamlit as st
import time
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="Professional POS", layout="centered")

# CSS
st.markdown("""
<style>
    .receipt-box { background: white; color: black; padding: 20px; border: 1px solid #333; 
                   font-family: 'Courier New', monospace; width: 320px; margin: auto; }
</style>
""", unsafe_allow_html=True)

# Session State Initialize
if "cart" not in st.session_state: st.session_state.cart = []
if "temp_list" not in st.session_state: st.session_state.temp_list = []

products = get_products() or []
product_map = {f"{p['name']} ({p.get('sku', '')})": p for p in products}

# Callbacks
def add_to_temp(p, qty):
    st.session_state.temp_list.append({**p, "qty": qty, "uid": time.time_ns()})

def delete_temp(uid):
    st.session_state.temp_list = [i for i in st.session_state.temp_list if i["uid"] != uid]

def confirm_sale():
    st.session_state.cart.extend(st.session_state.temp_list)
    st.session_state.temp_list = []

def clear_all():
    st.session_state.cart = []
    st.session_state.temp_list = []

st.subheader("🛒 Professional POS")

# --- SEARCH ---
c1, c2 = st.columns(2)
barcode = c1.text_input("📟 Barcode/SKU", key="bc_in")
name = c2.selectbox("🔍 Search Name", [""] + list(product_map.keys()), key="name_in")

selected = None
# Logic: Barcode မရှိမှ Name ကို စစ်သည် (Error မဖြစ်စေရန်)
if barcode:
    selected = next((p for p in products if barcode in [str(p.get('barcode', '')), str(p.get('sku', ''))]), None)
elif name:
    selected = product_map[name]

if selected:
    qty = st.number_input("Qty", 1, 99, 1, key="q_in")
    if st.button("➕ Add to Selection"):
        add_to_temp(selected, qty)
        st.rerun()

# --- TEMP SELECTION ---
if st.session_state.temp_list:
    st.write("--- Selection List ---")
    for item in st.session_state.temp_list:
        c = st.columns([2, 1, 0.5])
        c[0].write(f"{item['name']} x {item['qty']}")
        c[1].button("🗑", key=f"del_t_{item['uid']}", on_click=delete_temp, args=(item['uid'],))
    
    if st.button("✅ Confirm All to Cart", type="primary"):
        confirm_sale()
        st.rerun()

# --- CART DISPLAY ---
if st.session_state.cart:
    st.divider()
    subtotal = 0
    for item in st.session_state.cart:
        c = st.columns([2, 1, 1])
        c[0].write(item['name'])
        c[1].write(f"x {item['qty']}")
        c[2].write(f"{(float(item['selling_price'])*item['qty']):,.0f}")
        subtotal += float(item['selling_price']) * item['qty']

    # Checkout Section
    tax_rate = st.number_input("Total Tax %", 0.0, 100.0, 0.0)
    discount = st.number_input("Total Discount", 0.0, 100000.0, 0.0)
    final_total = subtotal - discount + ((subtotal - discount) * tax_rate / 100)
    
    st.markdown(f"### Payable: {final_total:,.0f} MMK")
    
    if st.button("💳 Pay & Print"):
        res = checkout_sale_rpc(st.session_state.cart, final_total, None)
        if res and res.get("success"):
            st.success("Success!")
            st.button("New Sale", on_click=clear_all)
