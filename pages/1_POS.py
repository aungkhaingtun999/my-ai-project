import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v8 Smart ERP", layout="wide")
st.title("🛒 POS v8 Shopify-Level Smart POS")

# --- Helpers ---
def safe_float(v): return float(v) if v is not None else 0.0
def norm(v): return str(v or "").lower().replace(" ", "")

if "cart" not in st.session_state: st.session_state.cart = []
products = get_products() or []

# --- Search UI ---
col1, col2 = st.columns([2, 1])

# Barcode Scanner (Always at the top)
code_search = col2.text_input("📟 Barcode / SKU (Scanner Mode)")

# Name Search (Floating Popover)
with col1:
    # popover သည် Floating Dropdown အဖြစ် အလုပ်လုပ်ပေးမည်
    with st.popover("🔍 Search Product Name (Click to Open List)", use_container_width=True):
        name_search = st.text_input("Type here to search...", label_visibility="collapsed")
        
        if name_search:
            results = [p for p in products if norm(name_search) in norm(p.get("name", ""))]
            for p in results[:8]:
                # ဤနေရာတွင် ရွေးလိုက်ပါက Popover သည် အောက်ပါ Layout ကို မထိခိုက်စေပါ
                if st.button(f"{p['name']} | {p.get('selling_price'):,.0f} MMK", key=f"btn_{p['id']}", use_container_width=True):
                    st.session_state.selected_product = p
                    st.rerun()

# --- Product Selection Detail ---
if "selected_product" in st.session_state and st.session_state.selected_product:
    p = st.session_state.selected_product
    st.divider()
    st.subheader("📦 Selected Product Detail")
    
    # Detail Area
    c1, c2, c3 = st.columns([3, 1, 1])
    c1.write(f"**{p['name']}**")
    qty = c2.number_input("Qty", 1, 100, 1)
    
    if c3.button("➕ Add to Cart", type="primary"):
        st.session_state.cart.append({**p, "qty": qty})
        st.session_state.selected_product = None
        st.rerun()

# --- Cart ---
st.divider()
st.subheader("🧾 Cart")
# (Cart Logic သည် 33.png တွင် ပြထားသည့်အတိုင်း အောက်တွင် ငြိမ်နေမည်ဖြစ်သည်)
