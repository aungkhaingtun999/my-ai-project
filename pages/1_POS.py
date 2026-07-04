import streamlit as st
from database import get_products

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="POS v10 Enterprise", layout="wide")

st.title("🛒 POS v10 Enterprise")

# =========================
# SESSION INIT
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
        if keyword in name:
            score += 300

        if keyword in barcode or keyword in sku:
            score += 250

        if score:
            results.append((score, p))

    results.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in results]

# =========================
# SEARCH INPUTS
# =========================
col1, col2 = st.columns(2)

with col1:
    search_name = st.text_input("🔍 Search Product Name")

with col2:
    barcode = st.text_input("📟 Barcode / SKU")

# =========================
# SELECT PRODUCT
# =========================
selected = None

# barcode first
if barcode:
    for p in products:
        if barcode == str(p.get("barcode")) or barcode == str(p.get("sku")):
            selected = p
            break

# name search
if selected is None and search_name:
    matches = search_products(search_name)

    if matches:
        labels = [
            f"{p['name']} | {safe_float(p.get('selling_price')):,.0f} MMK"
            for p in matches[:10]
        ]

        choice = st.selectbox("Search Results", labels)

        selected = matches[labels.index(choice)]

# =========================
# ADD TO CART
# =========================
if selected:
    st.divider()
    st.subheader("📦 Product")

    colA, colB, colC = st.columns([3,1,1])

    colA.write(selected["name"])
    qty = colB.number_input("Qty", 1, 999, 1)

    price = safe_float(selected.get("selling_price"))
    tax_rate = safe_float(selected.get("tax_rate", 0))
    discount_allowed = bool(selected.get("discount_allowed", False))

    if colC.button("➕ Add to Cart"):

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

        st.session_state.selected = None
        st.success("Added to cart")
        st.rerun()

# =========================
# CART SECTION (FIXED)
# =========================
st.divider()
st.subheader("🧾 Cart")

cart = st.session_state.cart

if len(cart) == 0:
    st.info("Cart is empty")

else:

    subtotal = 0
    total_tax = 0
    grand_total = 0

    for i, item in enumerate(cart):

        c1, c2, c3, c4, c5 = st.columns([3,1,1,1,1])

        name = item.get("name")
        price = safe_float(item.get("selling_price"))
        qty = item.get("qty", 1)
        tax_rate = safe_float(item.get("tax_rate", 0))

        line_base = price * qty
        tax = line_base * (tax_rate / 100)
        total = line_base + tax

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
        c4.write(f"{total:,.0f}")

        if c5.button("🗑", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

        subtotal += line_base
        total_tax += tax
        grand_total += total

    st.markdown("---")
    st.write(f"Subtotal: {subtotal:,.0f}")
    st.write(f"Tax: {total_tax:,.0f}")
    st.write(f"Grand Total: {grand_total:,.0f}")
