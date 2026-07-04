import streamlit as st
from database import get_products

# =========================
# PAGE CONFIG (MUST BE FIRST)
# =========================
st.set_page_config(page_title="POS v10 Enterprise", layout="wide")

# =========================
# SESSION INIT
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

# =========================
# HELPERS
# =========================
def safe_float(v):
    try:
        return float(v or 0)
    except:
        return 0.0


# =========================
# LOAD DATA
# =========================
products = get_products() or []

st.title("🛒 POS v10 Enterprise")
st.divider()
st.subheader("🧾 Cart")

cart = st.session_state.get("cart", [])

if not cart:
    st.info("Cart is empty")
else:

    total_tax = 0
    subtotal = 0
    grand_total = 0

    for i, item in enumerate(cart):

        try:
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])

            name = item.get("name", "Unknown")
            price = float(item.get("selling_price", 0))
            qty = int(item.get("qty", 1))

            tax_rate = float(item.get("tax_rate", 0))
            discount_allowed = bool(item.get("discount_allowed", False))

            line_base = price * qty
            tax_amount = line_base * (tax_rate / 100)

            discount = 0
            line_total = line_base + tax_amount - discount

            c1.write(name)

            new_qty = c2.number_input(
                "Qty",
                min_value=1,
                max_value=999,
                value=qty,
                key=f"qty_{i}"
            )

            item["qty"] = new_qty

            c3.write(f"{tax_rate}% Tax")
            c4.write(f"{line_total:,.0f}")

            if st.button("🗑", key=f"del_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()

            subtotal += line_base
            total_tax += tax_amount
            grand_total += line_total

        except Exception as e:
            st.error(f"Cart item error: {e}")

    st.markdown("---")
    st.write(f"Subtotal: {subtotal:,.0f}")
    st.write(f"Tax: {total_tax:,.0f}")
    st.write(f"Grand Total: {grand_total:,.0f}")
else:
    st.info("Cart is empty")
