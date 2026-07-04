import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS Pro", layout="centered")

# Professional Compact Styling
st.markdown("""
<style>
    .cart-item { font-size: 13px; border-bottom: 1px solid #eee; padding: 5px 0; }
    .receipt-box { background: #f9f9f9; padding: 15px; border: 1px dashed #ccc; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

if "cart" not in st.session_state: st.session_state.cart = []
products = get_products() or []
product_map = {f"{p['name']} ({p.get('sku', '')})": p for p in products}

st.subheader("🛒 POS System")

# --- SEARCH ---
selected_label = st.selectbox("🔍 Search", [""] + list(product_map.keys()))
if selected_label:
    selected = product_map[selected_label]
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        c1.markdown(f"**{selected['name']}**")
        c1.caption(f"💰 {float(selected.get('selling_price',0)):,.0f} | Tax: {selected.get('tax_rate',0)}% | Disc: {'YES' if selected.get('discount_allowed') else 'NO'}")
        qty = c2.number_input("Qty", 1, 99, 1, key="q_input")
        if c2.button("➕ Add"):
            item = {**selected, "qty": qty}
            found = False
            for c in st.session_state.cart:
                if c["id"] == item["id"]: c["qty"] += qty; found = True
            if not found: st.session_state.cart.append(item)
            st.rerun()

# --- CART DISPLAY (WITH TAX & DISC BOX) ---
if st.session_state.cart:
    st.divider()
    subtotal = 0
    total_tax = 0
    
    for i, item in enumerate(st.session_state.cart):
        p = float(item.get('selling_price', 0))
        t = float(item.get('tax_rate', 0))
        d = item.get('discount_allowed', False)
        l_total = p * item['qty']
        t_amt = l_total * (t / 100)
        
        # Display Row
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.markdown(f"**{item['name']}**<br><small>Tax: {t}% | Disc: {'✅' if d else '❌'}</small>", unsafe_allow_html=True)
        c2.number_input("Q", 1, 99, item['qty'], key=f"q_{i}", label_visibility="collapsed")
        c3.write(f"**{(l_total+t_amt):,.0f}**")
        if c3.button("🗑", key=f"del_{i}"): st.session_state.cart.pop(i); st.rerun()
        
        subtotal += l_total
        total_tax += t_amt

    st.divider()
    st.markdown(f"### Total: {(subtotal + total_tax):,.0f} MMK")

    # --- CHECKOUT & RECEIPT ---
    if st.button("💳 Pay & Print", type="primary"):
        prepared = [{
            "id": i["id"], "qty": i["qty"], "selling_price": float(i["selling_price"]),
            "tax_rate": float(i.get("tax_rate", 0)), "discount_allowed": bool(i.get("discount_allowed", False))
        } for i in st.session_state.cart]
        
        res = checkout_sale_rpc(prepared, subtotal + total_tax, None)
        
        if res and res.get("success"):
            # World-Class Receipt Design
            receipt_html = f"""
            <div class="receipt-box">
                <center><b>ENTERPRISE WORLD CLASS</b><br>
                Tachileik Branch<br>
                -------------------------------<br>
                Receipt: {res.get('receipt_no')}<br>
                Date: 2026-07-05 01:30<br>
                -------------------------------</center>
                {'<br>'.join([f"{i['name']} x{i['qty']} : {(float(i['selling_price'])*i['qty']):,.0f}" for i in st.session_state.cart])}<br>
                -------------------------------<br>
                <b>Grand Total: {(subtotal + total_tax):,.0f} MMK</b><br>
                <center>Thank You!</center>
            </div>
            """
            st.success("Transaction Successful!")
            st.markdown(receipt_html, unsafe_allow_html=True)
            if st.button("Clear Receipt"): 
                st.session_state.cart = []
                st.rerun()
        else:
            st.error("Checkout Failed")
