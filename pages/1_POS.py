import streamlit as st
from database import get_products

st.title("🛒 POS v3 Ultra (Enterprise Grade)")

# =========================
# INIT CART
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

# =========================
# SETTINGS (ERP CONFIG)
# =========================
TAX_RATE = 0.05   # 5% Commercial Tax (change anytime)

# =========================
# LOAD PRODUCTS
# =========================
products_resp = get_products()
products = products_resp.data if products_resp and products_resp.data else []

# =========================
# SEARCH / BARCODE
# =========================
search = st.text_input("🔎 Scan / Enter Barcode or Search")

filtered = [
    p for p in products
    if search.lower() in (p.get("name", "") + str(p.get("barcode", ""))).lower()
] if search else products

# =========================
# ADD TO CART (FLOATING PRICE SUPPORT)
# =========================
def add_to_cart(p):
    for item in st.session_state.cart:
        if item["id"] == p["id"]:
            item["qty"] += 1
            return

    st.session_state.cart.append({
        "id": p["id"],
        "name": p["name"],
        "qty": 1,

        # 🔥 FLOATING PRICE SUPPORT
        "price": float(p.get("selling_price") or 0),

        # optional override
        "custom_price": None
    })

# =========================
# PRODUCT LIST
# =========================
st.subheader("📦 Products")

for p in filtered:
    col1, col2, col3 = st.columns([5, 2, 1])

    with col1:
        st.write(f"🛒 {p['name']}")

    with col2:
        st.write(f"{p.get('selling_price',0)} MMK")

    with col3:
        if st.button("➕", key=f"add_{p['id']}"):
            add_to_cart(p)
            st.rerun()

st.divider()

# =========================
# CART
# =========================
st.subheader("🧾 Cart")

subtotal = 0

for i, item in enumerate(st.session_state.cart):

    col1, col2, col3, col4 = st.columns([4, 2, 2, 1])

    with col1:
        st.write(item["name"])

    # =========================
    # FLOATING PRICE EDIT
    # =========================
    with col2:
        price = st.number_input(
            "Price",
            value=item["price"],
            key=f"price_{i}"
        )
        item["price"] = price

    with col3:
        qty = st.number_input(
            "Qty",
            value=item["qty"],
            min_value=1,
            key=f"qty_{i}"
        )
        item["qty"] = qty

    with col4:
        if st.button("❌", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

    subtotal += item["price"] * item["qty"]

# =========================
# DISCOUNT (GLOBAL)
# =========================
st.divider()

discount_pct = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, value=0.0)

discount_amount = subtotal * (discount_pct / 100)

after_discount = subtotal - discount_amount

# =========================
# TAX (COMMERCIAL TAX)
# =========================
tax = after_discount * TAX_RATE

# =========================
# FINAL TOTAL
# =========================
total = after_discount + tax

# =========================
# SUMMARY
# =========================
st.write("## 💰 Summary")

st.write("Subtotal:", subtotal)
st.write("Discount:", discount_amount)
st.write("After Discount:", after_discount)
st.write("Tax (5%):", tax)

st.write("## 🧾 TOTAL:", total)

# =========================
# CHECKOUT PLACEHOLDER
# =========================
paid = st.number_input("Paid Amount", min_value=0.0)

if st.button("Pay & Print"):

    if not st.session_state.cart:
        st.error("Cart empty")

    elif paid < total:
        st.error("Insufficient payment")

    else:
        change = paid - total

        st.success("Payment Successful 🚀")
        st.info(f"Change: {change}")

        st.session_state.cart = []
        st.rerun()