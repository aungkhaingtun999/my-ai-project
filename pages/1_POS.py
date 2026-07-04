import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v8 Smart ERP", layout="wide")

# Helper Functions
def safe_float(v):
    try: return float(v) if v is not None else 0.0
    except: return 0.0

# Session State
if "cart" not in st.session_state: st.session_state.cart = []
products = get_products() or []

st.title("🛒 POS v8 Smart ERP")

# ======================================================
# SEARCH & DROPDOWN SECTION
# ======================================================
# 1. Barcode/SKU Scan (Fast Add)
code_search = st.text_input("📟 Barcode / SKU (Scanner Mode)", key="scanner")
if code_search:
    found = next((p for p in products if code_search in [p.get('barcode'), p.get('sku')]), None)
    if found:
        st.session_state.cart.append({**found, "qty": 1, "selling_price": safe_float(found.get('selling_price'))})
        st.toast(f"Added {found['name']}")
        st.rerun()

# 2. Searchable Dropdown
st.write("---")
# search_term ကို အသုံးပြုပြီး selectbox ရဲ့ options တွေကို filter လုပ်ပေးပါမယ်
search_term = st.text_input("🔍 Search Product Name (Type here to filter...)", key="search_bar")

if search_term:
    filtered = [p for p in products if search_term.lower() in p.get('name', '').lower()]
    
    # ဤနေရာတွင် selectbox ကို အသုံးပြု၍ dropdown ဖြစ်အောင် ဖန်တီးသည်
    selected = st.selectbox(
        "Select a product from results:",
        options=filtered,
        format_func=lambda x: f"{x['name']} | {x.get('selling_price'):,.0f} MMK",
        index=None,
        placeholder="Choose an item..."
    )

    if selected:
        # Product တစ်ခုကို ရွေးလိုက်သည်နှင့် Cart ထဲရောက်ပြီး အလိုအလျောက် Rerun ဖြစ်မည်
        st.session_state.cart.append({**selected, "qty": 1, "selling_price": safe_float(selected.get('selling_price'))})
        st.rerun()

# ======================================================
# CART & CHECKOUT
# ======================================================
st.subheader("🧾 Current Order")
if st.session_state.cart:
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3 = st.columns([5, 2, 1])
        c1.write(item["name"])
        c2.write(f"{item['selling_price']:,.0f} MMK")
        if c3.button("❌", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

    if st.button("💳 Pay & Print", type="primary"):
        res = checkout_sale_rpc(st.session_state.cart, paid_amount=0) # Total logic here
        st.success("Transaction Complete")
        st.session_state.cart = []
        st.rerun()
