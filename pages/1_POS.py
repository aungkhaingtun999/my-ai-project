import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v8 Smart ERP", layout="wide")

# --- Helpers ---
def safe_float(v): return float(v) if v is not None else 0.0
def norm(v): return str(v or "").lower().replace(" ", "")

# --- State ---
if "cart" not in st.session_state: st.session_state.cart = []
if "show_detail" not in st.session_state: st.session_state.show_detail = None

products = get_products() or []

st.title("🛒 POS v8 Smart ERP")

# --- Search Area (Fixed) ---
col_s1, col_s2 = st.columns([3, 1])
name_search = col_s1.text_input("🔍 Search Product", key="name_input")
code_search = col_s2.text_input("📟 Barcode Scan", key="code_input")

# --- Floating Overlay Container ---
overlay = st.empty() 

# Logic: Search & Filter
results = []
if name_search:
    q = norm(name_search)
    results = [p for p in products if q in norm(p.get("name", ""))]

# --- Display Floating Results ---
if name_search and results:
    with overlay.container():
        # CSS to make it look like a dropdown
        st.markdown("""<style>
            div[data-testid="stVerticalBlock"] div[data-testid="stButton"] { margin: 0px !important; }
        </style>""", unsafe_allow_html=True)
        
        for p in results[:5]:
            if st.button(f"📄 {p['name']} | {p.get('selling_price'):,.0f} MMK", key=f"res_{p['id']}"):
                st.session_state.show_detail = p
                st.rerun()

# --- Product Detail (Only shows when selected) ---
if st.session_state.show_detail:
    p = st.session_state.show_detail
    with st.expander("📦 Selected Product Detail", expanded=True):
        st.write(f"**Name:** {p['name']}")
        qty = st.number_input("Quantity", 1, 100, 1)
        if st.button("➕ Add to Cart"):
            st.session_state.cart.append({**p, "qty": qty})
            st.session_state.show_detail = None
            st.rerun()
        if st.button("❌ Cancel"):
            st.session_state.show_detail = None
            st.rerun()

# --- Cart (Stays Below) ---
st.divider()
st.subheader("🧾 Cart Items")

if st.session_state.cart:
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3 = st.columns([5, 2, 1])
        c1.write(f"{item['name']} (x{item['qty']})")
        c2.write(f"{item['selling_price'] * item['qty']:,.0f} MMK")
        if c3.button("🗑", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

    total = sum(i['selling_price'] * i['qty'] for i in st.session_state.cart)
    st.markdown(f"### Total: {total:,.0f} MMK")
    if st.button("💳 Checkout"):
        checkout_sale_rpc(st.session_state.cart, paid_amount=total)
        st.session_state.cart = []
        st.rerun()
