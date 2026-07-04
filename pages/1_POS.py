import streamlit as st
import time  # <--- Error မတက်စေရန် အရေးကြီးဆုံး Import ဖြစ်သည်
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="Professional POS", layout="centered")

# CSS: 4-Column Receipt Grid
st.markdown("""
<style>
    .receipt-container { 
        background: #fff; color: #000; padding: 20px; border: 1px solid #000; 
        font-family: 'Courier New', Courier, monospace; width: 350px; margin: auto;
    }
    .receipt-header { text-align: center; font-weight: bold; font-size: 1.2em; }
    .receipt-divider { border-top: 1px dashed #000; margin: 10px 0; }
    /* 4-Column Grid: Name, Qty, UnitPrice, Total */
    .receipt-grid { display: grid; grid-template-columns: 100px 40px 80px 80px; gap: 5px; font-size: 0.9em; }
    .receipt-total-row { display: flex; justify-content: space-between; font-weight: bold; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

if "cart" not in st.session_state: st.session_state.cart = []
products = get_products() or []
product_map = {f"{p['name']} ({p.get('sku', '')})": p for p in products}

def clear_cart():
    st.session_state.cart = []

st.subheader("🛒 Professional POS")

# Input Section
col1, col2 = st.columns(2)
barcode = col1.text_input("📟 Barcode", key="bc_in")
name = col2.selectbox("🔍 Search Name", [""] + list(product_map.keys()), key="name_in")

selected = None
if barcode:
    selected = next((p for p in products if str(p.get('barcode', '')) == barcode), None)
elif name:
    selected = product_map[name]

if selected:
    qty = st.number_input("Quantity", 1, 99, 1, key="qty_input")
    if st.button("➕ Add to Cart", type="primary"):
        uid = f"{selected['id']}_{time.time_ns()}" # Unique ID
        st.session_state.cart.append({**selected, "qty": qty, "uid": uid})
        st.rerun()

# Cart Table
if st.session_state.cart:
    st.divider()
    subtotal = 0
    for item in st.session_state.cart:
        c = st.columns([2, 1, 1, 0.5])
        c[0].write(item['name'])
        c[1].write(f"{float(item['selling_price']):,.0f}")
        item['qty'] = c[2].number_input("Qty", 1, 99, item['qty'], key=f"q_{item['uid']}")
        if c[3].button("🗑", key=f"del_{item['uid']}"):
            st.session_state.cart = [i for i in st.session_state.cart if i["uid"] != item["uid"]]
            st.rerun()
        subtotal += float(item['selling_price']) * item['qty']

    tax_rate = st.number_input("Total Tax %", 0.0, 100.0, 0.0)
    disc = st.number_input("Total Discount", 0.0, 100000.0, 0.0)
    
    tax_amount = (subtotal - disc) * (tax_rate / 100)
    final_total = subtotal - disc + tax_amount
    
    if st.button("💳 Pay & Print", type="primary"):
        res = checkout_sale_rpc(st.session_state.cart, final_total, None)
        if res and res.get("success"):
            # Generate Receipt
            receipt_rows = ""
            for i in st.session_state.cart:
                u_price = float(i["selling_price"])
                line_total = u_price * i["qty"]
                receipt_rows += f'<div class="receipt-grid"><span>{i["name"][:12]}</span><span>x{i["qty"]}</span><span>{u_price:,.0f}</span><span style="text-align:right">{line_total:,.0f}</span></div>'
            
            st.markdown(f"""
            <div class="receipt-container">
                <div class="receipt-header">AURORA LUXE RETAIL<br>Tachileik Branch</div>
                <div class="receipt-divider"></div>
                <div class="receipt-grid" style="font-weight:bold"><span>ITEM</span><span>QTY</span><span>PRICE</span><span style="text-align:right">TOTAL</span></div>
                <div class="receipt-divider"></div>
                {receipt_rows}
                <div class="receipt-divider"></div>
                <div class="receipt-total-row"><span>SUBTOTAL</span><span>{subtotal:,.0f}</span></div>
                <div class="receipt-total-row"><span>DISCOUNT</span><span>-{disc:,.0f}</span></div>
                <div class="receipt-total-row"><span>TAX</span><span>{tax_amount:,.0f}</span></div>
                <div class="receipt-total-row" style="font-size: 1.2em;"><span>GRAND TOTAL</span><span>{final_total:,.0f}</span></div>
            </div>
            """, unsafe_html=True)
            
            # New Sale button clears cart
            st.button("New Sale", on_click=clear_cart)
