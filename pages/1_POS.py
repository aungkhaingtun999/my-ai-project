import streamlit as st
import time
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="Professional POS", layout="centered")

# CSS: Professional Receipt Design
st.markdown("""
<style>
    .receipt-box { background: white; color: black; padding: 20px; border: 1px solid #333; 
                   font-family: 'Courier New', monospace; width: 320px; margin: auto; }
</style>
""", unsafe_allow_html=True)

# Session State Initialize
if "cart" not in st.session_state:
    st.session_state.cart = []

# Product Mapping
products = get_products() or []
product_map = {f"{p['name']} ({p.get('sku', '')})": p for p in products}

# Callback Functions
def add_to_cart():
    # ခြင်းတောင်းထဲ ပစ္စည်းထည့်ခြင်း
    if st.session_state.selected_prod:
        p = st.session_state.selected_prod
        new_item = {**p, "qty": st.session_state.qty_in, "unique_id": f"{p['id']}_{time.time_ns()}"}
        st.session_state.cart.append(new_item)

def delete_item(uid):
    st.session_state.cart = [item for item in st.session_state.cart if item["unique_id"] != uid]

def clear_cart():
    st.session_state.cart = []

st.subheader("🛒 Professional POS")

# --- SEARCH & ADD ---
c1, c2 = st.columns([1, 1])
barcode = c1.text_input("📟 Scan Barcode/SKU")
name = c2.selectbox("🔍 Search Name", [""] + list(product_map.keys()), key="name_in")

selected = None
if barcode:
    selected = next((p for p in products if barcode in [str(p.get('barcode', '')), str(p.get('sku', ''))]), None)
elif name:
    selected = product_map[name]

if selected:
    st.session_state.selected_prod = selected
    st.number_input("Qty", 1, 99, 1, key="qty_in")
    st.button("➕ Add to Cart", type="primary", on_click=add_to_cart)

# --- CART DISPLAY ---
if st.session_state.cart:
    st.divider()
    subtotal = 0
    cols = st.columns([2, 1, 1, 0.5])
    cols[0].write("**Item**"); cols[1].write("**Price**"); cols[2].write("**Qty**")
    
    for item in st.session_state.cart:
        uid = item["unique_id"]
        c = st.columns([2, 1, 1, 0.5])
        c[0].write(item['name'])
        c[1].write(f"{float(item['selling_price']):,.0f}")
        c[2].write(f"x {item['qty']}")
        c[3].button("🗑", key=f"del_{uid}", on_click=delete_item, args=(uid,))
        subtotal += float(item['selling_price']) * item['qty']

    st.divider()
    col1, col2 = st.columns(2)
    tax_rate = col1.number_input("Tax %", 0.0, 100.0, 0.0, key="tax_in")
    discount = col2.number_input("Discount (MMK)", 0.0, 100000.0, 0.0, key="disc_in")
    
    final_tax = (subtotal - discount) * (tax_rate / 100)
    final_total = subtotal - discount + final_tax
    
    st.markdown(f"### Total Payable: {final_total:,.0f} MMK")

    # --- CHECKOUT ---
    if st.button("💳 Pay & Print", type="primary"):
        res = checkout_sale_rpc(st.session_state.cart, final_total, None)
        if res and res.get("success"):
            st.success("Payment Successful!")
            receipt_str = "".join([f"{i['name'][:15]:<15} x{i['qty']} : {(float(i['selling_price'])*i['qty']):,.0f}\n" for i in st.session_state.cart])
            
            st.markdown(f"""
            <div class="receipt-box">
                <center><b>ENTERPRISE WORLD CLASS</b><br>Tachileik Branch</center>
                <pre>{receipt_str}</pre>
                -------------------------------<br>
                <b>GRAND TOTAL : {final_total:,.0f} MMK</b>
            </div>
            """, unsafe_allow_html=True)
            
            st.button("New Sale", on_click=clear_cart)
