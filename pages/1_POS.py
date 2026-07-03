import streamlit as st
from database import get_products, checkout_sale_rpc

st.title("🛒 POS v3 Ultra FIXED (Tax + Discount Engine)")

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
# ADD TO CART
# =====================
def add_to_cart(p):
    for item in st.session_state.cart:
        if item["id"] == p["id"]:
            item["qty"] += 1
            return

    st.session_state.cart.append({
        "id": p["id"],
        "name": p["name"],
        "selling_price": float(p.get("selling_price", 0)),
        "qty": 1
    })

# =====================
# PRODUCT LIST
# =====================
st.subheader("📦 Products")

for p in products:
    col1, col2, col3 = st.columns([4, 2, 1])

    col1.write(p["name"])
    col2.write(f"{p.get('selling_price',0)} MMK")

    if col3.button("➕", key=f"add_{p['id']}"):
        add_to_cart(p)
        st.rerun()

st.divider()

# =====================
# CART
# =====================
st.subheader("🧾 Cart")

subtotal = 0

for item in st.session_state.cart:
    subtotal += item["selling_price"] * item["qty"]
    st.write(f"{item['name']} x {item['qty']} = {item['selling_price'] * item['qty']} MMK")

st.write("### Subtotal:", subtotal)

# =====================
# DISCOUNT + TAX CONTROLS
# =====================
col1, col2 = st.columns(2)

discount_rate = col1.number_input("Discount (%)", 0.0, 100.0, 0.0)
tax_rate = col2.number_input("Tax (%)", 0.0, 100.0, 5.0)

# =====================
# CALC ENGINE (IMPORTANT FIX)
# =====================
discount_amount = subtotal * (discount_rate / 100)
after_discount = subtotal - discount_amount

tax_amount = after_discount * (tax_rate / 100)

total = after_discount + tax_amount

# =====================
# SUMMARY
# =====================
st.markdown("## 💰 Summary")

st.write("Subtotal:", subtotal)
st.write("Discount:", discount_amount)
st.write("After Discount:", after_discount)
st.write("Tax:", tax_amount)
st.write("TOTAL:", total)

# =====================
# CHECKOUT
# =====================
paid = st.number_input("Paid Amount", min_value=0.0)

if st.button("💳 Pay & Print"):

    if not st.session_state.cart:
        st.error("Cart is empty")

    elif paid < total:
        st.error("Insufficient payment")

    else:
        result = checkout_sale_rpc(
            st.session_state.cart,
            paid_amount=paid
        )

        if not result or "error" in result:
            st.error(result.get("error", "Checkout failed"))
        else:
            st.success(f"Sale Complete ID: {result['sale_id']}")
            st.info(f"Receipt: {result['receipt_no']}")

            st.session_state.cart = []
            st.rerun()
