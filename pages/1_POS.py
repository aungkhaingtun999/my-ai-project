import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v6 Floating Search ERP", layout="wide")

st.title("🛒 POS v6 Shopify-Level Floating Search ERP")

# ======================================================
# SAFE FLOAT
# ======================================================
def safe_float(v):
    try:
        return float(v) if v is not None else 0.0
    except:
        return 0.0


# ======================================================
# SESSION STATE
# ======================================================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "selected_product" not in st.session_state:
    st.session_state.selected_product = None


# ======================================================
# LOAD PRODUCTS
# ======================================================
products = get_products() or []


# ======================================================
# NORMALIZE + SCORE ENGINE
# ======================================================
def norm(v):
    return str(v or "").lower().replace(" ", "")


def score(p, q):
    if not q:
        return 0

    q = norm(q)
    name = norm(p.get("name"))
    barcode = norm(p.get("barcode"))
    sku = norm(p.get("sku"))

    s = 0

    if q == name or q == barcode or q == sku:
        s += 200

    if name.startswith(q):
        s += 120

    if q in name:
        s += 90

    if q in barcode or q in sku:
        s += 80

    return s


# ======================================================
# SEARCH INPUT
# ======================================================
search = st.text_input("🔍 Search product (name / barcode / SKU)", "")


# ======================================================
# FLOATING DROPDOWN ENGINE (IMPORTANT PART)
# ======================================================
results = []

if search:
    for p in products:
        sc = score(p, search)
        if sc > 0:
            p["_score"] = sc
            results.append(p)

    results.sort(key=lambda x: x["_score"], reverse=True)

    # limit like real autocomplete dropdown
    results = results[:8]


# ======================================================
# FLOAT DROPDOWN UI (CUSTOM OVERLAY STYLE)
# ======================================================
if search:

    st.markdown(
        """
        <style>
        .float-box {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 5px;
            max-height: 250px;
            overflow-y: auto;
            background: white;
        }
        .item {
            padding: 10px;
            border-bottom: 1px solid #eee;
            cursor: pointer;
        }
        .item:hover {
            background-color: #f2f2f2;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 🔽 Results")

    if results:

        for p in results:
            label = f"{p['name']} | {p.get('barcode')} | {p.get('sku')}"

            if st.button(label, key=f"sel_{p['id']}"):
                st.session_state.selected_product = p
                st.rerun()

    else:
        st.info("No matching product")


# ======================================================
# SELECTED PRODUCT DETAIL (ONLY AFTER CLICK)
# ======================================================
p = st.session_state.selected_product

if p:

    st.divider()
    st.subheader("🛒 Product Detail")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.write(p["name"])
        st.caption(f"{p.get('barcode')} | {p.get('sku')} | {p.get('unit','pcs')}")

    with col2:
        st.write(f"💰 {safe_float(p.get('selling_price')):,.0f}")

    qty = st.number_input("Qty", 1, 100, 1)

    if st.button("➕ Add to Cart"):

        pid = p["id"]

        for item in st.session_state.cart:
            if item["id"] == pid:
                item["qty"] += qty
                break
        else:
            st.session_state.cart.append({
                "id": pid,
                "name": p["name"],
                "barcode": p["barcode"],
                "sku": p["sku"],
                "unit": p.get("unit", "pcs"),
                "selling_price": safe_float(p.get("selling_price")),
                "qty": qty
            })

        st.session_state.selected_product = None
        st.success("Added")
        st.rerun()


# ======================================================
# CART
# ======================================================
st.divider()
st.subheader("🧾 Cart")

subtotal = 0

for item in st.session_state.cart:
    line = item["selling_price"] * item["qty"]
    subtotal += line

    c1, c2, c3 = st.columns([5, 2, 2])
    c1.write(item["name"])
    c2.write(f"{item['qty']} x {item['selling_price']:,.0f}")
    c3.write(f"{line:,.0f}")


st.write("## Subtotal:", f"{subtotal:,.0f} MMK")


# ======================================================
# TOTAL
# ======================================================
c1, c2 = st.columns(2)

discount = c1.number_input("Discount (%)", 0.0, 100.0, 0.0)
tax = c2.number_input("Tax (%)", 0.0, 100.0, 5.0)

after_discount = subtotal * (1 - discount / 100)
total = after_discount * (1 + tax / 100)

st.markdown(f"## 🧾 TOTAL: {total:,.0f} MMK")


# ======================================================
# PAYMENT
# ======================================================
paid = st.number_input("Paid Amount", 0.0)

if st.button("💳 Pay & Print"):

    if not st.session_state.cart:
        st.error("Cart is empty")
        st.stop()

    if paid < total:
        st.error("Insufficient payment")
        st.stop()

    result = checkout_sale_rpc(st.session_state.cart, paid_amount=paid)

    if isinstance(result, dict) and result.get("error"):
        st.error(result["error"])
        st.stop()

    st.success(f"Sale ID: {result.get('sale_id')}")
    st.info(f"Receipt: {result.get('receipt_no')}")

    st.session_state.cart = []
    st.session_state.selected_product = None
    st.rerun()
