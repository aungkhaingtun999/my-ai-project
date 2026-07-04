import streamlit as st
from database import get_products, checkout_sale_rpc

# Page Config
st.set_page_config(page_title="POS Pro", layout="centered")

# Compact Styling
st.markdown("""
<style>
    .cart-row { display: flex; align-items: center; border-bottom: 1px solid #ddd; padding: 5px 0; font-size: 13px; }
    .receipt-container { background: white; color: black; padding: 20px; border: 1px solid #333; 
                         font-family: 'Courier New', monospace; width: 300px; margin: auto; }
    .stNumberInput { margin-bottom: -10px !important; }
</style>
""", unsafe_allow_html=True)

# Session State
if "cart" not in st.session_state: st.session_state.cart = []

products = get_products() or []
product_map = {f"{p['name']} ({p.get('sku', '')})": p for p in products}

st.subheader("🛒 Professional POS")

# --- SEARCH ---
col_s1, col_s2 = st.columns([1, 1])
barcode_input = col_s1.text_input("📟 Barcode/SKU", placeholder="Scan/Type...")
name_search = col_s2.selectbox("🔍 Search Name", [""] + list(product_map.keys()))

selected = None
if barcode_input:
    selected = next((p for p in products if barcode_input in [str(p.get('barcode', '')), str(p.get('sku', ''))]), None)
elif name_search:
    selected = product_map[name_search]

if selected:
    c1, c2 = st.columns([3, 1])
    qty = c2.number_input("Qty", 1, 99, 1, key="qty_add")
    if c1.button(f"➕ Add {selected['name']}", type="primary"):
        st.session_state.cart.append({
            **selected, "qty": qty, 
            "tax_rate": float(selected.get("tax_rate", 0)), 
            "discount": 0.0
        })
        st.rerun()

# --- CART DISPLAY ---
if st.session_state.cart:
    st.divider()
    subtotal, total_tax, total_disc = 0, 0, 0
    delete_index = None
    
    for i, item in enumerate(st.session_state.cart):
        st.markdown(f'<div class="cart-row"><b>{item["name"]}</b></div>', unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns([1.5, 1, 1, 1, 0.5])
        
        item["qty"] = c1.number_input("Q", 1, 99, item["qty"], key=f"q_{i}", label_visibility="collapsed")
        item["tax_rate"] = c2.number_input("Tax%", 0.0, 100.0, float(item.get("tax_rate", 0)), key=f"t_{i}", label_visibility="collapsed")
        item["discount"] = c3.number_input("Disc", 0.0, 100000.0, float(item.get("discount", 0)), key=f"d_{i}", label_visibility="collapsed")
        
        p = float(item.get("selling_price", 0))
        line_val = (p * item["qty"]) - item["discount"]
        tax_val = line_val * (item["tax_rate"] / 100)
        c4.write(f"**{(line_val + tax_val):,.0f}**")
        
        if c5.button("🗑", key=f"del_{i}", label_visibility="collapsed"): delete_index = i
        
        subtotal += (p * item["qty"])
        total_disc += item["discount"]
        total_tax += tax_val

    if delete_index is not None:
        st.session_state.cart.pop(delete_index)
        st.rerun()

    final_total = subtotal - total_disc + total_tax
    st.markdown(f"### Total Payable: {final_total:,.0f} MMK")

    # --- CHECKOUT ---
    if st.button("💳 Pay & Print", type="primary"):
        res = checkout_sale_rpc(st.session_state.cart, final_total, None)
        if res and res.get("success"):
            st.success("Success!")
            # Receipt
            receipt_items = "".join([f"{i['name']} x{i['qty']} : {(float(i['selling_price'])*i['qty'] - i['discount']):,.0f}<br>" for i in st.session_state.cart])
            receipt_html = f"""
            <div class="receipt-container">
                <center><b>ENTERPRISE WORLD CLASS</b><br>Tachileik Branch<br>-------------------------------</center>
                {receipt_items}
                -------------------------------<br>
                <b>SUBTOTAL: {(subtotal-total_disc):,.0f}</b><br>
                <b>TAX: {total_tax:,.0f}</b><br>
                <b>GRAND TOTAL: {final_total:,.0f} MMK</b><br>
                <center>Thank You!</center>
            </div>
            """
            st.markdown(receipt_html, unsafe_allow_html=True)
            if st.button("New Sale"): st.session_state.cart = []; st.rerun()
        else:
            st.error("Checkout Failed")
