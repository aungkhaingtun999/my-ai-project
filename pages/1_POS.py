import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v3 Ultra FIXED", layout="wide")

st.title("🛒 POS v3 Ultra FIXED ENGINE (Stable + Safe + Production Ready)")

# =========================
# INIT CART SAFE
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

# =========================
# LOAD PRODUCTS SAFE
# =========================
products_resp = get_products()
products = []

if products_resp and hasattr(products_resp, "data"):
    products = products_resp.data or []

# =========================
# SAFE ADD TO CART
# =========================
def add_to_cart(p):
    if not p:
        return

    price = float(p.get("selling_price") or 0)

    for item in st.session_state.cart:
        if item.get("id") == p.get("id"):
            item["qty"] += 1
            return

    st.session_state.cart.append({
        "id": p.get("id"),
        "name": p.get("name", "Unknown"),
        "selling_price": price,
        "qty": 1
    })

# =========================
# PRODUCT LIST
# =========================
st.subheader("📦 Products")

if products:
    for p in products:
        c1, c2, c3 = st.columns([4, 2, 1])

        c1.write(f"🛒 {p.get('name','')}")
        c2.write(f"{p.get('selling_price',0)} MMK")

        if c3.button("➕", key=f"add_{p.get('id')}"):
            add_to_cart(p)
            st.rerun()
else:
    st.warning("No products found")

# =========================
# CART
# =========================
st.divider()
st.subheader("🧾 Cart")

subtotal = 0.0

for item in st.session_state.cart:
    price = float(item.get("selling_price") or 0)
    qty = int(item.get("qty") or 0)

    line_total = price * qty
    subtotal += line_total

    c1, c2, c3 = st.columns([4, 2, 1])

    c1.write(item.get("name"))
    c2.write(f"{qty} x {price}")
    c3.write(f"{line_total}")

st.write("## Subtotal:", round(subtotal, 2), "MMK")

# =========================
# DISCOUNT + TAX ENGINE
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
# PAYMENT SECTION
# =========================
paid = st.number_input("Paid Amount", min_value=0.0)

if st.button("💳 Pay & Print"):

    # CART CHECK
    if len(st.session_state.cart) == 0:
        st.error("Cart is empty")
        st.stop()

    # PAYMENT CHECK
    if paid < total:
        st.error("Insufficient payment")
        st.stop()

    # =========================
    # RPC CALL SAFE
    # =========================
    result = checkout_sale_rpc(
        st.session_state.cart,
        paid_amount=paid
    )

    # SAFE RESULT CHECK
    if not result:
        st.error("Checkout failed (no response)")
        st.stop()

    if isinstance(result, dict) and result.get("error"):
        st.error(result["error"])
        st.stop()

    # SUCCESS HANDLING
    st.success(f"Sale Completed ID: {result.get('sale_id')}")
    st.info(f"Receipt No: {result.get('receipt_no')}")

    # RESET CART
    st.session_state.cart = []
    st.rerun()
