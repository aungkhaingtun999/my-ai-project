import streamlit as st
from database import get_products, checkout_sale_rpc

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="POS v10 Enterprise", layout="wide")
st.title("🛒 POS v10 Enterprise")

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
# SEARCH UI (2 BOXES)
# =========================
c1, c2 = st.columns(2)

with c1:
    search_name = st.text_input("🔍 Product Name")

with c2:
    barcode = st.text_input("📟 Barcode / SKU")

# =========================
# SELECT PRODUCT
# =========================
selected = None

# barcode priority
if barcode:
    for p in products:
        if barcode == str(p.get("barcode")) or barcode == str(p.get("sku")):
            selected = p
            break

# name search dropdown
if selected is None and search_name:
    matches = search_products(search_name)

    if matches:
        labels = [
            f"{p['name']} | {safe_float(p.get('selling_price')):,.0f} MMK"
            for p in matches[:15]
        ]

        choice = st.selectbox(
            "Search Result",
            labels,
            key="dropdown_product"
        )

        selected = matches[labels.index(choice)]

        # keep selection in session (IMPORTANT FIX)
        st.session_state.selected_product = selected

# restore selection if rerun
if selected is None:
    selected = st.session_state.selected_product


# =========================
# PRODUCT SECTION
# =========================
if selected:

    st.markdown("---")

    col1, col2, col3 = st.columns([4, 1, 1])

    with col1:
        st.write(f"**{selected['name']}**")
        st.caption(f"Barcode: {selected.get('barcode','')}")
        st.caption(f"SKU: {selected.get('sku','')}")

    with col2:
        st.metric("Price", f"{safe_float(selected.get('selling_price')):,.0f}")

    with col3:
        qty = st.number_input("Qty", 1, 999, 1, key="qty_input")

    tax_rate = safe_float(selected.get("tax_rate", 0))
    discount_allowed = bool(selected.get("discount_allowed", False))

    st.write(f"Tax: {tax_rate}% | Discount: {'YES' if discount_allowed else 'NO'}")

    if st.button("➕ Add to Cart", type="primary"):

        item = {
            "id": selected["id"],
            "name": selected["name"],
            "selling_price": safe_float(selected.get("selling_price")),
            "qty": qty,
            "tax_rate": tax_rate,
            "discount_allowed": discount_allowed
        }

        # merge cart
        found = False
        for c in st.session_state.cart:
            if c["id"] == item["id"]:
                c["qty"] += qty
                found = True
                break

        if not found:
            st.session_state.cart.append(item)

        st.session_state.selected_product = None
        st.success("Added to cart")
        st.rerun()


# =========================
# CART SECTION (FIXED + CLEAN UI)
# =========================
st.markdown("## 🧾 Cart")

if len(st.session_state.cart) == 0:
    st.info("Cart is empty")

else:
    subtotal = 0
    total_tax = 0

    for i, item in enumerate(st.session_state.cart):

        c1, c2, c3, c4, c5 = st.columns([4, 1, 1, 1, 1])

        price = safe_float(item.get("selling_price"))
        qty = int(item.get("qty", 1))
        tax_rate = safe_float(item.get("tax_rate", 0))

        line = price * qty
        tax = line * (tax_rate / 100)
        total = line + tax

        c1.write(item.get("name", "Unknown"))

        new_qty = c2.number_input(
            "",
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

        subtotal += line
        total_tax += tax

    st.markdown("---")
    st.write(f"Subtotal: {subtotal:,.0f}")
    st.write(f"Tax: {total_tax:,.0f}")
    st.write(f"### Grand Total: {(subtotal + total_tax):,.0f} MMK")


# =========================
# CHECKOUT (FIXED RECEIPT LOGIC)
# =========================
if st.button("💳 Pay & Print", type="primary"):

    if not st.session_state.cart:
        st.warning("Cart is empty")
        st.stop()

    prepared = [
        {
            "id": int(i["id"]),
            "qty": int(i["qty"]),
            "selling_price": float(i["selling_price"]),
            "tax_rate": float(i.get("tax_rate", 0)),
            "discount_allowed": bool(i.get("discount_allowed", False))
        }
        for i in st.session_state.cart
    ]

    total_amount = sum(
        (i["selling_price"] * i["qty"]) * (1 + i.get("tax_rate", 0) / 100)
        for i in st.session_state.cart
    )

    with st.spinner("Processing sale..."):
        result = checkout_sale_rpc(prepared, float(total_amount), None)

    if result and isinstance(result, dict) and result.get("success"):

        st.success("Sale completed successfully 🎉")

        # FIX: only clear AFTER success
        st.session_state.cart = []
        st.session_state.selected_product = None

        st.rerun()

    else:
        st.error("Checkout failed")
