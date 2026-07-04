import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v5 Smart ERP", layout="wide")

st.title("🛒 POS v5 Smart Search ERP Engine")

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
# ADD TO CART
# ======================================================
def add_to_cart(p):
    if not p:
        return

    price = safe_float(p.get("selling_price"))

    for item in st.session_state.cart:
        if item["id"] == p["id"]:
            item["qty"] = safe_float(item["qty"]) + 1
            return

    st.session_state.cart.append({
        "id": p["id"],
        "name": p.get("name"),
        "barcode": p.get("barcode"),
        "sku": p.get("sku"),
        "unit": p.get("unit", "pcs"),
        "selling_price": price,
        "qty": 1
    })


# ======================================================
# 🔍 SEARCH BOX (MAIN FEATURE)
# ======================================================
search = st.text_input("🔍 Search by Name / Barcode / SKU")

def match(p, q):
    q = q.lower()

    return (
        q in str(p.get("name", "")).lower()
        or q in str(p.get("barcode", "")).lower()
        or q in str(p.get("sku", "")).lower()
    )

filtered_products = [
    p for p in products
    if not search or match(p, search)
]


# ======================================================
# PRODUCTS GRID (MODERN CARD UI)
# ======================================================
st.subheader("📦 Products")

if not filtered_products:
    st.warning("No matching products found")
else:
    for p in filtered_products:

        stock = safe_float(p.get("stock"))
        min_stock = safe_float(p.get("minimum_stock"))

        with st.container(border=True):

            col1, col2, col3 = st.columns([5, 2, 1])

            with col1:
                st.write(f"🛒 **{p.get('name')}**")
                st.caption(
                    f"Barcode: {p.get('barcode')} | "
                    f"SKU: {p.get('sku')} | "
                    f"Unit: {p.get('unit', 'pcs')}"
                )

                if stock <= min_stock:
                    st.error(f"⚠ Low Stock: {stock}")

            col2.write(f"💰 {safe_float(p.get('selling_price')):,.0f} MMK")

            if col3.button("➕", key=f"add_{p['id']}"):
                if stock <= 0:
                    st.error("Out of stock")
                else:
                    add_to_cart(p)
                    st.rerun()


# ======================================================
# CART
# ======================================================
st.divider()
st.subheader("🧾 Cart")

subtotal = 0.0

for item in st.session_state.cart:
    price = safe_float(item["selling_price"])
    qty = safe_float(item["qty"])

    line = price * qty
    subtotal += line

    c1, c2, c3 = st.columns([5, 2, 2])
    c1.write(f"{item['name']} ({item.get('unit','pcs')})")
    c2.write(f"{qty} x {price:,.0f}")
    c3.write(f"{line:,.0f}")


st.write("## Subtotal:", f"{subtotal:,.0f} MMK")


# ======================================================
# DISCOUNT / TAX
# ======================================================
c1, c2 = st.columns(2)

discount = c1.number_input("Discount (%)", 0.0, 100.0, 0.0)
tax = c2.number_input("Tax (%)", 0.0, 100.0, 5.0)

after_discount = subtotal - (subtotal * discount / 100)
total = after_discount + (after_discount * tax / 100)

st.markdown(f"## 🧾 TOTAL: {total:,.0f} MMK")


# ======================================================
# PAYMENT
# ======================================================
paid = st.number_input("Paid Amount", 0.0)

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

    if isinstance(result, dict) and result.get("error"):
        st.error(result["error"])
        st.stop()

    st.success(f"Sale ID: {result.get('sale_id')}")
    st.info(f"Receipt: {result.get('receipt_no')}")

    st.session_state.cart = []
    st.rerun()
