import streamlit as st
from database import get_products, checkout_sale_rpc

# =========================
# CONFIG (MUST FIRST)
# =========================
st.set_page_config(page_title="POS v10 Enterprise", layout="wide")

st.title("🛒 POS v10 Enterprise")

# =========================
# SESSION STATE
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "last_selected" not in st.session_state:
    st.session_state.last_selected = None

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
# SEARCH UI (FIXED ALIGNMENT)
# =========================
c1, c2 = st.columns([2, 2])

with c1:
    search_name = st.text_input("🔍 Product Name")

with c2:
    barcode = st.text_input("📟 Barcode / SKU")

selected_product = None

# barcode priority
if barcode:
    for p in products:
        if barcode == str(p.get("barcode")) or barcode == str(p.get("sku")):
            selected_product = p
            break

# name search dropdown (NO RESET)
if selected_product is None and search_name:
    matches = search_products(search_name)

    if matches:
        options = [
            f"{p['name']} | {safe_float(p.get('selling_price')):,.0f} MMK"
            for p in matches[:15]
        ]

        choice = st.selectbox(
            "Search Result",
            options,
            key="product_dropdown"
        )

        selected_product = matches[options.index(choice)]


# =========================
# PRODUCT PREVIEW (SMALL UI FIX)
# =========================
if selected_product:
    st.markdown("---")

    col1, col2, col3 = st.columns([4, 1, 1])

    with col1:
        st.write(f"**{selected_product['name']}**")

        st.caption(f"Barcode: {selected_product.get('barcode','')}")
        st.caption(f"SKU: {selected_product.get('sku','')}")

    with col2:
        st.metric("Price", f"{safe_float(selected_product.get('selling_price')):,.0f}")

    with col3:
        qty = st.number_input("Qty", 1, 999, 1, key="qty_input")

    # discount + tax show FIX
    tax_rate = safe_float(selected_product.get("tax_rate", 0))
    discount_allowed = bool(selected_product.get("discount_allowed", False))

    st.write(f"Tax: {tax_rate}% | Discount: {'YES' if discount_allowed else 'NO'}")

    if st.button("➕ Add to Cart", type="primary"):

        item = {
            "id": selected_product["id"],
            "name": selected_product["name"],
            "selling_price": safe_float(selected_product.get("selling_price")),
            "qty": qty,
            "tax_rate": tax_rate,
            "discount_allowed": discount_allowed
        }

        # IMPORTANT: accumulate (NO overwrite)
        found = False
        for c in st.session_state.cart:
            if c["id"] == item["id"]:
                c["qty"] += qty
                found = True
                break

        if not found:
            st.session_state.cart.append(item)

        st.success("Added to cart")
        st.rerun()


# =========================
# CART (FIXED + COMPACT UI)
# =========================
st.markdown("## 🧾 Cart")

if len(st.session_state.cart) == 0:
    st.info("Cart is empty")

else:
    subtotal = 0
    total_tax = 0

    for i, item in enumerate(st.session_state.cart):

        c1, c2, c3, c4, c5 = st.columns([4, 1, 1, 1, 1])

        price = safe_float(item["selling_price"])
        qty = int(item["qty"])
        tax_rate = safe_float(item.get("tax_rate", 0))

        line = price * qty
        tax = line * (tax_rate / 100)
        total = line + tax

        c1.write(item["name"])

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
    st.write(f"**Grand Total: {(subtotal + total_tax):,.0f} MMK**")


# =========================
# CHECKOUT (SAFE RECEIPT FIX)
# =========================
if st.button("💳 Pay & Print", type="primary"):

    if not st.session_state.cart:
        st.warning("Cart is empty")
        st.stop()

    prepared = []

    for item in st.session_state.cart:
        prepared.append({
            "id": int(item["id"]),
            "qty": int(item["qty"]),
            "selling_price": float(item["selling_price"]),
            "tax_rate": float(item.get("tax_rate", 0)),
            "discount_allowed": bool(item.get("discount_allowed", False))
        })

    total_amount = sum(
        (i["selling_price"] * i["qty"]) * (1 + i.get("tax_rate", 0)/100)
        for i in st.session_state.cart
    )

    with st.spinner("Processing..."):
        result = checkout_sale_rpc(prepared, float(total_amount), None)

    if result and isinstance(result, dict) and result.get("success"):
        st.success("Sale completed successfully")

        # IMPORTANT: receipt bug FIX (clear AFTER success only)
        st.session_state.cart = []
        st.rerun()

    else:
        st.error("Checkout failed")
