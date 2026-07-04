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
if "selection_pool" not in st.session_state: st.session_state.selection_pool = []

products = get_products() or []
product_map = {f"{p['name']} ({p.get('sku', '')})": p for p in products}

st.subheader("🛒 Professional POS")

# 1. Barcode Scanner (အပေါ်မှာ သီးသန့်)
barcode = st.text_input("📟 Barcode Scanner", key="bc_input", placeholder="Scan here...")
if barcode:
    selected = next((p for p in products if str(p.get('barcode')) == barcode), None)
    if selected:
        st.session_state.selection_pool.append({**selected, "uid": f"{selected['id']}_{len(st.session_state.selection_pool)}"})
        st.rerun()

# 2. Name Search (အောက်မှာ သီးသန့်)
name = st.selectbox("🔍 Search Name", [""] + list(product_map.keys()), key="name_input")
if name:
    selected = product_map[name]
    st.session_state.selection_pool.append({**selected, "uid": f"{selected['id']}_{len(st.session_state.selection_pool)}"})
    st.rerun()

# 3. Selection Pool (ယာယီရွေးထားသော ပစ္စည်းများ)
if st.session_state.selection_pool:
    st.write("--- ယာယီရွေးထားသော ပစ္စည်းများ ---")
    for i, item in enumerate(st.session_state.selection_pool):
        c1, c2 = st.columns([4, 1])
        c1.write(f"{i+1}. {item['name']}")
        if c2.button("❌", key=f"del_pool_{item['uid']}"):
            st.session_state.selection_pool.pop(i)
            st.rerun()

    c_a, c_b = st.columns(2)
    if c_a.button("📥 Add All to Cart", type="primary"):
        st.session_state.cart.extend(st.session_state.selection_pool)
        st.session_state.selection_pool = []
        st.rerun()
    if c_b.button("🗑 Clear All Selection"):
        st.session_state.selection_pool = []
        st.rerun()

# 4. Cart & Receipt
if st.session_state.cart:
    st.divider()
    subtotal = 0
    def delete_item(uid): st.session_state.cart = [i for i in st.session_state.cart if i["uid"] != uid]
    
    for item in st.session_state.cart:
        c = st.columns([2, 1, 1, 0.5])
        c[0].write(item['name'])
        c[1].write(f"{float(item['selling_price']):,.0f}")
        item['qty'] = c[2].number_input("Qty", 1, 99, item.get('qty', 1), key=f"q_{item['uid']}")
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
            receipt_lines = "".join([f"{i['name'][:15]:<15} x{i['qty']} : {(float(i['selling_price'])*i['qty']):,.0f}\n" for i in st.session_state.cart])
            st.markdown(f"""
            <div class="receipt-box">
                <center><b>ENTERPRISE WORLD CLASS</b><br>Tachileik Branch</center>
                <pre>{receipt_lines}</pre>
                -------------------------------<br>
                <b>GRAND TOTAL : {final_total:,.0f} MMK</b>
            </div>
            """, unsafe_allow_html=True)
            if st.button("New Sale"):
                st.session_state.cart = []
                st.rerun()
