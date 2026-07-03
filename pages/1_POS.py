import streamlit as st
from database import get_products, checkout_sale_rpc

st.title("🛒 POS System (Production Ready)")

# =====================
# INIT CART
# =====================
if "cart" not in st.session_state:
    st.session_state.cart = []

# =====================
# LOAD PRODUCTS (SAFE)
# =====================
products_resp = get_products()
products = products_resp.data if products_resp and products_resp.data else []

# =====================
# ADD TO CART
# =====================
def add_to_cart(product):
    cart = st.session_state.cart

    for item in cart:
        if item["id"] == product["id"]:
            item["qty"] += 1
            return

    cart.append({
        "id": product["id"],
        "name": product["name"],
        "selling_price": product.get("selling_price", 0),
        "qty": 1
    })

# =====================
# REMOVE ITEM
# =====================
def remove_item(product_id):
    st.session_state.cart = [
        item for item in st.session_state.cart
        if item["id"] != product_id
    ]

# =====================
# PRODUCTS UI
# =====================
st.subheader("Products")

for p in products:
    col1, col2 = st.columns([3, 1])

    with col1:
        st.write(f"{p.get('name')} - {p.get('selling_price',0)} MMK (Stock: {p.get('stock',0)})")

    with col2:
        if st.button("Add", key=f"add_{p['id']}"):
            add_to_cart(p)
            st.rerun()

# =====================
# CART
# =====================
st.divider()
st.subheader("🧾 Cart")

total = 0

if not st.session_state.cart:
    st.info("Cart is empty")

for item in st.session_state.cart:

    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

    with col1:
        st.write(item["name"])

    with col2:
        st.write(item["selling_price"])

    with col3:
        st.write(f"Qty: {item['qty']}")

    with col4:
        if st.button("❌", key=f"del_{item['id']}"):
            remove_item(item["id"])
            st.rerun()

    total += item["selling_price"] * item["qty"]

st.write("## Total:", total, "MMK")

# =====================
# CHECKOUT
# =====================
st.divider()
st.subheader("💳 Checkout")

paid = st.number_input("Paid Amount", min_value=0)

if st.button("Pay & Generate Receipt"):

    if not st.session_state.cart:
        st.warning("Cart is empty")

    elif paid < total:
        st.error("Insufficient payment")

    else:
        result = checkout_sale_rpc(
            st.session_state.cart,
            paid_amount=paid
        )

        if not result:
            st.error("Checkout failed")

        else:
            st.success(f"Sale Completed! ID: {result['sale_id']}")

            # CLEAR CART
            st.session_state.cart = []
            st.rerun()