import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v6 Split Search ERP", layout="wide")

st.title("🛒 POS v6 Smart Split Search Engine")


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
# SEARCH INPUTS (IMPORTANT FIX)
# ======================================================

name_search = st.text_input("🔍 Search Product Name", "")
code_search = st.text_input("📟 Barcode / SKU Scanner Input", "")


# normalize
def norm(v):
    return str(v or "").lower().replace(" ", "")


# ======================================================
# FILTER ENGINE 1: NAME SEARCH (FUZZY)
# ======================================================
def match_name(p, q):
    if not q:
        return True

    q = norm(q)
    name = norm(p.get("name"))

    return q in name


# ======================================================
# FILTER ENGINE 2: CODE SEARCH (EXACT / FAST)
# ======================================================
def match_code(p, q):
    if not q:
        return True

    q = norm(q)
    return (
        q == norm(p.get("barcode")) or
        q == norm(p.get("sku"))
    )


# ======================================================
# APPLY FILTER LOGIC (IMPORTANT PART)
# ======================================================

filtered = products

# STEP 1: name filter
if name_search:
    filtered = [p for p in filtered if match_name(p, name_search)]

# STEP 2: barcode/sku filter (more strict)
if code_search:
    filtered = [p for p in filtered if match_code(p, code_search)]


# ======================================================
# FLOAT LIST UI (NO SELECTBOX)
# ======================================================
st.subheader("📦 Products")

if name_search or code_search:

    if not filtered:
        st.warning("No product found")

    else:
        for p in filtered[:10]:

            pid = p["id"]
            stock = safe_float(p.get("stock"))

            with st.container(border=True):

                col1, col2, col3 = st.columns([5, 2, 1])

                with col1:
                    st.write(f"🛒 {p.get('name')}")
                    st.caption(f"{p.get('barcode')} | {p.get('sku')} | {p.get('unit','pcs')}")

                col2.write(f"💰 {safe_float(p.get('selling_price')):,.0f}")

                if col3.button("➕", key=f"add_{pid}"):

                    if stock <= 0:
                        st.error("Out of stock")
                    else:
                        for item in st.session_state.cart:
                            if item["id"] == pid:
                                item["qty"] += 1
                                break
                        else:
                            st.session_state.cart.append({
                                "id": pid,
                                "name": p["name"],
                                "barcode": p["barcode"],
                                "sku": p["sku"],
                                "unit": p.get("unit", "pcs"),
                                "selling_price": safe_float(p["selling_price"]),
                                "qty": 1
                            })

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
# TOTAL ENGINE
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
    st.rerun()
