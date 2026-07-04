import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(
    page_title="POS v10 Enterprise",
    layout="wide"
)

st.title("🛒 POS v10 Enterprise POS")


# =========================================================
# SESSION
# =========================================================

if "cart" not in st.session_state:
    st.session_state.cart = []

if "selected_product" not in st.session_state:
    st.session_state.selected_product = None


# =========================================================
# HELPERS
# =========================================================

def safe_float(v):
    try:
        return float(v or 0)
    except:
        return 0.0


def normalize(v):
    return str(v or "").lower().strip()


# =========================================================
# LOAD PRODUCTS
# =========================================================

products = get_products() or []


# =========================================================
# SMART SEARCH ENGINE
# =========================================================

def score_product(product, keyword):

    keyword = normalize(keyword)

    if keyword == "":
        return 0

    name = normalize(product.get("name"))
    barcode = normalize(product.get("barcode"))
    sku = normalize(product.get("sku"))

    score = 0

    # Exact
    if keyword == name:
        score += 1000

    if keyword == barcode:
        score += 950

    if keyword == sku:
        score += 900

    # Prefix
    if name.startswith(keyword):
        score += 500

    if barcode.startswith(keyword):
        score += 450

    if sku.startswith(keyword):
        score += 400

    # Contains
    if keyword in name:
        score += 300

    if keyword in barcode:
        score += 250

    if keyword in sku:
        score += 200

    return score


def search_products(keyword):

    result = []

    for p in products:

        s = score_product(p, keyword)

        if s > 0:
            result.append((s, p))

    result.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    return [x[1] for x in result]


# =========================================================
# SEARCH AREA
# =========================================================

left, right = st.columns([3,1])

with left:

    search_name = st.text_input(
        "🔍 Product Name",
        placeholder="Type product name..."
    )

with right:

    barcode = st.text_input(
        "📟 Barcode / SKU",
        placeholder="Scan..."
    )


# =========================================================
# BARCODE SEARCH
# =========================================================

selected = None

if barcode.strip():

    code = normalize(barcode)

    for p in products:

        if normalize(p.get("barcode")) == code:

            selected = p
            break

        if normalize(p.get("sku")) == code:

            selected = p
            break


# =========================================================
# NAME SEARCH
# =========================================================

if selected is None and search_name:

    matches = search_products(search_name)

    if matches:

        labels = []

        for p in matches[:20]:

            labels.append(
                f"{p['name']}   |   {safe_float(p['selling_price']):,.0f} MMK"
            )

        choice = st.selectbox(
            "Search Result",
            labels,
            index=None,
            placeholder="Choose product..."
        )

        if choice:

            index = labels.index(choice)

            selected = matches[index]


# =========================================================
# PRODUCT DETAIL
# =========================================================

if selected:

    st.divider()

    st.subheader("Selected Product")

    c1,c2,c3,c4 = st.columns([4,1,1,1])

    with c1:

        st.write(f"### {selected['name']}")

        st.caption(
            f"Barcode : {selected.get('barcode')}"
        )

        st.caption(
            f"SKU : {selected.get('sku')}"
        )

        st.caption(
            f"Unit : {selected.get('unit')}"
        )

    with c2:

        st.metric(
            "Price",
            f"{safe_float(selected.get('selling_price')):,.0f}"
        )

    with c3:

        stock = safe_float(
            selected.get("stock")
        )

        st.metric(
            "Stock",
            f"{stock:,.0f}"
        )

    with c4:

        qty = st.number_input(
            "Qty",
            1,
            999,
            1
        )

        if st.button(
            "➕ Add",
            use_container_width=True,
            type="primary"
        ):

            found = False

            for item in st.session_state.cart:

                if item["id"] == selected["id"]:

                    item["qty"] += qty

                    found = True

                    break

            if not found:

                st.session_state.cart.append({

                    "id": selected["id"],

                    "name": selected["name"],

                    "selling_price": safe_float(
                        selected.get("selling_price")
                    ),

                    "tax_rate": safe_float(
                        selected.get("tax_rate",0)
                    ),

                    "discount_allowed": bool(
                        selected.get("discount_allowed",False)
                    ),

                    "qty": qty

                })

            st.success("Added to Cart")

            st.rerun()
