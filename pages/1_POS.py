import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS Pro", layout="centered")

# CSS
st.markdown("""
<style>
    .cart-row { display: flex; align-items: center; border-bottom: 1px solid #ddd; padding: 5px 0; font-size: 13px; }
    .receipt-container { background: white; color: black; padding: 20px; border: 1px solid #333; 
                         font-family: 'Courier New', monospace; width: 300px; margin: auto; }
</style>
""", unsafe_allow_html=True)

if "cart" not in st.session_state: st.session_state.cart = []

products = get_products() or []
product_map = {f"{p['name']} ({p.get('sku', '')})": p for p in products}

st.subheader("🛒 Professional POS")

# --- SEARCH ---
col_s1, col_s2 = st.columns([1, 1])
barcode_input = col_s1.text_input("📟 Barcode/SKU", placeholder="Scan...")
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
            "discount": 0.0,
            "unique_id": f"{selected['id']}_{len(st.session_state.cart)}" 
        })
        st.rerun()

# --- CART DISPLAY ---
if st.session_state.cart:
    st.divider()
    # Header Titles
    c_h1, c_h2, c_h3, c_h4, c_h5 = st.columns([1.5, 1, 1, 1, 0.5])
    c_h1.write("Item")
    c_h2.write("Qty")
    c_h3.write("Tax%")
    c_h4.write("Disc")
    c_h5.write("Total")

    subtotal, total_tax, total_disc = 0, 0, 0
    
    # Callback function for delete
    def delete_item(uid):
        st.session_state.cart = [item for item in st.session_state.cart if item.get("unique_id") != uid]

    for item in st.session_state.cart:
        uid = item.get("unique_id")
        cols = st.columns([1.5, 1, 1, 1, 0.5])
        
        cols[0].write(item["name"])
        item["qty"] = cols[1].number_input("Q", 1, 99, item["qty"], key=f"q_{uid}", label_visibility="collapsed")
        item["tax_rate"] = cols[2].number_input("T", 0.0, 100.0, float(item.get("tax_rate", 0)), key=f"t_{uid}", label_visibility="collapsed")
        item["discount"] = cols[3].number_input("D", 0.0, 100000.0, float(item.get("discount", 0)), key=f"d_{uid}", label_visibility="collapsed")
        
        p = float(item.get("selling_price", 0))
        line_val = (p * item["qty"]) - item["discount"]
        tax_val = line_val * (item["tax_rate"] / 100)
        
        cols[4].button("🗑", key=f"del_{uid}", on_click=delete_item, args=(uid,))
        
        subtotal += (p * item["qty"])
        total_disc += item["discount"]
        total_tax += tax_val

    final_total = subtotal - total_disc + total_tax
    st.markdown(f"### Total Payable: {final_total:,.0f} MMK")

    if st.button("💳 Pay & Print", type="primary"):
        res = checkout_sale_rpc(st.session_state.cart, final_total, None)
        if res and res.get("success"):
            st.success("Success!")
            st.markdown(f"""
            <div class="receipt-container">
                <center><b>ENTERPRISE</b><br>Tachileik Branch</center>
                <br>Total: {final_total:,.0f} MMK
            </div>
            """, unsafe_allow_html=True)
            if st.button("New Sale"): st.session_state.cart = []; st.rerun()
