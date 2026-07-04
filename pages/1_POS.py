import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v7 Shopify UX", layout="wide")

st.title("🛒 POS v7 Shopify Infinite Smart Search")


# ======================================================
# SAFE FLOAT
# ======================================================
def safe_float(v):
    try:
        return float(v) if v is not None else 0.0
    except:
        return 0.0


# ======================================================
# SESSION INIT
# ======================================================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "selected" not in st.session_state:
    st.session_state.selected = None

if "limit" not in st.session_state:
    st.session_state.limit = 10   # pagination size


# ======================================================
# LOAD PRODUCTS
# ======================================================
products = get_products() or []


# ======================================================
# SEARCH INPUT (LIVE TYPEAHEAD)
# ======================================================
search = st.text_input("🔍 Search product (name / barcode / SKU)").strip().lower()


# ======================================================
# NORMALIZE + SCORE ENGINE
# ======================================================
def norm(v):
    return str(v or "").lower().replace(" ", "")


def score(p, q):
    if not q:
        return 0

    q = norm(q)
    name = norm(p.get("name"))
    barcode = norm(p.get("barcode"))
    sku = norm(p.get("sku"))

    s = 0

    if q in name:
        s += 100
    if q in barcode or q in sku:
        s += 90
    if name.startswith(q):
        s += 120

    return s


# ======================================================
# FILTER PRODUCTS
# ======================================================
filtered = []

if search:
    for p in products:
        sc = score(p, search)
        if sc > 0:
            p["_score"] = sc
            filtered.append(p)

    filtered.sort(key=lambda x: x["_score"], reverse=True)

# LIMIT (infinite simulation)
visible = filtered[:st.session_state.limit]


# ======================================================
# FLOAT DROPDOWN UI (CUSTOM PANEL)
# ======================================================
if search:

    st.markdown("### 🔍 Search Results")

    if not visible:
        st.info("No products found")

    for p in visible:

        col1, col2 = st.columns([6, 2])

        with col1:
            if st.button(
                f"{p['name']} | {p.get('barcode')} | {p.get('sku')}",
                key=f"sel_{p['id']}"
            ):
                st.session_state.selected = p

        with col2:
            st.write(f"{safe_float(p.get('selling_price')):,.0f} MMK")

    # ==================================================
    # LOAD MORE (INFINITE SCROLL SIMULATION)
    # ==================================================
    if len(filtered) > st.session_state.limit:
        if st.button("⬇ Load more"):
            st.session_state.limit += 10
            st.rerun()


# ======================================================
# SELECTED PRODUCT DETAIL (ONLY ONE)
# ======================================================
if st.session_state.selected:

    p = st.session_state.selected

    st.divider()
    st.subheader("🛒 Product Detail")

    st.write(p["name"])
    st.caption(f"{p.get('barcode')} | {p.get('sku')} | {p.get('unit','pcs')}")

    stock = safe_float(p.get("stock"))

    qty = st.number_input("Qty", 1, 100, 1)

    if st.button("➕ Add to Cart"):

        if stock <= 0:
            st.error("Out of stock")
        else:
            for item in st.session_state.cart:
                if item["id"] == p["id"]:
                    item["qty"] += qty
                    break
            else:
                st.session_state.cart.append({
                    "id": p["id"],
                    "name": p["name"],
                    "barcode": p["barcode"],
                    "sku": p["sku"],
                    "unit": p.get("unit", "pcs"),
                    "selling_price": safe_float(p.get("selling_price")),
                    "qty": qty
                })

            st.session_state.selected = None
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

st.write("### Subtotal:", f"{subtotal:,.0f} MMK")


# ======================================================
# TOTAL
# ======================================================
c1, c2 = st.columns(2)

discount = c1.number_input("Discount (%)", 0.0, 100.0, 0.0)
tax = c2.number_input("Tax (%)", 0.0, 100.0, 5.0)

total = subtotal * (1 - discount/100) * (1 + tax/100)

st.markdown(f"## 🧾 TOTAL: {total:,.0f} MMK")


# ======================================================
# PAYMENT
# ======================================================
paid = st.number_input("Paid Amount", 0.0)

if st.button("💳 Pay & Print"):

    if not st.session_state.cart:
        st.error("Cart empty")
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
    st.session_state.selected = None
    st.rerun()
