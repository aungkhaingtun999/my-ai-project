import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS Pro", layout="centered")

# CSS: Professional Receipt & Compact Layout
st.markdown("""
<style>
    .cart-row { font-size: 13px; border-bottom: 1px solid #eee; padding: 5px 0; }
    .receipt-box { background: white; color: black; padding: 20px; border: 1px solid #333; 
                   font-family: 'Courier New', monospace; width: 320px; margin: auto; }
</style>
""", unsafe_allow_html=True)

if "cart" not in st.session_state: st.session_state.cart = []

products = get_products() or []
product_map = {f"{p['name']} ({p.get('sku', '')})": p for p in products}

st.subheader("🛒 Professional POS")

# --- SEARCH ---
c1, c2 = st.columns([1, 1])
barcode = c1.text_input("📟 Scan Barcode/SKU")
name = c2.selectbox("🔍 Search Name", [""] + list(product_map.keys()))

selected = None
if barcode:
    selected = next((p for p in products if barcode in [str(p.get('barcode', '')), str(p.get('sku', ''))]), None)
elif name:
    selected = product_map[name]

if selected:
    qty = st.number_input("Qty", 1, 99, 1, key="add_qty")
    if st.button(f"➕ Add {selected['name']} to Cart"):
        st.session_state.cart.append({
            **selected, "qty": qty, "tax_rate": float(selected.get("tax_rate", 0)), 
            "discount": 0.0, "unique_id": f"{selected['id']}_{len(st.session_state.cart)}"
        })
        st.rerun()

# --- CART ---
if st.session_state.cart:
    st.divider()
    # Headers
    cols = st.columns([2, 1, 1, 1, 1, 0.5])
    cols[0].write("**Item**"); cols[1].write("**Price**"); cols[2].write("**Qty**"); cols[3].write("**Tax%**"); cols[4].write("**Disc**")

    subtotal, total_tax, total_disc = 0, 0, 0
    
    def delete_item(uid):
        st.session_state.cart = [i for i in st.session_state.cart if i["unique_id"] != uid]

    for item in st.session_state.cart:
        uid = item["unique_id"]
        c = st.columns([2, 1, 1, 1, 1, 0.5])
        c[0].write(item['name'])
        c[1].write(f"{float(item['selling_price']):,.0f}") # Unit Price
        item["qty"] = c[2].number_input("Q", 1, 99, item["qty"], key=f"q_{uid}", label_visibility="collapsed")
        item["tax_rate"] = c[3].number_input("T", 0.0, 100.0, float(item["tax_rate"]), key=f"t_{uid}", label_visibility="collapsed")
        item["discount"] = c[4].number_input("D", 0.0, 100000.0, float(item["discount"]), key=f"d_{uid}", label_visibility="collapsed")
        c[5].button("🗑", key=f"del_{uid}", on_click=delete_item, args=(uid,))
        
        # Calculate
        line_price = float(item['selling_price']) * item["qty"]
        line_tax = (line_price - item["discount"]) * (item["tax_rate"] / 100)
        subtotal += line_price
        total_disc += item["discount"]
        total_tax += line_tax

    final_total = subtotal - total_disc + total_tax
    st.markdown(f"### Total Payable: {final_total:,.0f} MMK")

    if st.button("💳 Pay & Print", type="primary"):
        res = checkout_sale_rpc(st.session_state.cart, final_total, None)
        if res and res.get("success"):
            st.success("Success!")
            # World Class Receipt
            receipt_items = "".join([f"{i['name'][:15]:<15} x{i['qty']} : {(float(i['selling_price'])*i['qty'] - i['discount']):,.0f}\n" for i in st.session_state.cart])
            st.markdown(f"""
            <div class="receipt-box">
                <center><b>ENTERPRISE WORLD CLASS</b><br>Tachileik Branch<br>-------------------------------</center>
                <pre>{receipt_items}</pre>
                -------------------------------<br>
                <b>SUBTOTAL :</b> {subtotal-total_disc:,.0f}<br>
                <b>TAX      :</b> {total_tax:,.0f}<br>
                <b>TOTAL    :</b> {final_total:,.0f} MMK<br>
                <center>Thank You! Come Again.</center>
            </div>
            """, unsafe_allow_html=True)
            if st.button("New Sale"): st.session_state.cart = []; st.rerun()
