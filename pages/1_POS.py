import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v7 Smart UX FIX", layout="wide")

st.title("🛒 POS Smart ERP (Dropdown UX FIXED)")


# ======================================================
# SAFE FLOAT
# ======================================================
def safe_float(v):
    try:
        return float(v) if v is not None else 0.0
    except:
        return 0.0


# ======================================================
# SESSION
# ======================================================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "selected" not in st.session_state:
    st.session_state.selected = None


# ======================================================
# LOAD PRODUCTS
# ======================================================
products = get_products() or []


# ======================================================
# SEARCH
# ======================================================
search = st.text_input("🔍 Search product (name / barcode / SKU)").strip().lower()


def norm(v):
    return str(v or "").lower().replace(" ", "")


def score(p, q):
    if not q:
        return 0

    q = norm(q)
    name = norm(p.get("name"))
    barcode = norm(p.get("barcode"))
    sku = norm(p.get("sku"))

    s = 0

    if q in name:
        s += 100
    if q in barcode or q in sku:
        s += 90
    if name.startswith(q):
        s += 120

    return s


# ======================================================
# FILTER
# ======================================================
results = []

if search:
    for p in products:
        sc = score(p, search)
        if sc > 0:
            p["_score"] = sc
            results.append(p)

    results.sort(key=lambda x: x["_score"], reverse=True)
    results = results[:6]   # dropdown limit


# ======================================================
# FLOAT DROPDOWN (REAL FIX)
# ======================================================
dropdown = st.empty()

selected = None

with dropdown.container():

    if search and results:

        st.markdown("### 🔎 Results")

        # RADIO = dropdown replacement (clean UX)
        choice = st.radio(
            "Select product",
            options=[
                f"{p['name']} | {p.get('barcode')} | {p.get('sku')}"
                for p in results
            ],
            label_visibility="collapsed"
        )

        selected = results[
            [
                f"{p['name']} | {p.get('barcode')} | {p.get('sku')}"
                for p in results
            ].index(choice)
        ]

    elif search:
        st.info("No matching product")


# ======================================================
# CLEAR DROP WHEN SELECTED
# ======================================================
if selected:
    dropdown.empty()  # 🔥 hides dropdown → real UX feel


    st.divider()
    st.subheader("🛒 Selected Product")

    stock = safe_float(selected.get("stock"))

    st.write(selected["name"])
    st.caption(f"{selected.get('barcode')} | {selected.get('sku')}")

    qty = st.number_input("Qty", 1, 100, 1)

    if st.button("➕ Add to Cart"):

        if stock <= 0:
            st.error("Out of stock")
        else:
            for item in st.session_state.cart:
                if item["id"] == selected["id"]:
                    item["qty"] += qty
                    break
            else:
                st.session_state.cart.append({
                    "id": selected["id"],
                    "name": selected["name"],
                    "barcode": selected["barcode"],
                    "sku": selected["sku"],
                    "unit": selected.get("unit", "pcs"),
                    "selling_price": safe_float(selected.get("selling_price")),
                    "qty": qty
                })

            st.session_state.selected = None
            st.rerun()


# ======================================================
# CART
# ======================================================
st.divider()
st.subheader("🧾 Cart")

subtotal = 0

for item in st.session_state.cart:
    line = item["selling_price"] * item["qty"]
    subtotal += line

    c1, c2, c3 = st.columns([5, 2, 2])
    c1.write(item["name"])
    c2.write(f"{item['qty']} x {item['selling_price']:,.0f}")
    c3.write(f"{line:,.0f}")

st.write("### Subtotal:", f"{subtotal:,.0f} MMK")


# ======================================================
# TOTAL
# ======================================================
c1, c2 = st.columns(2)

discount = c1.number_input("Discount (%)", 0.0, 100.0, 0.0)
tax = c2.number_input("Tax (%)", 0.0, 100.0, 5.0)

total = subtotal * (1 - discount/100) * (1 + tax/100)

st.markdown(f"## 🧾 TOTAL: {total:,.0f} MMK")


# ======================================================
# PAYMENT
# ======================================================
paid = st.number_input("Paid Amount", 0.0)

if st.button("💳 Pay & Print"):

    if not st.session_state.cart:
        st.error("Cart empty")
        st.stop()

    if paid < total:
        st.error("Insufficient payment")
        st.stop()

    result = checkout_sale_rpc(st.session_state.cart, paid_amount=paid)

    if isinstance(result, dict) and result.get("error"):
        st.error(result["error"])
        st.stop()

    st.success(f"Sale ID: {result.get('sale_id')}")
    st.info(f"Receipt: {result.get('receipt_no')}")

    st.session_state.cart = []
    st.rerun()
