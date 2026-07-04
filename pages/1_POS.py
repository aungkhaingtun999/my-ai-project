import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v8 Smart ERP", layout="wide")

# ======================================================
# HELPERS
# ======================================================
def safe_float(v):
    try: return float(v) if v is not None else 0.0
    except: return 0.0

# ======================================================
# SESSION STATE
# ======================================================
if "cart" not in st.session_state: st.session_state.cart = []

products = get_products() or []

st.title("🛒 POS v8 Smart POS")

# ======================================================
# SEARCH / SELECT SECTION (Dropdown Style)
# ======================================================
# Excel dropdown လိုမျိုး ရွေးချယ်စရာ list ပြုလုပ်ခြင်း
product_options = {f"{p['name']} | {safe_float(p.get('selling_price')):,.0f} MMK": p for p in products}

selected_label = st.selectbox("🔍 Select Product", options=[""] + list(product_options.keys()), index=0)

if selected_label:
    p = product_options[selected_label]
    col1, col2 = st.columns([3, 1])
    qty = col1.number_input("Quantity", min_value=1, value=1, key="add_qty")
    
    if col2.button("➕ Add to Cart"):
        cart_item = {
            "id": p["id"],
            "name": p["name"],
            "selling_price": safe_float(p.get("selling_price")),
            "qty": qty
        }
        
        # Cart ထဲမှာ ရှိပြီးသားဆို qty ပေါင်းပေးခြင်း
        found = False
        for item in st.session_state.cart:
            if item["id"] == cart_item["id"]:
                item["qty"] += qty
                found = True
        if not found:
            st.session_state.cart.append(cart_item)
        
        st.success(f"Added {p['name']} to cart!")
        st.rerun()

# ======================================================
# CART SECTION
# ======================================================
st.divider()
st.subheader("🧾 Cart")

if st.session_state.cart:
    # Cart ကို display လုပ်ခြင်း (ရင်ရွေးထားတာတွေ မပျောက်တော့ပါ)
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
        c1.write(item["name"])
        item["qty"] = c2.number_input("Qty", 1, 99, item["qty"], key=f"q_{i}")
        c3.write(f"{(item['selling_price'] * item['qty']):,.0f} MMK")
        if c4.button("🗑", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

    subtotal = sum(i["selling_price"] * i["qty"] for i in st.session_state.cart)
    st.markdown(f"### Total: {subtotal:,.0f} MMK")
    
    # PAY & PRINT
    if st.button("💳 Pay & Print", type="primary"):
        prepared_cart = []
        for item in st.session_state.cart:
            prepared_cart.append({
                "id": int(float(item["id"])),
                "qty": int(float(item["qty"])),
                "selling_price": float(item["selling_price"])
            })

        try:
            result = checkout_sale_rpc(prepared_cart, paid_amount=float(subtotal))
            if isinstance(result, dict) and result.get("error"):
                st.error(f"Error: {result.get('error')}")
            else:
                st.success("အရောင်း အောင်မြင်ပါသည်။")
                st.session_state.cart = []
                st.rerun()
        except Exception as e:
            st.error(f"API Connection Error: {str(e)}")
else:
    st.info("ခြင်းတောင်း ဗလာဖြစ်နေပါသည်။")
