import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v3 Ultra", layout="wide")

st.title("🛒 POS v3 Ultra FIXED ENGINE (Tax + Discount + Stable Checkout)")

# =========================
# INIT CART
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

# =========================
# LOAD PRODUCTS
# =========================
products_resp = get_products()
products = products_resp.data if products_resp and products_resp.data else []

# =========================
# SAFE ADD TO CART
# =========================
def add_to_cart(p):
    if not p:
        return

    for item in st.session_state.cart:
        if item["id"] == p["id"]:
            item["qty"] += 1
            return

    st.session_state.cart.append({
        "id": p["id"],
        "name": p["name"],
        "selling_price": float(p.get("selling_price") or 0),
        "qty": 1
    })

# =========================
# PRODUCT LIST
# =========================
st.subheader("📦 Products")

colA, colB = st.columns([3, 2])

with colA:
    for p in products:
        c1, c2, c3 = st.columns([4, 2, 1])

        c1.write(f"🛒 {p['name']}")
        c2.write(f"{p.get('selling_price',0)} MMK")

        if c3.button("➕", key=f"add_{p['id']}"):
            add_to_cart(p)
            st.rerun()

# =========================
# CART
# =========================
st.divider()
st.subheader("🧾 Cart")

subtotal = 0

for item in st.session_state.cart:
    line_total = item["selling_price"] * item["qty"]
    subtotal += line_total

    c1, c2, c3 = st.columns([4, 2, 1])

    c1.write(item["name"])
    c2.write(f"{item['qty']} x {item['selling_price']}")
    c3.write(f"{line_total}")

st.write("## Subtotal:", round(subtotal, 2), "MMK")

# =========================
# DISCOUNT + TAX ENGINE (FIXED)
# =========================
col1, col2 = st.columns(2)

discount_rate = col1.number_input("Discount (%)", 0.0, 100.0, 0.0)
tax_rate = col2.number_input("Tax (%)", 0.0, 100.0, 5.0)

discount_amount = subtotal * (discount_rate / 100)
after_discount = subtotal - discount_amount

tax_amount = after_discount * (tax_rate / 100)

total = after_discount + tax_amount

# =========================
# SUMMARY
# =========================
st.markdown("## 💰 Summary")

st.write("Subtotal:", round(subtotal, 2))
st.write("Discount:", round(discount_amount, 2))
st.write("After Discount:", round(after_discount, 2))
st.write("Tax:", round(tax_amount, 2))

st.markdown(f"## 🧾 TOTAL: {round(total, 2)} MMK")

# =========================
# PAYMENT
# =========================
paid = st.number_input("Paid Amount", min_value=0.0)

if st.button("💳 Pay & Print"):

    if len(st.session_state.cart) == 0:
        st.error("Cart is empty")
        st.stop()

    if paid < total:
        st.error("Insufficient payment")
        st.stop()

    # =========================
    # SAFE RPC CALL
    # =========================
    result = checkout_sale_rpc(
        st.session_state.cart,
        paid_amount=paid
    )

    # =========================
    # SAFE RESULT HANDLING
    # =========================
    if not result or not result.get("success"):
        st.error(result.get("error", "Checkout failed"))
        st.stop()

    st.success(f"Sale Completed ID: {result['sale_id']}")
    st.info(f"Receipt No: {result['receipt_no']}")

    # reset cart
    st.session_state.cart = []
    st.rerun()
