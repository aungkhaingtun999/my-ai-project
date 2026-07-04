import streamlit as st
from database import get_products, checkout_sale_rpc

# =========================
# PAGE CONFIG (SMALL UI)
# =========================
st.set_page_config(
    page_title="POS v10 Enterprise",
    layout="centered"   # 🔥 FIX UI SIZE (NOT WIDE)
)

st.title("🛒 POS v10 Enterprise")

# =========================
# SESSION STATE
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "last_receipt" not in st.session_state:
    st.session_state.last_receipt = None

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

product_map = {
    f"{p['name']} | {safe_float(p.get('selling_price')):,.0f} MMK": p
    for p in products
}

# =========================
# SEARCH UI (COMPACT)
# =========================
st.markdown("### 🔍 Search")

col1, col2 = st.columns([3, 2])

with col1:
    selected_label = st.selectbox(
        "Product",
        [""] + list(product_map.keys()),
        key="select_product"
    )

with col2:
    barcode = st.text_input("Barcode", label_visibility="collapsed")

selected = None

if selected_label:
    selected = product_map[selected_label]

elif barcode:
    selected = next(
        (p for p in products if barcode in [str(p.get("barcode","")), str(p.get("sku",""))]),
        None
    )

# =========================
# ADD TO CART (NO OVERWRITE FIX)
# =========================
if selected:

    st.markdown("---")

    c1, c2, c3 = st.columns([4,1,1])

    c1.markdown(f"**{selected['name']}**")

    qty = c2.number_input("Qty", 1, 999, 1, key="qty")

    if c3.button("➕ Add", use_container_width=True):

        item = {
            "id": selected["id"],
            "name": selected["name"],
            "price": safe_float(selected.get("selling_price")),
            "tax_rate": safe_float(selected.get("tax_rate", 0)),
            "qty": qty
        }

        # 🔥 FIX: ALWAYS APPEND (NO OVERWRITE)
        st.session_state.cart.append(item)

        st.success("Added")
        st.rerun()

# =========================
# CART (COMPACT UI FIX)
# =========================
st.markdown("---")
st.subheader("🧾 Cart")

cart = st.session_state.cart

if not cart:
    st.info("Cart is empty")

else:

    subtotal = 0
    tax_total = 0

    for i, item in enumerate(cart):

        c1, c2, c3, c4 = st.columns([4,1,1,1])

        price = item["price"]
        qty = item["qty"]
        tax_rate = item.get("tax_rate", 0)

        line = price * qty
        tax = line * (tax_rate / 100)

        c1.write(item["name"])

        new_qty = c2.number_input(
            "Qty",
            1, 999,
            qty,
            key=f"q_{i}"
        )

        item["qty"] = new_qty

        c3.write(f"{(line + tax):,.0f}")

        if c4.button("🗑", key=f"d_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

        subtotal += line
        tax_total += tax

    total = subtotal + tax_total

    st.markdown("### 💰 TOTAL")
    st.write(f"Subtotal: {subtotal:,.0f}")
    st.write(f"Tax: {tax_total:,.0f}")
    st.markdown(f"## Grand Total: {total:,.0f}")

    # =========================
    # PAY & RECEIPT FIX
    # =========================
    if st.button("💳 Pay & Print"):

        prepared = []

        for item in cart:
            prepared.append({
                "id": item["id"],
                "qty": item["qty"],
                "price": item["price"],
                "tax_rate": item["tax_rate"]
            })

        result = checkout_sale_rpc(prepared, total, None)

        # =========================
        # RECEIPT FIX
        # =========================
        if result and isinstance(result, dict) and result.get("success"):

            receipt = {
                "items": cart.copy(),
                "total": total,
                "tax": tax_total
            }

            st.session_state.last_receipt = receipt
            st.session_state.cart = []

            st.success("Payment Success")

            # 🔥 SHOW RECEIPT
            st.markdown("## 🧾 RECEIPT")
            for it in receipt["items"]:
                st.write(f"{it['name']} x {it['qty']} = {it['price'] * it['qty']:,.0f}")

            st.markdown(f"### TOTAL: {total:,.0f}")

            st.rerun()

        else:
            st.error("Payment Failed")
