import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS Pro", layout="centered")

if "cart" not in st.session_state: st.session_state.cart = []
if "selection_pool" not in st.session_state: st.session_state.selection_pool = []

products = get_products() or []
product_map = {f"{p['name']} ({p.get('sku', '')})": p for p in products}

def clear_all():
    st.session_state.cart = []
    st.session_state.selection_pool = []

st.subheader("🛒 Professional POS")

# --- SEARCH & SELECTION ---
c1, c2 = st.columns(2)
barcode = c1.text_input("📟 Barcode/SKU", key="bc_in")
name = c2.selectbox("🔍 Search Name", [""] + list(product_map.keys()), key="name_in")

selected = None
if barcode:
    selected = next((p for p in products if barcode in [str(p.get('barcode', '')), str(p.get('sku', ''))]), None)
elif name:
    selected = product_map[name]

# ပစ္စည်းကို ရွေးလိုက်တာနဲ့ ယာယီစာရင်း (Selection Pool) ထဲရောက်မယ်
if selected:
    # Key အသစ်ဖြစ်ကြောင်း သေချာစေရန်
    pool_item = {**selected, "uid": f"{selected['id']}_{len(st.session_state.selection_pool)}"}
    st.session_state.selection_pool.append(pool_item)
    # Search box ပြန်လည်ရှင်းလင်းရန်
    st.rerun()

# --- SELECTION POOL (ယာယီစာရင်း) ---
if st.session_state.selection_pool:
    st.write("--- ယာယီရွေးထားသော ပစ္စည်းများ ---")
    for item in st.session_state.selection_pool:
        st.write(f"✅ {item['name']}")
    
    col_a, col_b = st.columns(2)
    if col_a.button("📥 Add All to Cart", type="primary"):
        st.session_state.cart.extend(st.session_state.selection_pool)
        st.session_state.selection_pool = []
        st.rerun()
    if col_b.button("❌ Clear Selection"):
        st.session_state.selection_pool = []
        st.rerun()

# --- CART DISPLAY ---
if st.session_state.cart:
    st.divider()
    subtotal = 0
    
    def delete_item(uid): st.session_state.cart = [i for i in st.session_state.cart if i["uid"] != uid]
    
    for item in st.session_state.cart:
        c = st.columns([2, 1, 1, 0.5])
        c[0].write(item['name'])
        c[1].write(f"{float(item['selling_price']):,.0f}")
        item['qty'] = c[2].number_input("Qty", 1, 99, 1, key=f"q_{item['uid']}")
        c[3].button("🗑", key=f"del_{item['uid']}", on_click=delete_item, args=(item['uid'],))
        subtotal += float(item['selling_price']) * item['qty']

    st.divider()
    tax = st.number_input("Total Tax %", 0.0, 100.0, 0.0)
    disc = st.number_input("Total Discount", 0.0, 100000.0, 0.0)
    final_total = subtotal - disc + ((subtotal - disc) * tax / 100)
    
    st.markdown(f"### Grand Total: {final_total:,.0f} MMK")
    
    if st.button("💳 Pay & Print", type="primary"):
        res = checkout_sale_rpc(st.session_state.cart, final_total, None)
        if res and res.get("success"):
            st.success("Success!")
            st.button("New Sale", on_click=clear_all)
