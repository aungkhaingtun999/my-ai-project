import streamlit as st
from database import checkout_sale_rpc
from utils.helpers import safe_float

# =========================================================
# CART INIT
# =========================================================
if "cart" not in st.session_state:
    st.session_state.cart = []


# =========================================================
# ADD TO CART FUNCTION
# =========================================================
def add_to_cart(product, qty):

    for item in st.session_state.cart:

        if item["id"] == product["id"]:
            item["qty"] += qty
            return

    st.session_state.cart.append({
        "id": product["id"],
        "name": product["name"],
        "selling_price": safe_float(product.get("selling_price")),
        "tax_rate": safe_float(product.get("tax_rate", 0)),
        "discount_allowed": bool(product.get("discount_allowed", False)),
        "qty": qty
    })


# =========================================================
# CART UI (SHOPIFY STYLE CLEAN TABLE)
# =========================================================
st.divider()
st.subheader("🧾 Cart")

subtotal = 0
total_tax = 0

if st.session_state.cart:

    for i, item in enumerate(st.session_state.cart):

        line_total = item["selling_price"] * item["qty"]
        tax = line_total * (item.get("tax_rate", 0) / 100)

        subtotal += line_total
        total_tax += tax

        c1, c2, c3, c4, c5 = st.columns([4, 1, 1, 1, 1])

        with c1:
            st.write(item["name"])

        with c2:
            item["qty"] = st.number_input(
                "Qty",
                min_value=1,
                value=item["qty"],
                key=f"qty_{i}"
            )

        with c3:
            st.write(f"{safe_float(item.get('tax_rate'))}%")

        with c4:
            st.write("✓" if item.get("discount_allowed") else "—")

        with c5:
            st.write(f"{line_total + tax:,.0f}")

            if st.button("🗑", key=f"del_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()

    # =========================================================
    # TOTAL SECTION
    # =========================================================
    st.markdown("---")

    grand_total = subtotal + total_tax

    col1, col2, col3 = st.columns(3)

    col1.metric("Subtotal", f"{subtotal:,.0f}")
    col2.metric("Tax", f"{total_tax:,.0f}")
    col3.metric("Grand Total", f"{grand_total:,.0f}")


    # =========================================================
    # CHECKOUT
    # =========================================================
    st.markdown("## 💳 Checkout")

    paid = st.number_input("Paid Amount", min_value=0.0, value=grand_total)

    if st.button("💰 Pay & Complete Sale", type="primary"):

        if paid < grand_total:
            st.error("Insufficient payment")
            st.stop()

        payload = [
            {
                "id": i["id"],
                "qty": i["qty"],
                "selling_price": i["selling_price"],
                "tax_rate": i.get("tax_rate", 0),
                "discount_allowed": i.get("discount_allowed", False)
            }
            for i in st.session_state.cart
        ]

        with st.spinner("Processing sale..."):
            result = checkout_sale_rpc(payload, paid_amount=paid)

        if result and result.get("success"):

            st.success(f"Sale Completed ✔ ID: {result.get('sale_id')}")

            st.session_state.cart = []
            st.rerun()

        else:
            st.error(result.get("error", "Transaction failed"))

else:
    st.info("Cart is empty")
