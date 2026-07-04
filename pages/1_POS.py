import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS Pro", layout="centered")

# Styling
st.markdown("""
<style>
    .cart-box { background: #f0f2f6; padding: 10px; border-radius: 8px; margin-bottom: 5px; font-size: 13px; }
    .receipt-container { background: white; color: black; padding: 20px; border: 2px solid #333; 
                         font-family: 'Courier New', monospace; width: 300px; margin: auto; }
</style>
""", unsafe_allow_html=True)

if "cart" not in st.session_state: st.session_state.cart = []
products = get_products() or []

st.subheader("🛒 Professional POS")

# --- BARCODE / SKU SEARCH ---
barcode_input = st.text_input("📟 Scan Barcode or Type SKU", placeholder="Enter code...")
product_map = {f"{p['name']} ({p.get('sku', '')})": p for p in products}
selected = None

if barcode_input:
    # Barcode/SKU ဖြင့် ရှာဖွေခြင်း
    match = next((p for p in products if barcode_input in [str(p.get('barcode', '')), str(p.get('sku', ''))]), None)
    if match:
        selected = match
    else:
        st.error("Product not found!")
else:
    # နာမည်ဖြင့် ရှာဖွေခြင်း (Fallback)
    name_search = st.selectbox("🔍 Or Search by Name", [""] + list(product_map.keys()))
    if name_search:
        selected = product_map[name_search]

# --- PRODUCT ADDITION ---
if selected:
    with st.container(border=True):
        st.markdown(f"**{selected['name']}**")
        qty = st.number_input("Qty", 1, 99, 1, key="qty_add")
        if st.button("➕ Add to Cart"):
            st.session_state.cart.append({**selected, "qty": qty})
            st.rerun()

# --- CART DISPLAY ---
if st.session_state.cart:
    st.divider()
    subtotal = 0
    total_tax = 0
    
    for i, item in enumerate(st.session_state.cart):
        with st.container():
            st.markdown(f'<div class="cart-box"><b>{item["name"]}</b>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([2, 1, 1])
            item["tax_rate"] = c1.number_input("Tax %", 0.0, 100.0, float(item.get("tax_rate", 0)), key=f"t_{i}")
            item["qty"] = c2.number_input("Qty", 1, 99, item["qty"], key=f"q_{i}")
            if c3.button("🗑", key=f"del_{i}"): st.session_state.cart.pop(i); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            subtotal += float(item.get("selling_price", 0)) * item["qty"]
            total_tax += (float(item.get("selling_price", 0)) * item["qty"]) * (item["tax_rate"] / 100)

    st.markdown(f"### Total Payable: {(subtotal + total_tax):,.0f} MMK")

    # --- CHECKOUT ---
    if st.button("💳 Pay & Print", type="primary"):
        res = checkout_sale_rpc(st.session_state.cart, subtotal + total_tax, None)
        if res and res.get("success"):
            st.success("Payment Successful!")
            receipt_html = f"""
            <div class="receipt-container">
                <center><b>ENTERPRISE WORLD CLASS</b><br>
                Tachileik Branch<br>
                -------------------------------<br>
                Date: {st.session_state.get('now', '2026-07-05')}<br>
                Receipt #: {res.get('receipt_no')}<br>
                -------------------------------</center>
                {''.join([f"{i['name']} x{i['qty']} : {(float(i['selling_price'])*i['qty']):,.0f}<br>" for i in st.session_state.cart])}
                -------------------------------<br>
                <b>TOTAL TAX: {total_tax:,.0f}</b><br>
                <b>GRAND TOTAL: {(subtotal + total_tax):,.0f} MMK</b><br>
                <center>Thank You!</center>
            </div>
            """
            st.markdown(receipt_html, unsafe_allow_html=True)
            if st.button("New Sale"): st.session_state.cart = []; st.rerun()
        else:
            st.error("Checkout Failed")
