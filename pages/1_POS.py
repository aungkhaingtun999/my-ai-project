import streamlit as st
from database import get_products, checkout_sale_rpc

# =========================
# PAGE CONFIG (MUST FIRST)
# =========================
st.set_page_config(page_title="POS v10 Enterprise", layout="wide")

st.title("🛒 POS v10 Enterprise POS")

# =========================
# SESSION INIT
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "selected" not in st.session_state:
    st.session_state.selected = None

products = get_products() or []

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
# SEARCH ENGINE (FAST)
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
        if keyword in name:
            score += 300
        if keyword in barcode or keyword in sku:
            score += 250

        if score:
            results.append((score, p))

    results.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in results]

# =========================
# FLOATING SEARCH UI
# =========================
search_text = st.text_input("🔍 Search Product (Name / Barcode / SKU)")

dropdown = st.container()

matches = search_products(search_text)

selected = None

if search_text and matches:

    with dropdown:
        st.markdown("""
        <style>
        .dropbox {
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
            max-height: 260px;
            overflow-y: auto;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            padding: 5px;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="dropbox">', unsafe_allow_html=True)

        for i, p in enumerate(matches[:12]):

            label = f"{p['name']} | {p.get('barcode','')} | {p.get('sku','')}"

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
    st.subheader("📦 Selected Product")

    c1, c2, c3 = st.columns([4,1,1])

    c1.write(selected["name"])
    c2.write(f"{safe_float(selected.get('selling_price')):,.0f} MMK")

    qty = c3.number_input("Qty", 1, 999, 1)

    if st.button("➕ Add to Cart", type="primary"):

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
                "selling_price": safe_float(selected.get("selling_price")),
                "tax_rate": safe_float(selected.get("tax_rate", 0)),
                "discount_allowed": bool(selected.get("discount_allowed", False)),
                "qty": qty
            })

        st.session_state.selected = None
        st.success("Added to cart")
        st.rerun()

# =========================
# CART (FULL LOGIC: TAX + DISCOUNT)
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

        # 👉 DISCOUNT (future-ready hook)
        discount = 0
        if discount_allowed:
            discount = 0  # placeholder (future manual discount UI)

        line_total = line_base + tax_amount - discount

        c1.write(name)

        new_qty = c2.number_input(
            "Qty",
            1,
            999,
            qty,
            key=f"qty_{i}"
        )

        item["qty"] = new_qty

        c3.write(f"{tax_rate}%")
        c4.write(f"{line_total:,.0f}")

        if c5.button("🗑", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

        subtotal += line_base
        total_tax += tax_amount
        grand_total += line_total

    st.markdown("---")
    st.markdown(f"### Subtotal: {subtotal:,.0f} MMK")
    st.markdown(f"### Tax: {total_tax:,.0f} MMK")
    st.markdown(f"### Grand Total: {grand_total:,.0f} MMK")

# =========================
# CHECKOUT (SAFE)
# =========================
if cart and st.button("💳 Pay & Print", type="primary"):

    prepared_cart = []

    for item in cart:
        prepared_cart.append({
            "id": int(item["id"]),
            "qty": int(item["qty"]),
            "selling_price": float(item["selling_price"]),
            "tax_rate": float(item.get("tax_rate", 0)),
            "discount_allowed": bool(item.get("discount_allowed", False))
        })

    with st.spinner("Processing sale..."):
        result = checkout_sale_rpc(
            prepared_cart,
            float(grand_total),
            None
        )

    if result and isinstance(result, dict) and result.get("success"):
        st.success("Sale completed successfully")
        st.session_state.cart = []
        st.session_state.selected = None
        st.rerun()

    else:
        st.error("Checkout failed")
