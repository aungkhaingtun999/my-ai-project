import streamlit as st
from database import get_products, checkout_sale_rpc

# =========================
# CONFIG (SMALL UI)
# =========================
st.set_page_config(page_title="POS", layout="centered")

st.markdown("## 🛒 POS System")

# =========================
# SESSION
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "selected" not in st.session_state:
    st.session_state.selected = None

# =========================
# HELPERS
# =========================
def safe_float(v):
    try:
        return float(v or 0)
    except:
        return 0.0

def norm(v):
    return str(v or "").lower().strip()

# =========================
# PRODUCTS
# =========================
products = get_products() or []

# =========================
# SEARCH ENGINE
# =========================
def search_products(keyword):
    keyword = norm(keyword)
    if not keyword:
        return []

    result = []

    for p in products:
        name = norm(p.get("name"))
        barcode = norm(p.get("barcode"))
        sku = norm(p.get("sku"))

        score = 0

        if keyword == name or keyword == barcode or keyword == sku:
            score += 1000

        if name.startswith(keyword):
            score += 500

        if keyword in name:
            score += 300

        if keyword in barcode or keyword in sku:
            score += 200

        if score:
            result.append((score, p))

    result.sort(reverse=True, key=lambda x: x[0])
    return [p for _, p in result]


# =========================
# FLOAT SEARCH (SMALL DROPDOWN)
# =========================
search = st.text_input("🔍 Search Product", placeholder="Type name...")

matches = search_products(search)

selected = None

if search and matches:

    with st.container():

        st.markdown("""
        <style>
        .box {
            border:1px solid #ddd;
            border-radius:8px;
            padding:6px;
            max-height:180px;
            overflow-y:auto;
            background:white;
        }
        .item {
            padding:6px;
            font-size:13px;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="box">', unsafe_allow_html=True)

        for i, p in enumerate(matches[:8]):

            label = f"{p['name']} | {safe_float(p.get('selling_price')):,.0f} MMK"

            if st.button(label, key=f"p_{i}"):

                st.session_state.selected = p
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# restore selected
selected = st.session_state.selected


# =========================
# PRODUCT CARD (SMALL FIXED UI)
# =========================
if selected:

    st.markdown("---")

    st.markdown(f"### {selected['name']}")

    c1, c2 = st.columns([2, 1])

    price = safe_float(selected.get("selling_price"))
    tax = safe_float(selected.get("tax_rate", 0))
    discount = bool(selected.get("discount_allowed", False))

    c1.write(f"💰 {price:,.0f} MMK")
    c1.caption(f"Tax: {tax}% | Discount: {'YES' if discount else 'NO'}")

    qty = c2.number_input("Qty", 1, 99, 1, key="qty")

    if st.button("➕ Add to Cart"):

        item = {
            "id": selected["id"],
            "name": selected["name"],
            "selling_price": price,
            "qty": qty,
            "tax_rate": tax,
            "discount_allowed": discount
        }

        found = False
        for c in st.session_state.cart:
            if c["id"] == item["id"]:
                c["qty"] += qty
                found = True

        if not found:
            st.session_state.cart.append(item)

        st.session_state.selected = None
        st.rerun()


# =========================
# CART (CLEAN SMALL UI)
# =========================
st.markdown("## 🧾 Cart")

if len(st.session_state.cart) == 0:
    st.info("Cart is empty")

else:

    subtotal = 0
    total_tax = 0

    for i, item in enumerate(st.session_state.cart):

        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])

        price = safe_float(item.get("selling_price"))
        qty = int(item.get("qty", 1))
        tax = safe_float(item.get("tax_rate", 0))

        line = price * qty
        tax_amt = line * tax / 100
        total = line + tax_amt

        c1.write(f"{item['name']}")

        new_qty = c2.number_input("", 1, 99, qty, key=f"q_{i}")
        item["qty"] = new_qty

        c3.write(f"{total:,.0f}")

        if c4.button("🗑", key=f"d_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

        subtotal += line
        total_tax += tax_amt

    st.markdown("---")
    st.markdown(f"### TOTAL: {(subtotal + total_tax):,.0f} MMK")


# =========================
# CHECKOUT SAFE
# =========================
if st.button("💳 Pay & Print"):

    if not st.session_state.cart:
        st.warning("Cart is empty")
        st.stop()

    prepared = [
        {
            "id": i["id"],
            "qty": i["qty"],
            "selling_price": i["selling_price"],
            "tax_rate": i.get("tax_rate", 0),
            "discount_allowed": i.get("discount_allowed", False)
        }
        for i in st.session_state.cart
    ]

    total = sum(
        (i["selling_price"] * i["qty"]) * (1 + i.get("tax_rate", 0)/100)
        for i in st.session_state.cart
    )

    result = checkout_sale_rpc(prepared, float(total), None)

    if result and result.get("success"):
        st.success("Done ✔")

        st.session_state.cart = []
        st.session_state.selected = None
        st.rerun()

    else:
        st.error("Checkout failed")
