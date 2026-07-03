import streamlit as st
from database import get_products, checkout_sale_rpc

st.title("🛒 POS System (Smart Search Upgrade)")

# =====================
# INIT CART
# =====================
if "cart" not in st.session_state:
    st.session_state.cart = []

# =====================
# LOAD PRODUCTS
# =====================
products_resp = get_products()
products = products_resp.data if products_resp and products_resp.data else []

# =====================
# SEARCH BOX (FLOATING FILTER)
# =====================
search = st.text_input("🔍 Search Products")

filtered_products = []

if search:
    filtered_products = [
        p for p in products
        if search.lower() in p["name"].lower()
    ]
else:
    filtered_products = products

# =====================
# ADD TO CART
# =====================
def add_to_cart(product):
    for item in st.session_state.cart:
        if item["id"] == product["id"]:
            item["qty"] += 1
            return

    st.session_state.cart.append({
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
# FLOATING PRODUCT LIST UI
# =====================
st.subheader("Products")

for p in filtered_products:

    with st.container():
        col1, col2, col3 = st.columns([4, 2, 1])

        with col1:
            st.write(f"🛒 {p['name']}")

        with col2:
            st.write(f"{p.get('selling_price',0)} MMK")

        with col3:
            if st.button("➕", key=f"add_{p['id']}"):
                add_to_cart(p)
                st.rerun()

        st.markdown("---")

# =====================
# CART
# =====================
st.divider()
st.subheader("🧾 Cart")

subtotal = 0

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

    subtotal += item["selling_price"] * item["qty"]

st.write("## Total:", subtotal, "MMK")

# =====================
# CHECKOUT
# =====================
st.divider()
st.subheader("💳 Checkout")

paid = st.number_input("Paid Amount", min_value=0)

if st.button("Pay & Generate Receipt"):

    if not st.session_state.cart:
        st.warning("Cart is empty")

    elif paid < subtotal:
        st.error("Insufficient payment")

    else:
        result = checkout_sale_rpc(
            st.session_state.cart,
            paid_amount=paid
        )

        if not result or "error" in result:
            st.error(result.get("error", "Checkout failed"))

        else:
            st.success(f"Sale Completed! ID: {result['sale_id']}")

            st.info(f"Receipt: {result['receipt_no']}")

            st.session_state.cart = []
            st.rerun()