import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v8 Smart ERP", layout="wide")

# ======================================================
# HELPER FUNCTIONS
# ======================================================
def safe_float(v):
    try: return float(v) if v is not None else 0.0
    except: return 0.0

def norm(v): return str(v or "").lower().replace(" ", "")

# ======================================================
# SESSION STATE
# ======================================================
if "cart" not in st.session_state: st.session_state.cart = []
products = get_products() or []

st.title("🛒 POS v8 Smart ERP")

# ======================================================
# SEARCH SECTION (FIXED AT TOP)
# ======================================================
# col1: Name Search, col2: Scanner
s1, s2 = st.columns([2, 1])
name_input = s1.text_input("🔍 Search Product Name", key="name_query")
barcode_input = s2.text_input("📟 Barcode / SKU Scan", key="barcode_query")

# Search Logic
search_placeholder = st.empty() # Overlay အတွက် အရေးကြီးသည်
results = []
if name_input:
    q = norm(name_input)
    results = [p for p in products if q in norm(p.get("name", ""))]

# Floating Dropdown Overlay
if name_input and results:
    with search_placeholder.container():
        st.markdown("""
        <style>
        .dropdown { position: absolute; z-index: 1000; background: white; border: 1px solid #ddd; width: 100%; padding: 10px; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            for p in results[:5]:
                if st.button(f"➕ {p['name']} - {safe_float(p.get('selling_price')):,.0f} MMK", key=f"sel_{p['id']}"):
                    st.session_state.cart.append({**p, "qty": 1, "selling_price": safe_float(p.get('selling_price'))})
                    st.rerun()

# Barcode Fast Logic
if barcode_input:
    exact = next((p for p in products if barcode_input in [p.get('barcode'), p.get('sku')]), None)
    if exact:
        st.session_state.cart.append({**exact, "qty": 1, "selling_price": safe_float(exact.get('selling_price'))})
        st.rerun()

# ======================================================
# CART SECTION
# ======================================================
st.divider()
st.subheader("🧾 ခြင်းတောင်း (Cart)")

# သန့်ရှင်းသော Cart UI
if st.session_state.cart:
    # Header
    cols = st.columns([4, 2, 2, 1])
    cols[0].write("**ပစ္စည်းအမည်**")
    cols[1].write("**Qty**")
    cols[2].write("**စုစုပေါင်း**")
    
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
        c1.write(item["name"])
        item["qty"] = c2.number_input("Qty", 1, 99, item["qty"], key=f"q_{i}", label_visibility="collapsed")
        c3.write(f"{item['selling_price'] * item['qty']:,.0f}")
        if c4.button("🗑", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

    subtotal = sum(i["selling_price"] * i["qty"] for i in st.session_state.cart)
    st.write("---")
    st.markdown(f"## Subtotal: {subtotal:,.0f} MMK")
else:
    st.info("ခြင်းတောင်း ဗလာဖြစ်နေပါသည်။")

# Clear Overlay if empty
if not name_input:
    search_placeholder.empty()
