import streamlit as st
from database import get_products, checkout_sale_rpc

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="POS v10 Enterprise", layout="wide")

st.title("🛒 POS v10 Enterprise POS")

# =========================
# SESSION
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
# SEARCH ENGINE (NAME ONLY)
# =========================
def search_by_name(keyword):
    keyword = norm(keyword)
    if not keyword:
        return []

    results = []

    for p in products:
        name = norm(p.get("name"))

        score = 0
        if keyword == name:
            score += 1000
        if name.startswith(keyword):
            score += 500
        if keyword in name:
            score += 300

        if score:
            results.append((score, p))

    results.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in results]

# =========================
# SEARCH UI (2 BOXES)
# =========================
col1, col2 = st.columns(2)

# ---------- NAME SEARCH ----------
with col1:
    st.subheader("🔍 Product Name Search")

    name_input = st.text_input("Type product name")

    selected_by_name = None

    if name_input:
        matches = search_by_name(name_input)

        if matches:
            labels = [
                f"{p['name']} | {safe_float(p.get('selling_price')):,.0f} MMK"
                for p in matches[:15]
            ]

            choice = st.selectbox("Results", labels)

            selected_by_name = matches[labels.index(choice)]

# ---------- BARCODE SEARCH ----------
with col2:
    st.subheader("📟 Barcode / SKU Scan")

    barcode_input = st.text_input("Scan or type barcode / SKU")

    selected_by_code = None

    if barcode_input:
        code = norm(barcode_input)

        for p in products:
            if code == norm(p.get("barcode")) or code == norm(p.get("sku")):
                selected_by_code = p
                break

# =========================
# FINAL SELECT
# =========================
selected = selected_by_name or selected_by_code

# =========================
# PRODUCT PANEL
# =========================
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

        st.success("Added to cart")
        st.rerun()

# =========================
# CART SECTION
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

        base = price * qty
        tax = base * (tax_rate / 100)
        total = base + tax

        c1.write(name)

        new_qty = c2.number_input(
            "Qty",
            1, 999,
            qty,
            key=f"qty_{i}"
        )

        item["qty"] = new_qty

        c3.write(f"{tax_rate}%")
        c4.write(f"{total:,.0f}")

        if c5.button("🗑", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

        subtotal += base
        total_tax += tax
        grand_total += total

    st.markdown("---")
    st.markdown(f"### Subtotal: {subtotal:,.0f} MMK")
    st.markdown(f"### Tax: {total_tax:,.0f} MMK")
    st.markdown(f"### Grand Total: {grand_total:,.0f} MMK")

# =========================
# CHECKOUT
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

    result = checkout_sale_rpc(prepared_cart, float(grand_total), None)

    if result and isinstance(result, dict) and result.get("success"):
        st.success("Sale completed successfully")
        st.session_state.cart = []
        st.rerun()
    else:
        st.error("Checkout failed")
