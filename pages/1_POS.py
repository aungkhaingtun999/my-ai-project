import streamlit as st
from streamlit_searchbox import st_searchbox
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v8 Smart ERP", layout="wide")

# --- Helpers ---
def safe_float(v): return float(v) if v is not None else 0.0
def norm(v): return str(v or "").lower().replace(" ", "")

# --- State ---
if "cart" not in st.session_state: st.session_state.cart = []
products = get_products() or []

st.title("🛒 POS v8 Smart ERP")

# --- Search Logic for Searchbox ---
def search_products(searchterm: str):
    if not searchterm: return []
    return [
        (f"{p['name']} | {p.get('selling_price'):,.0f} MMK", p) 
        for p in products if norm(searchterm) in norm(p['name'])
    ]

# --- Floating Searchbox (The "Magic" Part) ---
# ဒါက page layout ကို မထိခိုက်ဘဲ dropdown လို ပေါ်နေမှာပါ
selected_product_tuple = st_searchbox(
    search_products,
    key="product_search",
    placeholder="🔍 ပစ္စည်းအမည်ရိုက်ရှာပါ..."
)

# --- Product Detail (When selected) ---
if selected_product_tuple:
    p = selected_product_tuple  # ပစ္စည်းအချက်အလက်
    st.info(f"Selected: **{p['name']}** | Price: {p['selling_price']:,.0f} MMK")
    
    col1, col2 = st.columns([1, 3])
    qty = col1.number_input("Qty", 1, 99, 1)
    if col2.button("➕ Add to Cart"):
        st.session_state.cart.append({**p, "qty": qty})
        st.rerun()

# --- Cart ---
st.divider()
st.subheader("🧾 ခြင်းတောင်း (Cart)")

if st.session_state.cart:
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3 = st.columns([5, 2, 1])
        c1.write(f"{item['name']} x {item['qty']}")
        c2.write(f"{item['selling_price'] * item['qty']:,.0f} MMK")
        if c3.button("🗑", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

    total = sum(i['selling_price'] * i['qty'] for i in st.session_state.cart)
    st.write("---")
    st.markdown(f"### Subtotal: {total:,.0f} MMK")
