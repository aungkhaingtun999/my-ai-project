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
# SEARCH SECTION
# ======================================================
c_name, c_code = st.columns([2, 1])

with c_name:
    name_search = st.text_input("🔍 Search Product Name", key="name_input")
    dropdown_placeholder = st.empty()
    
    if name_search:
        results = [p for p in products if name_search.lower() in str(p.get('name', '')).lower()]
        if results:
            with dropdown_placeholder.container():
                for p in results[:5]:
                    if st.button(f"📄 {p['name']} | {safe_float(p.get('selling_price')):,.0f} MMK", key=f"sel_{p['id']}", use_container_width=True):
                        st.session_state.selected_product = p
                        st.rerun()

with c_code:
    code_search = st.text_input("📟 Barcode / SKU Scan", key="code_input")
    if code_search:
        match = next((p for p in products if code_search in [str(p.get('barcode', '')), str(p.get('sku', ''))]), None)
        if match:
            st.session_state.selected_product = match
            st.rerun()

# ======================================================
# SELECTED PRODUCT DETAIL (Logic with clean data)
# ======================================================
if st.session_state.selected_product:
    p = st.session_state.selected_product
    st.divider()
    st.subheader("📦 Product Detail")
    
    col_d1, col_d2, col_d3 = st.columns([3, 1, 1])
    col_d1.write(f"**{p['name']}**")
    qty = col_d2.number_input("Qty", 1, 100, 1, key="q_input")
    
    if col_d3.button("➕ Add to Cart", type="primary"):
        # CLEAN DATA: API Error မတက်စေရန် လိုအပ်သော data သီးသန့်သာ ထည့်ပါ
        cart_item = {
            "id": p["id"],
            "name": p["name"],
            "selling_price": safe_float(p.get("selling_price")),
            "qty": qty
        }
        
        # Check existing
        found = False
        for item in st.session_state.cart:
            if item["id"] == cart_item["id"]:
                item["qty"] += qty
                found = True
        if not found:
            st.session_state.cart.append(cart_item)
        
        st.session_state.selected_product = None
        st.rerun()

# ======================================================
# CART
# ======================================================
st.divider()
st.subheader("🧾 Cart")

if st.session_state.cart:
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
        c1.write(item["name"])
        item["qty"] = c2.number_input("Qty", 1, 99, item["qty"], key=f"q_{i}", label_visibility="collapsed")
        c3.write(f"{(item['selling_price'] * item['qty']):,.0f} MMK")
        if c4.button("🗑", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

    subtotal = sum(i["selling_price"] * i["qty"] for i in st.session_state.cart)
    st.markdown(f"### Total: {subtotal:,.0f} MMK")
    
    # [FIX] Pay & Print Button Logic အတွက် အစားထိုးရန်
    if st.button("💳 Pay & Print", type="primary"):
        if not st.session_state.cart:
            st.error("ခြင်းတောင်း ဗလာဖြစ်နေပါသည်။")
            st.stop()

        # Database Schema နှင့် ကိုက်ညီသော သန့်စင်ပြီးသား Data ဖွဲ့စည်းပုံ
        # Schema တွင်ပါသော အဓိကလိုအပ်သည့် column များသာ ထည့်ပါ
        prepared_cart = []
        for item in st.session_state.cart:
            prepared_cart.append({
                "id": int(item["id"]),             # bigint
                "qty": int(item["qty"]),           # integer
                "selling_price": float(item["selling_price"]) # numeric
            })

        # API သို့ စနစ်တကျ ပေးပို့ခြင်း
        try:
            result = checkout_sale_rpc(prepared_cart, paid_amount=float(subtotal))
            
            if isinstance(result, dict) and result.get("error"):
                st.error(f"Error: {result.get('error')}")
            else:
                st.success("အရောင်း အောင်မြင်ပါသည်။")
                st.session_state.cart = [] # Cart ရှင်းခြင်း
                st.rerun()
        except Exception as e:
            st.error(f"API Connection Error: {str(e)}")
