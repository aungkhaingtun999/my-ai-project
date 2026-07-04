import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS Pro", layout="centered")

# Optimized Compact CSS
st.markdown("""
<style>
    .stNumberInput, .stSelectbox { margin-bottom: -10px !important; }
    .cart-row { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #eee; padding: 4px 0; font-size: 13px; }
    .receipt-container { background: white; color: black; padding: 15px; border: 1px solid #333; 
                         font-family: 'Courier New', monospace; width: 280px; margin: auto; }
</style>
""", unsafe_allow_html=True)

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
    c1, c2, c3 = st.columns([2, 1, 1])
    qty = c2.number_input("Qty", 1, 99, 1, key="qty_add")
    if c3.button("➕ Add"):
        st.session_state.cart.append({**selected, "qty": qty, "tax_rate": float(selected.get("tax_rate", 0)), "discount": 0.0})
        st.rerun()

# --- COMPACT CART LIST ---
if st.session_state.cart:
    st.divider()
    subtotal = 0
    total_tax = 0
    total_disc = 0
    
    for i, item in enumerate(st.session_state.cart):
        with st.container():
            st.markdown(f'<div class="cart-row"><b>{item["name"]}</b>', unsafe_allow_html=True)
            c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 0.5])
            item["qty"] = c1.number_input("Q", 1, 99, item["qty"], key=f"q_{i}", label_visibility="collapsed")
            item["tax_rate"] = c2.number_input("T%", 0.0, 100.0, float(item.get("tax_rate", 0)), key=f"t_{i}", label_visibility="collapsed")
            item["discount"] = c3.number_input("D", 0.0, 100000.0, float(item.get("discount", 0)), key=f"d_{i}", label_visibility="collapsed")
            
            p = float(item.get("selling_price", 0))
            line_total = (p * item["qty"]) - item["discount"]
            tax_amt = line_total * (item["tax_rate"] / 100)
            
            c4.write(f"{(line_total + tax_amt):,.0f}")
            if c5.button("🗑", key=f"del_{i}", label_visibility="collapsed"): st.session_state.cart.pop(i); st.rerun()
            
            subtotal += (p * item["qty"])
            total_disc += item["discount"]
            total_tax += tax_amt

    st.markdown(f"**Total:** {(subtotal - total_disc + total_tax):,.0f} MMK")

    if st.button("💳 Pay & Print", type="primary"):
        res = checkout_sale_rpc(st.session_state.cart, subtotal - total_disc + total_tax, None)
        if res and res.get("success"):
            st.success("Success!")
            # Receipt Simulation
            receipt = f"""
            <div class="receipt-container">
                <center><b>ENTERPRISE WORLD CLASS</b><br>
                Tachileik Branch<br>-------------------------------<br>
                {'<br>'.join([f"{i['name']} x{i['qty']} : {(float(i['selling_price'])*i['qty'] - i['discount']):,.0f}" for i in st.session_state.cart])}
                -------------------------------<br>
                <b>Grand Total: {(subtotal - total_disc + total_tax):,.0f} MMK</b>
            </div>
            """
            st.markdown(receipt, unsafe_allow_html=True)
            if st.button("New Sale"): st.session_state.cart = []; st.rerun()
