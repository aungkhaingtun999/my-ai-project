import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v8 Smart ERP", layout="wide")

# --- Helpers ---
def safe_float(v): return float(v) if v is not None else 0.0
def norm(v): return str(v or "").lower().replace(" ", "")

# --- State ---
if "cart" not in st.session_state: st.session_state.cart = []
products = get_products() or []

st.title("🛒 POS v8 Smart ERP")

# --- SEARCH SECTION (Both Boxes) ---
col_s1, col_s2 = st.columns([2, 1])

# Name Search
name_query = col_s1.text_input("🔍 Search Product Name", key="name_search")
# Barcode Search
code_query = col_s2.text_input("📟 Barcode / SKU Scan", key="barcode_search")

# --- Floating Dropdown Container ---
# ဤ container သည် အောက်ပါ content များကို တွန်းမချစေရန် လုပ်ပေးသည်
dropdown_placeholder = st.empty()

# --- Search Logic ---
results = []
if name_query:
    q = norm(name_query)
    results = [p for p in products if q in norm(p.get("name", ""))]

# Barcode Match (Instant)
if code_query:
    exact = next((p for p in products if code_query in [p.get('barcode'), p.get('sku')]), None)
    if exact:
        st.session_state.cart.append({**exact, "qty": 1, "selling_price": safe_float(exact.get('selling_price'))})
        st.rerun()

# Display Floating Dropdown
if name_query and results:
    with dropdown_placeholder.container():
        st.markdown("### 🔽 Select Product")
        for p in results[:5]:
            if st.button(f"{p['name']} - {safe_float(p.get('selling_price')):,.0f} MMK", key=f"res_{p['id']}"):
                st.session_state.cart.append({**p, "qty": 1, "selling_price": safe_float(p.get('selling_price'))})
                st.rerun()
else:
    dropdown_placeholder.empty()

# --- CART SECTION ---
st.divider()
st.subheader("🧾 ခြင်းတောင်း (Cart)")

if st.session_state.cart:
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3 = st.columns([5, 2, 1])
        c1.write(f"{item['name']}")
        item["qty"] = c2.number_input("Qty", 1, 99, item["qty"], key=f"q_{i}", label_visibility="collapsed")
        if c3.button("🗑", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

    total = sum(i['selling_price'] * i['qty'] for i in st.session_state.cart)
    st.markdown(f"## Subtotal: {total:,.0f} MMK")
    
    if st.button("💳 Pay & Print", type="primary"):
        checkout_sale_rpc(st.session_state.cart, paid_amount=total)
        st.session_state.cart = []
        st.rerun()
else:
    st.info("ခြင်းတောင်း ဗလာဖြစ်နေပါသည်။")
