import streamlit as st
from database import get_products, checkout_sale_rpc

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="POS v10 Enterprise", layout="wide")

st.title("🛒 POS v10 Enterprise POS")

# =========================
# SESSION STATE
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "selected_product" not in st.session_state:
    st.session_state.selected_product = None

# =========================
# HELPERS
# =========================
def safe_float(v):
    try:
        return float(v or 0)
    except:
        return 0.0

# =========================
# LOAD PRODUCTS
# =========================
products = get_products() or []

# =========================
# PRODUCT OPTIONS (SELECTBOX)
# =========================
product_map = {
    f"{p['name']} | {safe_float(p.get('selling_price')):,.0f} MMK": p
    for p in products
}

# =========================
# SEARCH (SELECTBOX BASED - STABLE)
# =========================
col1, col2 = st.columns(2)

with col1:
    selected_label = st.selectbox(
        "🔍 Select Product",
        options=[""] + list(product_map.keys()),
        key="product_select"
    )

with col2:
    barcode = st.text_input("📟 Barcode / SKU Scan")

# =========================
# RESOLVE PRODUCT
# =========================
selected_product = None

if selected_label:
    selected_product = product_map.get(selected_label)

elif barcode:
    selected_product = next(
        (p for p in products if barcode in [str(p.get("barcode","")), str(p.get("sku",""))]),
        None
    )

# =========================
# ADD TO CART
# =========================
if selected_product:

    st.divider()
    st.subheader("📦 Product")

    c1, c2, c3 = st.columns([4,1,1])

    c1.write(selected_product["name"])
    qty = c2.number_input("Qty", 1, 999, 1, key="qty_input")

    if c3.button("➕ Add to Cart", type="primary"):

        cart_item = {
            "id": selected_product["id"],
            "name": selected_product["name"],
            "selling_price": safe_float(selected_product.get("selling_price")),
            "tax_rate": safe_float(selected_product.get("tax_rate", 0)),
            "discount_allowed": bool(selected_product.get("discount_allowed", False)),
            "qty": qty
        }

        # update if exists
        found = False
        for item in st.session_state.cart:
            if item["id"] == cart_item["id"]:
                item["qty"] += qty
                found = True
                break

        if not found:
            st.session_state.cart.append(cart_item)

        st.success("Added to cart")
        st.rerun()

# =========================
# CART SECTION
# =========================
st.divider()
st.subheader("🧾 Cart")

cart = st.session_state.cart

if not cart:
    st.info("Cart is empty")

else:

    subtotal = 0
    total_tax = 0

    for i, item in enumerate(cart):

        c1, c2, c3, c4 = st.columns([4,2,2,1])

        price = safe_float(item["selling_price"])
        qty = item["qty"]
        tax_rate = safe_float(item.get("tax_rate", 0))

        line = price * qty
        tax = line * (tax_rate / 100)

        c1.write(item["name"])

        new_qty = c2.number_input(
            "Qty",
            1, 999,
            qty,
            key=f"qty_{i}"
        )

        item["qty"] = new_qty

        c3.write(f"{(line + tax):,.0f} MMK")

        if c4.button("🗑", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

        subtotal += line
        total_tax += tax

    st.markdown("---")
    st.markdown(f"### Total: {(subtotal + total_tax):,.0f} MMK")

    # =========================
    # PAY & PRINT (FIXED)
    # =========================
    if st.button("💳 Pay & Print", type="primary"):

        if len(st.session_state.cart) == 0:
            st.warning("Cart is empty")
            st.stop()

        prepared = []

        for item in st.session_state.cart:
            prepared.append({
                "id": int(item["id"]),
                "qty": int(item["qty"]),
                "selling_price": float(item["selling_price"]),
                "tax_rate": float(item.get("tax_rate", 0)),
                "discount_allowed": bool(item.get("discount_allowed", False))
            })

        with st.spinner("Processing sale..."):
            result = checkout_sale_rpc(
                prepared,
                float(subtotal + total_tax),
                None
            )

        # =========================
        # SUCCESS HANDLING FIXED
        # =========================
        if result and isinstance(result, dict) and result.get("success"):

            st.success("Payment successful")

            # IMPORTANT: clear ONLY after success
            st.session_state.cart = []

            # optional reset
            st.session_state.selected_product = None

            st.rerun()

        elif result and isinstance(result, dict) and "error" in result:
            st.error(result["error"])

        else:
            st.error("Transaction failed")
