import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v8 Smart ERP", layout="wide")

# ======================================================
# HELPERS
# ======================================================
def safe_float(v):
    try: return float(v) if v is not None else 0.0
    except: return 0.0

# ======================================================
# SESSION STATE
# ======================================================
if "cart" not in st.session_state: st.session_state.cart = []
if "selected_product" not in st.session_state: st.session_state.selected_product = None

products = get_products() or []

st.title("🛒 POS v8 Shopify-Level Smart POS")

# ======================================================
# SEARCH SECTION (Floating Dropdown Feel)
# ======================================================
c_name, c_code = st.columns([2, 1])

with c_name:
    name_search = st.text_input("🔍 Search Product Name", key="name_input")
    
    # Dropdown List ကို Placeholder နဲ့ ထိန်းထားခြင်း (အောက်ကဟာတွေကို မတွန်းချဘူး)
    dropdown_placeholder = st.empty()
    
    if name_search:
        results = [p for p in products if name_search.lower() in p['name'].lower()]
        if results:
            with dropdown_placeholder.container():
                # Floating Style စာရင်း
                for p in results[:5]:
                    if st.button(f"📄 {p['name']} | {safe_float(p.get('selling_price')):,.0f} MMK", key=f"sel_{p['id']}", use_container_width=True):
                        st.session_state.selected_product = p
                        st.rerun()
        else:
            dropdown_placeholder.info("မတွေ့ရှိပါ")

with c_code:
    code_search = st.text_input("📟 Barcode / SKU (Scanner Mode)")
    if code_search:
        match = next((p for p in products if code_search in [p.get('barcode'), p.get('sku')]), None)
        if match:
            st.session_state.selected_product = match
            st.rerun()

# ======================================================
# SELECTED PRODUCT DETAIL
# ======================================================
if st.session_state.selected_product:
    p = st.session_state.selected_product
    st.divider()
    st.subheader("📦 Product Detail")
    
    col_d1, col_d2, col_d3 = st.columns([3, 1, 1])
    col_d1.write(f"**{p['name']}**")
    qty = col_d2.number_input("Qty", 1, 100, 1, key="q_input")
    
    if col_d3.button("➕ Add to Cart", type="primary"):
        # Cart ထဲထည့်ခြင်း (Existing check)
        found = False
        for item in st.session_state.cart:
            if item["id"] == p["id"]:
                item["qty"] += qty
                found = True
        if not found:
            st.session_state.cart.append({**p, "qty": qty, "selling_price": safe_float(p.get("selling_price"))})
        
        st.session_state.selected_product = None # ပစ္စည်းရွေးပြီးတာနဲ့ Detail ပိတ်မယ်
        st.rerun()

# ======================================================
# CART (PERSISTENT)
# ======================================================
st.divider()
st.subheader("🧾 Cart")

if st.session_state.cart:
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
        c1.write(item["name"])
        # Qty ပြင်ဆင်ခြင်း
        new_qty = c2.number_input("Qty", 1, 99, item["qty"], key=f"q_{i}", label_visibility="collapsed")
        item["qty"] = new_qty
        c3.write(f"{(item['selling_price'] * item['qty']):,.0f} MMK")
        if c4.button("🗑", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

    subtotal = sum(i["selling_price"] * i["qty"] for i in st.session_state.cart)
    st.markdown(f"### Total: {subtotal:,.0f} MMK")
    
    if st.button("💳 Pay & Print", type="primary"):
        checkout_sale_rpc(st.session_state.cart, paid_amount=subtotal)
        st.session_state.cart = [] # ရှင်းပြီးရင် Cart ပြန်လည်ရှင်းထုတ်မယ်
        st.rerun()
else:
    st.info("ခြင်းတောင်း ဗလာဖြစ်နေပါသည်။")
