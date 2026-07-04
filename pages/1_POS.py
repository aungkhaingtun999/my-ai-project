import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS Pro", layout="centered")

# CSS: Professional Receipt
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

# --- SEARCH ---
c1, c2 = st.columns([1, 1])
barcode = c1.text_input("📟 Barcode/SKU")
name = c2.selectbox("🔍 Search Name", [""] + list(product_map.keys()))

selected = next((p for p in products if barcode in [str(p.get('barcode', '')), str(p.get('sku', ''))]), None) if barcode else (product_map[name] if name else None)

if selected:
    qty = st.number_input("Qty", 1, 99, 1)
    if st.button("➕ Add to Cart", type="primary"):
        st.session_state.cart.append({**selected, "qty": qty})
        st.rerun()

# --- CART ---
if st.session_state.cart:
    st.divider()
    subtotal = 0
    
    # Header
    cols = st.columns([2, 1, 1, 0.5])
    cols[0].write("**Item**"); cols[1].write("**Price**"); cols[2].write("**Qty**")
    
    def delete_item(uid): st.session_state.cart = [i for i in st.session_state.cart if i["id"] != uid]

    for item in st.session_state.cart:
        c = st.columns([2, 1, 1, 0.5])
        c[0].write(item['name'])
        c[1].write(f"{float(item['selling_price']):,.0f}")
        c[2].write(f"x {item['qty']}")
        c[3].button("🗑", key=f"del_{item['id']}", on_click=delete_item, args=(item['id'],))
        subtotal += float(item['selling_price']) * item['qty']

    st.divider()
    # Total Tax/Discount Inputs
    col1, col2 = st.columns(2)
    total_tax_rate = col1.number_input("Total Tax %", 0.0, 100.0, 0.0)
    total_discount = col2.number_input("Total Discount (MMK)", 0.0, 100000.0, 0.0)
    
    final_tax = (subtotal - total_discount) * (total_tax_rate / 100)
    final_total = subtotal - total_discount + final_tax
    
    st.markdown(f"### Total Payable: {final_total:,.0f} MMK")

    if st.button("💳 Pay & Print", type="primary"):
        res = checkout_sale_rpc(st.session_state.cart, final_total, None)
        if res and res.get("success"):
            st.success("Success!")
            # Receipt Display
            items_str = "".join([f"{i['name']:<15} x{i['qty']} : {(float(i['selling_price'])*i['qty']):,.0f}\n" for i in st.session_state.cart])
            st.markdown(f"""
            <div class="receipt-box">
                <center><b>ENTERPRISE WORLD CLASS</b><br>Tachileik Branch</center>
                <pre>{items_str}</pre>
                -------------------------------<br>
                <b>SUBTOTAL :</b> {subtotal:,.0f}<br>
                <b>DISCOUNT :</b> {total_discount:,.0f}<br>
                <b>TAX ({total_tax_rate}%) :</b> {final_tax:,.0f}<br>
                <b>GRAND TOTAL : {final_total:,.0f} MMK</b>
                <center>Thank You!</center>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("New Sale"): 
                st.session_state.cart = []
                st.rerun()
