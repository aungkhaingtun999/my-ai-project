import streamlit as st
from database import get_products, checkout_sale_rpc

# =========================
# PAGE CONFIG
# =========================
st.title("🛒 POS v3 Ultra (Enterprise Grade)")

# =========================
# SESSION INIT
# =========================
def init():
    if "cart" not in st.session_state:
        st.session_state.cart = []

    if "discount" not in st.session_state:
        st.session_state.discount = 0

init()

# =========================
# LOAD PRODUCTS
# =========================
resp = get_products()
products = resp.data or [] if resp else []

# =========================
# FAST SEARCH / BARCODE INPUT
# =========================
barcode = st.text_input("🔎 Scan / Enter Barcode or Search")

def find_product(query):
    query = query.lower()

    for p in products:
        if str(p.get("barcode","")) == query:
            return p
        if p.get("name") and query in p["name"].lower():
            return p
    return None

# =========================
# ADD TO CART (SMART ENGINE)
# =========================
def add(product):
    if not product:
        return

    for item in st.session_state.cart:
        if item["id"] == product["id"]:
            item["qty"] += 1
            return

    st.session_state.cart.append({
        "id": product["id"],
        "name": product.get("name"),
        "price": float(product.get("selling_price") or 0),
        "qty": 1
    })

# Auto add from barcode/search
if barcode:
    p = find_product(barcode)
    if p:
        add(p)
        st.success(f"Added: {p['name']}")
        st.rerun()

# =========================
# CART ENGINE
# =========================
st.subheader("🧾 Cart")

subtotal = 0

for item in st.session_state.cart:

    c1, c2, c3, c4 = st.columns([4,1,1,1])

    with c1:
        st.write(item["name"])

    with c2:
        st.write(item["price"])

    with c3:
        qty = st.number_input(
            "Qty",
            min_value=1,
            value=item["qty"],
            key=f"qty_{item['id']}"
        )
        item["qty"] = qty

    with c4:
        if st.button("❌", key=f"rm_{item['id']}"):
            st.session_state.cart.remove(item)
            st.rerun()

    subtotal += item["price"] * item["qty"]

# =========================
# DISCOUNT ENGINE
# =========================
st.divider()
st.subheader("💰 Pricing")

col1, col2 = st.columns(2)

with col1:
    st.session_state.discount = st.number_input(
        "Discount (%)",
        min_value=0,
        max_value=100,
        value=st.session_state.discount
    )

discount_amount = (subtotal * st.session_state.discount) / 100
total = subtotal - discount_amount

col2.metric("Subtotal", f"{subtotal:,.0f}")
col2.metric("Discount", f"{discount_amount:,.0f}")
col2.metric("Total", f"{total:,.0f}")

# =========================
# CHECKOUT SECTION
# =========================
st.divider()
st.subheader("💳 Checkout")

paid = st.number_input("Paid Amount", min_value=0.0, step=100.0)

col1, col2, col3 = st.columns(3)

checkout = col1.button("🚀 Pay (F2)")
clear = col2.button("🧹 Clear Cart")
hold = col3.button("⏸ Hold Sale")

# =========================
# CLEAR CART
# =========================
if clear:
    st.session_state.cart = []
    st.success("Cart Cleared")
    st.rerun()

# =========================
# HOLD SALE (future feature)
# =========================
if hold:
    st.info("Sale saved to HOLD (feature placeholder)")

# =========================
# CHECKOUT ENGINE (ULTRA SAFE)
# =========================
if checkout:

    if not st.session_state.cart:
        st.warning("Cart is empty")
        st.stop()

    if paid < total:
        st.error("Insufficient payment")
        st.stop()

    with st.spinner("Processing Ultra Checkout..."):

        result = checkout_sale_rpc(
            st.session_state.cart,
            paid_amount=paid
        )

    if not result or result.get("error"):
        st.error(result.get("error", "Checkout failed"))
        st.stop()

    st.success(f"Sale Completed: {result['sale_id']}")
    st.info(f"Receipt: {result['receipt_no']}")

    # reset
    st.session_state.cart = []
    st.session_state.discount = 0

    st.rerun()

# =========================
# SHORTCUT HELP
# =========================
st.caption("Tip: Use barcode scanner or F2 to speed checkout 🚀")