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
# FLOATING SEARCH SECTION
# ======================================================
# Popover အသုံးပြုခြင်းဖြင့် page အောက်မဆင်းဘဲ ပေါ်လာစေမည်
with st.popover("🔍 ရှာဖွေရန် နှိပ်ပါ", use_container_width=True):
    name_search = st.text_input("Product အမည်ရိုက်ထည့်ပါ", "")
    
    if name_search:
        q = norm(name_search)
        results = [p for p in products if q in norm(p.get("name", ""))]
        
        if results:
            for p in results[:8]:
                if st.button(f"{p['name']} ({p.get('selling_price', 0):,.0f} MMK)", key=f"res_{p['id']}"):
                    # Cart ထဲထည့်ခြင်း
                    st.session_state.cart.append({
                        **p, 
                        "qty": 1, 
                        "selling_price": safe_float(p.get('selling_price'))
                    })
                    st.rerun()
        else:
            st.warning("မတွေ့ရှိပါ။")

# Barcode Scanner Mode
code_search = st.text_input("📟 Barcode / SKU Scan", "")
if code_search:
    exact = next((p for p in products if code_search in [p.get('barcode'), p.get('sku')]), None)
    if exact:
        st.session_state.cart.append({**exact, "qty": 1, "selling_price": safe_float(exact.get('selling_price'))})
        st.rerun()

# ======================================================
# CART SECTION
# ======================================================
st.divider()
st.subheader("🧾 ခြင်းတောင်း (Cart)")

if st.session_state.cart:
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
        c1.write(f"**{item['name']}**")
        item["qty"] = c2.number_input("Qty", 1, 99, item["qty"], key=f"qty_{i}")
        c3.write(f"{(item['selling_price'] * item['qty']):,.0f} MMK")
        if c4.button("🗑", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

    subtotal = sum(i["selling_price"] * i["qty"] for i in st.session_state.cart)
    st.markdown(f"### Subtotal: {subtotal:,.0f} MMK")

    if st.button("💳 Pay & Print", type="primary"):
        res = checkout_sale_rpc(st.session_state.cart, paid_amount=subtotal)
        st.session_state.cart = []
        st.rerun()
else:
    st.info("ခြင်းတောင်း ဗလာဖြစ်နေပါသည်။")
