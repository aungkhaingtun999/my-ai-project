import streamlit as st
from database import get_products

st.set_page_config(page_title="POS v10 Enterprise", layout="wide")

# =========================
# SESSION
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


# =========================
# SEARCH INPUT
# =========================
search_text = st.text_input("🔍 Search Product (Name / Barcode / SKU)")

# =========================
# FLOATING DROPDOWN CONTAINER
# =========================
dropdown = st.empty()

matches = search(search_text)

# =========================
# FLOAT UI (NO PAGE SHIFT)
# =========================
selected = None

if search_text and matches:

    with dropdown.container():

        st.markdown("""
        <style>
        .dropbox {
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
            max-height: 250px;
            overflow-y: auto;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        .item {
            padding: 10px;
            cursor: pointer;
        }
        .item:hover {
            background: #f0f6ff;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="dropbox">', unsafe_allow_html=True)

        for i, p in enumerate(matches[:10]):

            label = f"{p['name']} | {p.get('barcode','')} | {p.get('sku','')}"

            if st.button(label, key=f"p_{i}"):

                st.session_state.selected = p
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# =========================
# SELECTED PRODUCT ONLY
# =========================
selected = st.session_state.selected

if selected:

    st.divider()
    st.subheader("📦 Selected Product")

    c1, c2, c3 = st.columns([4,1,1])

    c1.write(selected["name"])
    c2.write(f"{selected.get('selling_price',0):,.0f} MMK")

    qty = c3.number_input("Qty", 1, 999, 1)

    if st.button("➕ Add to Cart"):

        st.session_state.cart.append({
            "id": selected["id"],
            "name": selected["name"],
            "price": selected.get("selling_price", 0),
            "qty": qty
        })

        st.session_state.selected = None
        st.success("Added to cart")
        st.rerun()


# =========================
# CART
# =========================
st.divider()
st.subheader("🧾 Cart")

total = 0

for i, item in enumerate(st.session_state.cart):

    c1, c2, c3 = st.columns([4,1,1])

    c1.write(item["name"])
    c2.write(f"{item['qty']} x {item['price']}")
    c3.write(f"{item['qty'] * item['price']:.0f}")

    total += item["qty"] * item["price"]

st.markdown(f"### TOTAL: {total:,.0f} MMK")
