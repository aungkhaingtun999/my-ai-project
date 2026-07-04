import streamlit as st
from database import get_products

st.set_page_config(page_title="POS v10 Enterprise", layout="wide")

# =========================
# SESSION STATE
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "selected" not in st.session_state:
    st.session_state.selected = None

products = get_products() or []

st.title("🛒 POS v10 Enterprise")


# =========================
# HELPERS
# =========================
def norm(v):
    return str(v or "").lower().strip()


def search(keyword):
    keyword = norm(keyword)
    if not keyword:
        return []

    results = []

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
            score += 250

        if score:
            results.append((score, p))

    results.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in results]


def money(x):
    return f"{float(x or 0):,.0f}"


# =========================
# SEARCH INPUT
# =========================
search_text = st.text_input(
    "🔍 Search Product (Name / Barcode / SKU)",
    key="search_input"
)

dropdown = st.empty()

matches = search(search_text)


# =========================
# FLOATING DROPDOWN (FIXED UX)
# =========================
if search_text and matches:

    with dropdown.container():

        st.markdown("""
        <style>
        .dropbox {
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
            max-height: 260px;
            overflow-y: auto;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="dropbox">', unsafe_allow_html=True)

        for i, p in enumerate(matches[:15]):

            label = f"{p['name']} | {p.get('barcode','')} | {money(p.get('selling_price'))} MMK"

            if st.button(label, key=f"prod_{i}"):

                st.session_state.selected = p
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# =========================
# SELECTED PRODUCT
# =========================
selected = st.session_state.selected

if selected:

    st.divider()
    st.subheader("📦 Product Detail")

    price = float(selected.get("selling_price", 0))
    tax_rate = float(selected.get("tax_rate", 0))
    discount_rate = float(selected.get("discount", 0))  # % discount (optional)

    c1, c2, c3, c4 = st.columns([4, 1, 1, 1])

    c1.write(selected["name"])
    c2.metric("Price", money(price))
    c3.metric("Tax %", f"{tax_rate}%")

    qty = c4.number_input("Qty", 1, 999, 1)

    # Discount input
    discount_input = st.number_input("Discount (%)", 0.0, 100.0, float(discount_rate))


    if st.button("➕ Add to Cart", type="primary"):

        base = price * qty

        tax = base * (tax_rate / 100)
        discount = base * (discount_input / 100)

        final = base + tax - discount

        st.session_state.cart.append({
            "id": selected["id"],
            "name": selected["name"],
            "price": price,
            "qty": qty,
            "tax_rate": tax_rate,
            "discount": discount_input,
            "line_total": final
        })

        st.session_state.selected = None
        st.success("Added to cart")
        st.rerun()


# =========================
# CART SECTION
# =========================
st.divider()
st.subheader("🧾 Cart")

total = 0
total_tax = 0
total_discount = 0

for i, item in enumerate(st.session_state.cart):

    c1, c2, c3, c4 = st.columns([4, 1, 1, 1])

    base = item["price"] * item["qty"]
    tax = base * (item.get("tax_rate", 0) / 100)
    discount = base * (item.get("discount", 0) / 100)
    final = base + tax - discount

    c1.write(item["name"])
    c2.write(f"{item['qty']} × {money(item['price'])}")

    c3.write(f"Tax: {money(tax)}")
    c4.write(f"{money(final)}")

    total += final
    total_tax += tax
    total_discount += discount


st.markdown("---")
st.markdown(f"### 🧾 Total: {money(total)} MMK")
st.markdown(f"### 🧾 Tax: {money(total_tax)} MMK")
st.markdown(f"### 🧾 Discount: {money(total_discount)} MMK")


# =========================
# CHECKOUT
# =========================
if st.button("💳 Checkout", type="primary"):

    if not st.session_state.cart:
        st.warning("Cart is empty")
        st.stop()

    st.success("Sale Completed!")

    # DB call placeholder
    # checkout_sale_rpc(st.session_state.cart, total)

    st.session_state.cart = []
    st.session_state.selected = None
    st.rerun()
