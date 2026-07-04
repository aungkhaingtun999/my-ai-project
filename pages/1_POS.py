import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v8 Smart ERP", layout="wide")

st.title("🛒 POS v8 Shopify-Level Smart POS")

# ======================================================
# SAFE FLOAT & NORMALIZE
# ======================================================
def safe_float(v):
    try:
        return float(v) if v is not None else 0.0
    except:
        return 0.0

def norm(v):
    return str(v or "").lower().replace(" ", "")

# ======================================================
# SESSION STATE
# ======================================================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "selected_product" not in st.session_state:
    st.session_state.selected_product = None

# ======================================================
# LOAD PRODUCTS
# ======================================================
products = get_products() or []

# ======================================================
# SEARCH INPUTS (Both Barcode and Name Restored Side-by-Side)
# ======================================================
col_s1, col_s2 = st.columns([2, 1])
name_search = col_s1.text_input("🔍 Search Product Name", "")
code_search = col_s2.text_input("📟 Barcode / SKU (Scanner Mode)", "")

# Floating Inline Dropdown Feel အတွက် နေရာလွတ် ကြိုယူထားခြင်း
dropdown_placeholder = st.empty()

# ======================================================
# 1. NAME SEARCH LOGIC
# ======================================================
name_results = []
if name_search:
    q = norm(name_search)
    name_results = [p for p in products if q in norm(p.get("name", ""))]
    name_results = name_results[:8]

# ======================================================
# 2. BARCODE / SKU SEARCH LOGIC (Instant Auto-Select)
# ======================================================
if code_search:
    q = norm(code_search)
    exact = next((p for p in products if q == norm(p.get("barcode")) or q == norm(p.get("sku"))), None)
    if exact:
        st.session_state.selected_product = exact
        st.toast("Product Scanned ✔")

# ======================================================
# FLOATING DROPDOWN UI (NAME SEARCH ONLY)
# ======================================================
if name_search and name_results:
    with dropdown_placeholder.container():
        st.markdown("### 🔽 Name Suggestions")
        for p in name_results:
            label = f"{p['name']} | {p.get('barcode')} | {p.get('sku')} | {safe_float(p.get('selling_price')):,.0f} MMK"
            if st.button(label, key=f"drop_{p['id']}", use_container_width=True):
                st.session_state.selected_product = p
                st.rerun()
else:
    dropdown_placeholder.empty()

# ======================================================
# SELECTED PRODUCT DETAIL (Show only when selected)
# ======================================================
p = st.session_state.selected_product

if p:
    st.divider()
    st.subheader("📦 Selected Product Detail")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.write(f"**{p['name']}**")
        st.caption(f"{p.get('barcode')} | {p.get('sku')} | {p.get('unit','pcs')}")

    with col2:
        st.write(f"💰 **{safe_float(p.get('selling_price')):,.0f} MMK**")

    qty = st.number_input("Quantity to add", 1, 100, 1, key="detail_qty")

    c_btn1, c_btn2 = st.columns([1, 4])
    
    if c_btn1.button("➕ Add to Cart", type="primary"):
        pid = p["id"]

        for item in st.session_state.cart:
            if item["id"] == pid:
                item["qty"] += qty
                break
        else:
            # STRICT ORIGINAL DICTIONARY STRUCTURE (API Error မတက်စေရန် စနစ်တကျ ထည့်သွင်းခြင်း)
            st.session_state.cart.append({
                "id": pid,
                "name": p["name"],
                "barcode": p.get("barcode"),
                "sku": p.get("sku"),
                "unit": p.get("unit", "pcs"),
                "selling_price": safe_float(p.get("selling_price")),
                "qty": qty
            })

        st.session_state.selected_product = None
        st.success("Added to cart successfully!")
        st.rerun()
        
    if c_btn2.button("❌ Cancel"):
        st.session_state.selected_product = None
        st.rerun()

# ======================================================
# CART SECTION
# ======================================================
st.divider()
st.subheader("🧾 Cart Items")

subtotal = 0

if st.session_state.cart:
    for i, item in enumerate(st.session_state.cart):
        line = item["selling_price"] * item["qty"]
        subtotal += line

        c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
        c1.write(item["name"])
        
        # Cart အတွင်း တိုက်ရိုက် အရေအတွက် ပြောင်းလဲနိုင်ခြင်း
        new_qty = c2.number_input("Qty", 1, 100, item["qty"], key=f"cart_q_{i}", label_visibility="collapsed")
        if new_qty != item["qty"]:
            item["qty"] = new_qty
            st.rerun()
            
        c3.write(f"{line:,.0f} MMK")
        if c4.button("🗑", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

    st.write("---")
    
    # Total calculation
    c1, c2 = st.columns(2)
    discount = c1.number_input("Discount (%)", 0.0, 100.0, 0.0)
    tax = c2.number_input("Tax (%)", 0.0, 100.0, 5.0)

    total = subtotal * (1 - discount / 100) * (1 + tax / 100)

    st.markdown(f"## 🧾 TOTAL: {total:,.0f} MMK")

    # Payment
    paid = st.number_input("Paid Amount", 0.0, value=float(total))

    if st.button("💳 Pay & Print", type="primary"):
        if not st.session_state.cart:
            st.error("Cart is empty")
            st.stop()

        if paid < total:
            st.error("Insufficient payment")
            st.stop()

        # သန့်စင်ပြီးသား Cart structure ကို သယ်ဆောင်သွားမည်ဖြစ်၍ API Error ကင်းဝေးမည်
        result = checkout_sale_rpc(st.session_state.cart, paid_amount=paid)

        if isinstance(result, dict) and result.get("error"):
            st.error(result["error"])
            st.stop()

        st.success(f"Sale ID: {result.get('sale_id')}")
        st.info(f"Receipt: {result.get('receipt_no')}")

        st.session_state.cart = []
        st.session_state.selected_product = None
        st.rerun()
else:
    st.info("Cart is empty.")
