import streamlit as st
from database import get_products, checkout_sale_rpc

# =========================
# PAGE CONFIG (MUST FIRST)
# =========================
st.set_page_config(page_title="POS v10 Enterprise", layout="wide")
st.title("🛒 POS v10 Enterprise POS")

# =========================
# SESSION STATE
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "selected_product" not in st.session_state:
    st.session_state.selected_product = None

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
# SMART SEARCH ENGINE
# =========================
def search_products(keyword):
    keyword = norm(keyword)
    if not keyword:
        return []

    scored = []

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
            scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored]


# =========================
# FLOATING SEARCH DROPDOWN
# =========================
search_text = st.text_input("🔍 Type Product Name / Barcode / SKU")

dropdown_box = st.container()

matches = search_products(search_text)


selected = None

if search_text and matches:

    with dropdown_box:

        st.markdown("""
        <style>
        .float-box {
            border: 1px solid #ddd;
            border-radius: 10px;
            max-height: 250px;
            overflow-y: auto;
            background: white;
            box-shadow: 0px 8px 20px rgba(0,0,0,0.15);
            padding: 5px;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="float-box">', unsafe_allow_html=True)

        for i, p in enumerate(matches[:12]):

            label = f"{p['name']} | {p.get('barcode','')} | {p.get('sku','')}"

            if st.button(label, key=f"sel_{i}"):

                st.session_state.selected_product = p
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# =========================
# SELECTED PRODUCT
# =========================
selected = st.session_state.selected_product

if selected:

    st.divider()
    st.subheader("📦 Selected Product")

    c1, c2, c3 = st.columns([4, 1, 1])

    c1.write(f"**{selected['name']}**")

    qty = c2.number_input("Qty", 1, 999, 1)

    price = safe_float(selected.get("selling_price"))
    tax_rate = safe_float(selected.get("tax_rate", 0))
    discount_allowed = bool(selected.get("discount_allowed", False))

    c3.metric("Price", f"{price:,.0f}")

    if st.button("➕ Add to Cart", type="primary"):

        found = False

        for item in st.session_state.cart:
            if item["id"] == selected["id"]:
                item["qty"] += qty
                found = True

        if not found:
            st.session_state.cart.append({
                "id": selected["id"],
                "name": selected["name"],
                "selling_price": price,
                "qty": qty,
                "tax_rate": tax_rate,
                "discount_allowed": discount_allowed
            })

        st.session_state.selected_product = None
        st.rerun()


# =========================
# CART (TAX + DISCOUNT FIXED)
# =========================
st.divider()
st.subheader("🧾 Cart")

cart = st.session_state.cart

if not cart:
    st.info("Cart is empty")

else:

    subtotal = 0
    total_tax = 0
    grand_total = 0

    for i, item in enumerate(cart):

        c1, c2, c3, c4, c5 = st.columns([3,1,1,1,1])

        name = item["name"]
        price = safe_float(item["selling_price"])
        qty = item["qty"]

        tax_rate = safe_float(item.get("tax_rate", 0))
        discount_allowed = item.get("discount_allowed", False)

        line_base = price * qty
        tax_amount = line_base * (tax_rate / 100)

        discount = 0
        if discount_allowed:
            discount = 0  # future hook

        total = line_base + tax_amount - discount

        c1.write(name)

        new_qty = c2.number_input(
            "Qty",
            1,
            999,
            qty,
            key=f"qty_{i}"
        )

        item["qty"] = new_qty

        c3.write(f"{tax_rate}% | Tax")

        c4.write(f"{total:,.0f}")

        if c5.button("🗑", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

        subtotal += line_base
        total_tax += tax_amount
        grand_total += total

    st.markdown("---")
    st.markdown(f"**Subtotal:** {subtotal:,.0f}")
    st.markdown(f"**Tax:** {total_tax:,.0f}")
    st.markdown(f"## 💰 Grand Total: {grand_total:,.0f}")


# =========================
# PAY BUTTON
# =========================
if cart:

    if st.button("💳 Pay & Print", type="primary"):

        prepared = []

        for item in cart:
            prepared.append({
                "id": int(item["id"]),
                "qty": int(item["qty"]),
                "selling_price": float(item["selling_price"]),
                "tax_rate": float(item.get("tax_rate", 0)),
                "discount_allowed": bool(item.get("discount_allowed", False))
            })

        with st.spinner("Processing..."):
            result = checkout_sale_rpc(
                prepared,
                float(grand_total),
                None
            )

        if result and isinstance(result, dict) and result.get("success"):
            st.success("Sale completed successfully!")
            st.session_state.cart = []
            st.session_state.selected_product = None
            st.rerun()

        elif result and isinstance(result, dict) and "error" in result:
            st.error(f"DB Error: {result['error']}")

        else:
            st.error("Transaction failed")
