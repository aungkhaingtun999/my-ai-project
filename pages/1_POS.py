import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v8 Smart ERP", layout="wide")

st.title("🛒 POS v8 Smart ERP")

# ======================================================
# HELPERS
# ======================================================
def safe_float(v):
    try: return float(v) if v is not None else 0.0
    except: return 0.0

def norm(v): return str(v or "").lower().replace(" ", "")

# ======================================================
# SESSION STATE
# ======================================================
if "cart" not in st.session_state: st.session_state.cart = []

# ======================================================
# SEARCH LOGIC
# ======================================================
products = get_products() or []

# Search Section (Top Inline)
col_s1, col_s2 = st.columns([2, 1])
name_search = col_s1.text_input("🔍 Search Product Name", "", key="name_input")
code_search = col_s2.text_input("📟 Barcode / SKU Scan", "", key="code_input")

# Logic to match
results = []
if name_search:
    q = norm(name_search)
    results = [p for p in products if q in norm(p.get("name", ""))]

# Handle Barcode (Instant add if exact match)
if code_search:
    exact = next((p for p in products if code_search in [p.get('barcode'), p.get('sku')]), None)
    if exact:
        st.session_state.cart.append({**exact, "qty": 1, "selling_price": safe_float(exact.get('selling_price'))})
        st.toast(f"Added {exact['name']} via Scanner")
        st.rerun()

# ======================================================
# FLOATING DROPDOWN UI
# ======================================================
if name_search and results:
    with st.container():
        st.markdown("### 🔽 Search Results")
        for p in results[:5]: # Show top 5
            label = f"{p['name']} - {safe_float(p.get('selling_price')):,.0f} MMK"
            if st.button(label, key=f"btn_{p['id']}"):
                # Add to cart immediately or open quantity dialog
                st.session_state.cart.append({**p, "qty": 1, "selling_price": safe_float(p.get('selling_price'))})
                st.rerun()

# ======================================================
# CART DISPLAY
# ======================================================
st.divider()
st.subheader("🧾 Current Order")

if st.session_state.cart:
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
        c1.write(item["name"])
        qty = c2.number_input("Qty", 1, 99, item["qty"], key=f"q_{i}")
        item["qty"] = qty
        c3.write(f"{item['selling_price'] * qty:,.0f} MMK")
        if c4.button("❌", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

    subtotal = sum(i["selling_price"] * i["qty"] for i in st.session_state.cart)
    
    col_t1, col_t2 = st.columns(2)
    discount = col_t1.number_input("Discount (%)", 0.0, 100.0, 0.0)
    tax = col_t2.number_input("Tax (%)", 0.0, 100.0, 5.0)
    
    total = subtotal * (1 - discount/100) * (1 + tax/100)
    st.metric("TOTAL AMOUNT", f"{total:,.0f} MMK")

    if st.button("💳 Pay & Print", type="primary"):
        res = checkout_sale_rpc(st.session_state.cart, paid_amount=total)
        if res and not res.get("error"):
            st.success("Transaction Successful!")
            st.session_state.cart = []
            st.rerun()
        else:
            st.error("Checkout Failed")
else:
    st.info("Cart is empty. Scan a barcode or search to add items.")
