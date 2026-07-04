import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="Professional POS", layout="centered")

# CSS: Professional Receipt Layout
st.markdown("""
<style>
    .receipt-box { background: white; color: black; padding: 20px; border: 1px solid #333; 
                   font-family: 'Courier New', monospace; width: 320px; margin: auto; }
</style>
""", unsafe_allow_html=True)

if "cart" not in st.session_state: st.session_state.cart = []

products = get_products() or []
product_map = {f"{p['name']} ({p.get('sku', '')})": p for p in products}

st.subheader("🛒 Professional POS")

# 1. Search Sections
col1, col2 = st.columns(2)
barcode = col1.text_input("📟 Barcode", key="bc_in")
name = col2.selectbox("🔍 Search Name", [""] + list(product_map.keys()), key="name_in")

# Logic to pick selected product
selected = None
if barcode:
    selected = next((p for p in products if str(p.get('barcode', '')) == barcode), None)
elif name:
    selected = product_map[name]

# 2. Add to Cart Button (ရွေးပြီးမှ နှိပ်ရမည့် အဆင့်)
if selected:
    qty = st.number_input("Quantity", 1, 99, 1, key="qty_input")
    if st.button("➕ Add to Cart", type="primary"):
        # Unique ID ထည့်သွင်းခြင်း
        uid = f"{selected['id']}_{len(st.session_state.cart)}"
        st.session_state.cart.append({**selected, "qty": qty, "uid": uid})
        st.rerun()

# 3. Cart Display
if st.session_state.cart:
    st.divider()
    subtotal = 0
    
    def delete_item(uid): st.session_state.cart = [i for i in st.session_state.cart if i["uid"] != uid]
    
    for item in st.session_state.cart:
        c = st.columns([2, 1, 1, 0.5])
        c[0].write(item['name'])
        c[1].write(f"{float(item['selling_price']):,.0f}")
        item['qty'] = c[2].number_input("Qty", 1, 99, item['qty'], key=f"q_{item['uid']}")
        c[3].button("🗑", key=f"del_{item['uid']}", on_click=delete_item, args=(item['uid'],))
        subtotal += float(item['selling_price']) * item['qty']

    # Checkout
    tax = st.number_input("Total Tax %", 0.0, 100.0, 0.0)
    disc = st.number_input("Total Discount", 0.0, 100000.0, 0.0)
    final_total = subtotal - disc + ((subtotal - disc) * tax / 100)
    
    st.markdown(f"### Grand Total: {final_total:,.0f} MMK")
    
    if st.button("💳 Pay & Print", type="primary"):
        res = checkout_sale_rpc(st.session_state.cart, final_total, None)
        if res and res.get("success"):
            st.success("Payment Successful!")
            # Receipt Display
            items_lines = "".join([f"{i['name'][:15]:<15} x{i['qty']} : {(float(i['selling_price'])*i['qty']):,.0f}\n" for i in st.session_state.cart])
            st.markdown(f"""
            <div class="receipt-box">
                <center><b>ENTERPRISE WORLD CLASS</b><br>Tachileik Branch</center>
                <pre>{items_lines}</pre>
                -------------------------------<br>
                <b>GRAND TOTAL : {final_total:,.0f} MMK</b>
            </div>
            """, unsafe_allow_html=True)
            if st.button("New Sale"):
                st.session_state.cart = []
                st.rerun()
