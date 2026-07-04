import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v5 Shopify-Level ERP", layout="wide")

st.title("🛒 POS v5 Shopify-Level Smart ERP Engine")


# ======================================================
# SAFE FLOAT ENGINE
# ======================================================
def safe_float(v):
    try:
        return float(v) if v is not None else 0.0
    except:
        return 0.0


# ======================================================
# SESSION CART
# ======================================================
if "cart" not in st.session_state:
    st.session_state.cart = []


# ======================================================
# LOAD PRODUCTS (FAST PATH)
# ======================================================
products = get_products() or []


# ======================================================
# SEARCH BAR (SHOPIFY STYLE)
# ======================================================
search = st.text_input(
    "🔍 Search product (name / barcode / SKU)",
    placeholder="Type to search instantly..."
).strip().lower()


# ======================================================
# SMART SCORING ENGINE (IMPROVED)
# ======================================================
def norm(v):
    return str(v or "").lower().replace(" ", "")


def score(p, q):
    if not q:
        return 0   # ❗ IMPORTANT: nothing shows without search

    q = norm(q)

    name = norm(p.get("name"))
    barcode = norm(p.get("barcode"))
    sku = norm(p.get("sku"))

    s = 0

    # exact
    if q == name or q == barcode or q == sku:
        s += 200

    # strong prefix
    if name.startswith(q):
        s += 120
    if barcode.startswith(q) or sku.startswith(q):
        s += 110

    # contains
    if q in name:
        s += 90
    if q in barcode or q in sku:
        s += 80

    # fuzzy fallback (safe)
    if any(ch in name for ch in q):
        s += 20

    return s


# ======================================================
# FILTER ENGINE (SHOPIFY STYLE)
# ======================================================
filtered = []

if search:
    for p in products:
        sc = score(p, search)
        if sc > 0:
            p["_score"] = sc
            filtered.append(p)

    filtered.sort(key=lambda x: x["_score"], reverse=True)

else:
    filtered = []   # ❗ clean UX (no search → no products)


# ======================================================
# ADD TO CART
# ======================================================
def add_to_cart(p):
    pid = p["id"]
    price = safe_float(p.get("selling_price"))

    for item in st.session_state.cart:
        if item["id"] == pid:
            item["qty"] += 1
            return

    st.session_state.cart.append({
        "id": pid,
        "name": p.get("name"),
        "barcode": p.get("barcode"),
        "sku": p.get("sku"),
        "unit": p.get("unit", "pcs"),
        "selling_price": price,
        "qty": 1
    })


# ======================================================
# PRODUCT GRID (SHOPIFY CARD UX)
# ======================================================
st.subheader("📦 Products")

if search and not filtered:
    st.warning("No matching products found")

for p in filtered:

    stock = safe_float(p.get("stock"))
    min_stock = safe_float(p.get("minimum_stock"))
    pid = p["id"]

    with st.container(border=True):

        col1, col2, col3 = st.columns([6, 2, 1])

        with col1:
            st.markdown(f"""
### 🛒 {p.get('name')}

**Barcode:** `{p.get('barcode')}`  
**SKU:** `{p.get('sku')}`  
**Unit:** `{p.get('unit','pcs')}`
            """)

            if stock <= min_stock:
                st.warning("⚠ Low stock alert")

        col2.markdown(f"## 💰 {safe_float(p.get('selling_price')):,.0f} MMK")

        if col3.button("➕", key=f"add_{pid}"):
            if stock <= 0:
                st.error("Out of stock")
            else:
                add_to_cart(p)
                st.rerun()


# ======================================================
# CART (SHOPIFY STYLE SUMMARY)
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
# TOTAL ENGINE
# ======================================================
c1, c2 = st.columns(2)

discount = c1.number_input("Discount (%)", 0.0, 100.0, 0.0)
tax = c2.number_input("Tax (%)", 0.0, 100.0, 5.0)

after_discount = subtotal * (1 - discount / 100)
total = after_discount * (1 + tax / 100)

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

    result = checkout_sale_rpc(
        st.session_state.cart,
        paid_amount=paid
    )

    if isinstance(result, dict) and result.get("error"):
        st.error(result["error"])
        st.stop()

    st.success(f"Sale ID: {result.get('sale_id')}")
    st.info(f"Receipt: {result.get('receipt_no')}")

    st.session_state.cart = []
    st.rerun()
