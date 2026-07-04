import streamlit as st
from database import get_products
from utils.helpers import safe_float

st.set_page_config(page_title="POS v10 Float Search", layout="wide")

products = get_products() or []

# =========================================================
# SESSION STATE
# =========================================================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "search_index" not in st.session_state:
    st.session_state.search_index = 0

if "dropdown_open" not in st.session_state:
    st.session_state.dropdown_open = False

if "selected_product" not in st.session_state:
    st.session_state.selected_product = None


# =========================================================
# NORMALIZE + SEARCH ENGINE
# =========================================================
def norm(x):
    return str(x or "").lower().strip()


def search(keyword):
    if not keyword:
        return []

    keyword = norm(keyword)
    results = []

    for p in products:

        name = norm(p.get("name"))
        barcode = norm(p.get("barcode"))
        sku = norm(p.get("sku"))

        score = 0

        if keyword == name or keyword == barcode or keyword == sku:
            score += 1000

        if keyword in name:
            score += 500

        if keyword in barcode or keyword in sku:
            score += 400

        if name.startswith(keyword):
            score += 600

        if score:
            results.append((score, p))

    results.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in results[:8]]   # FLOAT LIMIT


# =========================================================
# UI HEADER
# =========================================================
st.title("🛒 POS v10 Floating Search Engine")


# =========================================================
# SEARCH BOX
# =========================================================
search_input = st.text_input(
    "🔍 Search Product (type for floating dropdown)",
    key="search_box"
)

results = search(search_input)

# open dropdown automatically
st.session_state.dropdown_open = bool(search_input and results)


# =========================================================
# FLOATING DROPDOWN CONTAINER
# =========================================================
dropdown = st.empty()


if st.session_state.dropdown_open:

    with dropdown.container():

        st.markdown(
            """
            <style>
            .float-box {
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 10px;
                background: white;
                box-shadow: 0px 5px 20px rgba(0,0,0,0.15);
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### 🔎 Results")

        for i, p in enumerate(results):

            highlight = "🟡" if i == st.session_state.search_index else "⚪"

            if st.button(
                f"{highlight} {p['name']}  |  {safe_float(p['selling_price']):,.0f} MMK",
                key=f"p_{p['id']}"
            ):
                st.session_state.selected_product = p
                st.session_state.dropdown_open = False
                st.session_state.search_index = 0
                st.rerun()


# =========================================================
# KEYBOARD NAVIGATION (SIMULATED)
# =========================================================
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬆️ Up"):
        st.session_state.search_index = max(0, st.session_state.search_index - 1)
        st.rerun()

with col2:
    if st.button("⬇️ Down"):
        st.session_state.search_index = min(len(results)-1, st.session_state.search_index + 1)
        st.rerun()

with col3:
    if st.button("⏎ Select"):
        if results:
            st.session_state.selected_product = results[st.session_state.search_index]
            st.session_state.dropdown_open = False
            st.session_state.search_index = 0
            st.rerun()


# =========================================================
# PRODUCT DETAIL (ONLY AFTER SELECT)
# =========================================================
if st.session_state.selected_product:

    p = st.session_state.selected_product

    st.divider()
    st.subheader("🛒 Selected Product")

    c1, c2, c3 = st.columns(3)

    c1.write(p["name"])
    c2.metric("Price", f"{safe_float(p['selling_price']):,.0f}")
    c3.metric("Stock", safe_float(p.get("stock", 0)))

    qty = st.number_input("Qty", 1, 999, 1)

    if st.button("➕ Add to Cart", type="primary"):

        st.session_state.cart.append({
            "id": p["id"],
            "name": p["name"],
            "selling_price": safe_float(p["selling_price"]),
            "qty": qty
        })

        st.session_state.selected_product = None
        st.rerun()


# =========================================================
# CART (MINIMAL VIEW)
# =========================================================
st.divider()
st.subheader("🧾 Cart")

total = 0

for i, item in enumerate(st.session_state.cart):

    line = item["selling_price"] * item["qty"]
    total += line

    c1, c2, c3 = st.columns([5, 2, 1])

    c1.write(item["name"])
    c2.write(f"{item['qty']} x {item['selling_price']:,.0f}")
    c3.write(f"{line:,.0f}")

st.markdown(f"## Total: {total:,.0f} MMK")
