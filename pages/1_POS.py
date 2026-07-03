import streamlit as st

st.title("🛒 POS v3 FIXED ENGINE")

# =========================
# INIT CART (SAFE COPY)
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

# =========================
# PRODUCTS
# =========================
products = [
    {"id": 1, "name": "Cake", "price": 5000},
    {"id": 2, "name": "Coffee", "price": 2500},
    {"id": 3, "name": "Tea", "price": 1500},
]

# =========================
# ADD TO CART (IMMUTABLE STYLE)
# =========================
def add_to_cart(p):
    cart = st.session_state.cart

    for item in cart:
        if item["id"] == p["id"]:
            item["qty"] += 1
            st.session_state.cart = cart
            return

    cart.append({
        "id": p["id"],
        "name": p["name"],
        "price": float(p["price"]),
        "qty": 1
    })

    st.session_state.cart = cart

# =========================
# PRODUCTS UI
# =========================
st.subheader("📦 Products")

for p in products:
    col1, col2 = st.columns([3,1])

    with col1:
        st.write(f"{p['name']} - {p['price']} MMK")

    with col2:
        if st.button("➕", key=f"add_{p['id']}"):
            add_to_cart(p)
            st.rerun()

st.divider()

# =========================
# CART SAFE CALCULATION
# =========================
st.subheader("🧾 Cart")

subtotal = 0

cart_snapshot = st.session_state.cart.copy()

for i, item in enumerate(cart_snapshot):

    col1, col2, col3 = st.columns([4,2,1])

    with col1:
        st.write(item["name"])

    with col2:
        new_qty = st.number_input(
            "Qty",
            min_value=1,
            value=int(item["qty"]),
            key=f"qty_{item['id']}"
        )

    with col3:
        if st.button("❌", key=f"del_{item['id']}"):
            st.session_state.cart = [
                x for x in st.session_state.cart if x["id"] != item["id"]
            ]
            st.rerun()

    # 🔥 IMPORTANT: update AFTER loop safe 방식
    item["qty"] = new_qty

    subtotal += float(item["price"]) * int(new_qty)

# commit updated cart
st.session_state.cart = cart_snapshot

# =========================
# DISCOUNT + TAX
# =========================
discount = st.number_input("Discount (%)", 0.0)

discount_amt = subtotal * (discount / 100)
after_discount = subtotal - discount_amt

tax = after_discount * 0.05
total = after_discount + tax

st.write("Subtotal:", subtotal)
st.write("Discount:", discount_amt)
st.write("Tax:", tax)

st.write("## TOTAL:", total)

# =========================
# CHECKOUT FIXED
# =========================
paid = st.number_input("Paid Amount", 0.0)

if st.button("💳 Pay & Print"):

    # 🔥 DEBUG PRINT (important)
    st.write("DEBUG CART:", st.session_state.cart)
    st.write("DEBUG TOTAL:", total)

    if len(st.session_state.cart) == 0:
        st.error("Cart Empty")

    elif total <= 0:
        st.error("Total = 0 (calculation bug)")

    elif paid < total:
        st.error("Insufficient payment")

    else:
        st.success(f"Paid OK 🚀 Change: {paid - total}")

        st.session_state.cart = []
        st.rerun()
