import streamlit as st

st.title("🛒 POS v3 Ultra (FIXED ENGINE)")

# =========================
# INIT CART
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

# =========================
# ADD TEST PRODUCTS (if needed)
# =========================
products = [
    {"id": 1, "name": "Cake", "price": 5000},
    {"id": 2, "name": "Coffee", "price": 2500},
    {"id": 3, "name": "Tea", "price": 1500},
]

# =========================
# ADD TO CART
# =========================
def add(p):
    for i in st.session_state.cart:
        if i["id"] == p["id"]:
            i["qty"] += 1
            return

    st.session_state.cart.append({
        "id": p["id"],
        "name": p["name"],
        "price": float(p["price"]),
        "qty": 1
    })

# =========================
# PRODUCTS UI
# =========================
st.subheader("📦 Products")

for p in products:
    col1, col2 = st.columns([3,1])

    with col1:
        st.write(f"🛒 {p['name']} - {p['price']} MMK")

    with col2:
        if st.button("Add", key=f"add_{p['id']}"):
            add(p)
            st.rerun()

st.divider()

# =========================
# CART CALCULATION (FIXED)
# =========================
st.subheader("🧾 Cart")

subtotal = 0

for i, item in enumerate(st.session_state.cart):

    col1, col2, col3 = st.columns([4,2,1])

    with col1:
        st.write(item["name"])

    with col2:
        qty = st.number_input("Qty", min_value=1, value=item["qty"], key=f"q_{i}")
        item["qty"] = qty

    with col3:
        if st.button("❌", key=f"rm_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

    subtotal += float(item["price"]) * int(item["qty"])

# =========================
# DISCOUNT + TAX
# =========================
discount_pct = st.number_input("Discount (%)", min_value=0.0, value=0.0)

discount = subtotal * (discount_pct / 100)
after_discount = subtotal - discount

tax = after_discount * 0.05
total = after_discount + tax

# =========================
# SUMMARY (DEBUG SAFE)
# =========================
st.write("Subtotal:", subtotal)
st.write("Discount:", discount)
st.write("After Discount:", after_discount)
st.write("Tax:", tax)

st.write("## 🧾 TOTAL:", total)

# =========================
# CHECKOUT FIX
# =========================
paid = st.number_input("Paid Amount", min_value=0.0)

if st.button("💳 Pay & Print"):

    if len(st.session_state.cart) == 0:
        st.error("Cart empty ❌")

    elif total <= 0:
        st.error("Total is 0 → calculation bug")

    elif paid < total:
        st.error("Insufficient payment ❌")

    else:
        change = paid - total

        st.success("Payment Success 🚀")
        st.info(f"Change: {change}")

        st.session_state.cart = []
        st.rerun()
