import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v8 Smart ERP", layout="wide")

st.title("🛒 POS v8 Shopify-Level Smart POS")


# ======================================================
# SAFE FLOAT
# ======================================================
def safe_float(v):
    try:
        return float(v) if v is not None else 0.0
    except:
        return 0.0


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
# NORMALIZE
# ======================================================
def norm(v):
    return str(v or "").lower().replace(" ", "")


# ======================================================
# SEARCH INPUTS (IMPORTANT FIX)
# ======================================================
name_search = st.text_input("🔍 Search Product Name", "")
code_search = st.text_input("📟 Barcode / SKU (Scanner Mode)", "")


# ======================================================
# 1. NAME SEARCH (DROPDOWN STYLE)
# ======================================================
def match_name(p, q):
    return q and q in norm(p.get("name"))


name_results = []
if name_search:
    q = norm(name_search)
    for p in products:
        if match_name(p, q):
            name_results.append(p)

    name_results = name_results[:8]


# ======================================================
# 2. BARCODE / SKU SEARCH (EXACT FAST MATCH)
# ======================================================
def match_code(p, q):
    q = norm(q)
    return (
        q == norm(p.get("barcode")) or
        q == norm(p.get("sku"))
    )

code_results = []
if code_search:
    for p in products:
        if match_code(p, code_search):
            code_results.append(p)


# ======================================================
# DROPDOWN UI (NAME SEARCH ONLY)
# ======================================================
if name_search:

    st.markdown("### 🔽 Name Suggestions")

    if name_results:
        for p in name_results:
            label = f"{p['name']} | {p.get('barcode')} | {p.get('sku')}"

            if st.button(label, key=f"name_{p['id']}"):
                st.session_state.selected_product = p
                st.rerun()
    else:
        st.info("No product found")


# ======================================================
# AUTO SELECT FROM BARCODE / SKU
# ======================================================
if code_search and code_results:

    # auto-pick first match (scanner behavior)
    st.session_state.selected_product = code_results[0]
    st.success("Product scanned ✔")
    st.rerun()


# ======================================================
# SELECTED PRODUCT DETAIL
# ======================================================
p = st.session_state.selected_product

if p:

    st.divider()
    st.subheader("🛒 Product Detail")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.write(p["name"])
        st.caption(f"{p.get('barcode')} | {p.get('sku')} | {p.get('unit','pcs')}")

    with col2:
        st.write(f"💰 {safe_float(p.get('selling_price')):,.0f}")

    qty = st.number_input("Qty", 1, 100, 1)

    if st.button("➕ Add to Cart"):

        pid = p["id"]

        for item in st.session_state.cart:
            if item["id"] == pid:
                item["qty"] += qty
                break
        else:
            st.session_state.cart.append({
                "id": pid,
                "name": p["name"],
                "barcode": p["barcode"],
                "sku": p["sku"],
                "unit": p.get("unit", "pcs"),
                "selling_price": safe_float(p.get("selling_price")),
                "qty": qty
            })

        st.session_state.selected_product = None
        st.success("Added to cart")
        st.rerun()


# ======================================================
# CART
# ======================================================
st.divider()
st.subheader("🧾 Cart")

subtotal = 0

for item in st.session_state.cart:
    line = item["selling_price"] * item["qty"]
    subtotal += line

    c1, c2, c3 = st.columns([5, 2, 2])
    c1.write(item["name"])
    c2.write(f"{item['qty']} x {item['selling_price']:,.0f}")
    c3.write(f"{line:,.0f}")


st.write("## Subtotal:", f"{subtotal:,.0f} MMK")


# ======================================================
# TOTAL
# ======================================================
c1, c2 = st.columns(2)

discount = c1.number_input("Discount (%)", 0.0, 100.0, 0.0)
tax = c2.number_input("Tax (%)", 0.0, 100.0, 5.0)

total = subtotal * (1 - discount / 100) * (1 + tax / 100)

st.markdown(f"## 🧾 TOTAL: {total:,.0f} MMK")


# ======================================================
# PAYMENT
# ======================================================
paid = st.number_input("Paid Amount", 0.0)

if st.button("💳 Pay & Print"):

    if not st.session_state.cart:
        st.error("Cart is empty")
        st.stop()

    if paid < total:
        st.error("Insufficient payment")
        st.stop()

    result = checkout_sale_rpc(st.session_state.cart, paid_amount=paid)

    if isinstance(result, dict) and result.get("error"):
        st.error(result["error"])
        st.stop()

    st.success(f"Sale ID: {result.get('sale_id')}")
    st.info(f"Receipt: {result.get('receipt_no')}")

    st.session_state.cart = []
    st.session_state.selected_product = None
    st.rerun()
