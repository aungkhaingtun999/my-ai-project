import streamlit as st
from database import get_products, checkout_sale_rpc

# =========================
# PAGE CONFIG (MUST FIRST)
# =========================
st.set_page_config(page_title="POS v10 Enterprise", layout="wide")

st.title("🛒 POS v10 Enterprise")

# =========================
# SESSION STATE
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
# LOAD PRODUCTS
# =========================
products = get_products() or []

# =========================
# SEARCH ENGINE
# =========================
def search_products(keyword):
    keyword = norm(keyword)
    if not keyword:
        return []

    results = []

    for p in products:
        name = norm(p.get("name"))
        barcode = norm(p.get("barcode"))
        sku = norm(p.get("sku"))

        score = 0

        if keyword == name:
            score += 1000
        if keyword == barcode:
            score += 950
        if keyword == sku:
            score += 900

        if name.startswith(keyword):
            score += 500
        if barcode.startswith(keyword):
            score += 450
        if sku.startswith(keyword):
            score += 400

        if keyword in name:
            score += 300
        if keyword in barcode:
            score += 250
        if keyword in sku:
            score += 200

        if score:
            results.append((score, p))

    results.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in results]


# =========================
# SEARCH BOXES (2 INPUTS)
# =========================
col1, col2 = st.columns(2)

with col1:
    search_text = st.text_input("🔍 Product Name Search (Floating)")

with col2:
    barcode = st.text_input("📟 Barcode / SKU Scan")

# =========================
# BARCODE DIRECT SELECT
# =========================
selected = None

if barcode.strip():
    code = norm(barcode)

    for p in products:
        if norm(p.get("barcode")) == code or norm(p.get("sku")) == code:
            selected = p
            break

# =========================
# FLOATING DROPDOWN (NAME SEARCH)
# =========================
dropdown = st.empty()

if selected is None and search_text.strip():

    matches = search_products(search_text)

    if matches:

        with dropdown.container():

            st.markdown("""
            <style>
            .floatbox {
                border: 1px solid #ddd;
                border-radius: 12px;
                max-height: 260px;
                overflow-y: auto;
                background: white;
                box-shadow: 0 12px 30px rgba(0,0,0,0.15);
                padding: 6px;
            }
            </style>
            """, unsafe_allow_html=True)

            st.markdown('<div class="floatbox">', unsafe_allow_html=True)

            for i, p in enumerate(matches[:12]):

                label = f"{p['name']} | {safe_float(p.get('selling_price')):,.0f} MMK"

                if st.button(label, key=f"f_{i}"):

                    st.session_state.selected = p
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)


# =========================
# SELECTED PRODUCT
# =========================
selected = st.session_state.selected

if selected:

    st.divider()
    st.subheader("📦 Selected Product")

    c1, c2, c3 = st.columns([4, 1, 1])

    c1.write(selected["name"])

    qty = c2.number_input("Qty", 1, 999, 1)

    if c3.button("➕ Add to Cart", type="primary"):

        st.session_state.cart.append({
            "id": selected["id"],
            "name": selected["name"],
            "selling_price": safe_float(selected.get("selling_price")),
            "tax_rate": safe_float(selected.get("tax_rate", 0)),
            "discount_allowed": bool(selected.get("discount_allowed", False)),
            "qty": qty
        })

        st.session_state.selected = None
        st.rerun()


# =========================
# CART (WITH TAX + DISCOUNT)
# =========================
st.divider()
st.subheader("🧾 Cart")

if not st.session_state.cart:
    st.info("Cart is empty")

else:

    subtotal = 0
    total_tax = 0

    for i, item in enumerate(st.session_state.cart):

        c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])

        name = item["name"]
        price = safe_float(item["selling_price"])
        qty = item["qty"]

        tax_rate = safe_float(item.get("tax_rate", 0))
        discount_allowed = item.get("discount_allowed", False)

        line_total = price * qty
        tax = line_total * (tax_rate / 100)

        total_line = line_total + tax

        c1.write(name)

        new_qty = c2.number_input(
            "Qty",
            1, 999,
            qty,
            key=f"q_{i}"
        )

        item["qty"] = new_qty

        c3.write(f"{tax_rate}% | { 'DISC' if discount_allowed else 'NO' }")

        c4.write(f"{total_line:,.0f} MMK")

        if c5.button("🗑", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

        subtotal += line_total
        total_tax += tax

    st.markdown("---")
    st.markdown(f"### Subtotal: {subtotal:,.0f} MMK")
    st.markdown(f"### Tax: {total_tax:,.0f} MMK")
    st.markdown(f"## TOTAL: {(subtotal + total_tax):,.0f} MMK")

    # =========================
    # CHECKOUT
    # =========================
    if st.button("💳 Pay & Print", type="primary"):

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

        if result and isinstance(result, dict) and result.get("success"):
            st.success("Sale Completed Successfully")
            st.session_state.cart = []
            st.session_state.selected = None
            st.rerun()

        elif result and isinstance(result, dict) and "error" in result:
            st.error(result["error"])

        else:
            st.error("Transaction failed")
