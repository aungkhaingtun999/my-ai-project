import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v4 ERP Ultra", layout="wide")

st.title("🛒 POS v4 Ultra ERP ENGINE (Production Ready)")

# ======================================================
# SAFE FLOAT
# ======================================================
def safe_float(v):
    try:
        return float(v)
    except:
        return 0.0


# ======================================================
# CART INIT
# ======================================================
if "cart" not in st.session_state:
    st.session_state.cart = []


# ======================================================
# LOAD PRODUCTS
# ======================================================
products_resp = get_products()
products = products_resp.data if products_resp and hasattr(products_resp, "data") else []


# ======================================================
# ADD TO CART (ERP SAFE)
# ======================================================
def add_to_cart(p):
    if not p:
        return

    price = safe_float(p.get("selling_price"))

    for item in st.session_state.cart:
        if item.get("id") == p.get("id"):
            item["qty"] = safe_float(item.get("qty")) + 1
            return

    st.session_state.cart.append({
        "id": p.get("id"),
        "name": p.get("name", "Unknown"),
        "barcode": p.get("barcode"),
        "sku": p.get("sku"),
        "unit": p.get("unit", "pcs"),
        "selling_price": price,
        "qty": 1
    })


# ======================================================
# PRODUCT LIST (WITH ERP INFO)
# ======================================================
st.subheader("📦 Products")

if products:
    for p in products:

        stock = safe_float(p.get("stock"))
        min_stock = safe_float(p.get("minimum_stock"))

        col1, col2, col3 = st.columns([5, 2, 1])

        # PRODUCT INFO BLOCK
        with col1:
            st.write(f"🛒 **{p.get('name','')}**")

            st.caption(
                f"Barcode: {p.get('barcode','-')} | "
                f"SKU: {p.get('sku','-')} | "
                f"Unit: {p.get('unit','pcs')}"
            )

            # LOW STOCK WARNING
            if stock <= min_stock:
                st.error(f"⚠ Low Stock: {stock} left")

        # PRICE
        col2.write(f"{safe_float(p.get('selling_price')):,.2f} MMK")

        # ADD BUTTON
        if col3.button("➕", key=f"add_{p.get('id')}"):
            if stock <= 0:
                st.error("Out of stock")
            else:
                add_to_cart(p)
                st.rerun()

else:
    st.warning("No products found")


# ======================================================
# CART
# ======================================================
st.divider()
st.subheader("🧾 Cart")

subtotal = 0.0

for item in st.session_state.cart:

    price = safe_float(item.get("selling_price"))
    qty = safe_float(item.get("qty"))
    unit = item.get("unit", "pcs")

    line_total = price * qty
    subtotal += line_total

    c1, c2, c3 = st.columns([5, 2, 2])

    c1.write(f"{item.get('name')} ({unit})")
    c2.write(f"{qty} x {price:,.2f}")
    c3.write(f"{line_total:,.2f}")


st.write("## Subtotal:", f"{subtotal:,.2f} MMK")


# ======================================================
# DISCOUNT + TAX
# ======================================================
col1, col2 = st.columns(2)

discount_rate = col1.number_input("Discount (%)", 0.0, 100.0, 0.0)
tax_rate = col2.number_input("Tax (%)", 0.0, 100.0, 5.0)

discount_amount = subtotal * discount_rate / 100
after_discount = subtotal - discount_amount
tax_amount = after_discount * tax_rate / 100

total = after_discount + tax_amount


# ======================================================
# SUMMARY
# ======================================================
st.markdown("## 💰 Summary")

st.write("Subtotal:", f"{subtotal:,.2f}")
st.write("Discount:", f"{discount_amount:,.2f}")
st.write("After Discount:", f"{after_discount:,.2f}")
st.write("Tax:", f"{tax_amount:,.2f}")

st.markdown(f"## 🧾 TOTAL: {total:,.2f} MMK")


# ======================================================
# PAYMENT
# ======================================================
paid = st.number_input("Paid Amount", min_value=0.0, value=0.0)

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

    if not result:
        st.error("Checkout failed")
        st.stop()

    if isinstance(result, dict) and result.get("error"):
        st.error(result["error"])
        st.stop()

    st.success(f"Sale Completed ID: {result.get('sale_id')}")
    st.info(f"Receipt No: {result.get('receipt_no')}")

    # RESET
    st.session_state.cart = []
    st.rerun()
