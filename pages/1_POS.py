import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v8", layout="centered")

# CSS for Floating Dropdown Effect
st.markdown("""
<style>
    div[data-testid="stVerticalBlock"] > div:has(div.floating-box) {
        position: sticky;
        top: 0;
        z-index: 999;
        background: white;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

if "cart" not in st.session_state: st.session_state.cart = []
products = get_products() or []

st.header("🛒 Smart POS")

# --- SEARCH ENGINE ---
product_map = {f"{p['name']} ({p.get('sku', '')})": p for p in products}
search_selection = st.selectbox("🔍 Search Product", [""] + list(product_map.keys()), key="search_bar")

if search_selection:
    selected = product_map[search_selection]
    
    # Product Card
    with st.container(border=True):
        st.subheader(selected['name'])
        c1, c2 = st.columns(2)
        c1.write(f"💰 {float(selected.get('selling_price', 0)):,.0f} MMK")
        c2.caption(f"Tax: {selected.get('tax_rate', 0)}% | Disc: {'Yes' if selected.get('discount_allowed') else 'No'}")
        
        qty = st.number_input("Quantity", 1, 99, 1)
        if st.button("➕ Add to Cart", type="primary"):
            item = {**selected, "qty": qty}
            # Add to cart logic
            found = False
            for c in st.session_state.cart:
                if c["id"] == item["id"]:
                    c["qty"] += qty
                    found = True
            if not found: st.session_state.cart.append(item)
            st.rerun()

# --- CART DISPLAY ---
st.subheader("🧾 Cart")
if not st.session_state.cart:
    st.info("Cart is empty")
else:
    subtotal = 0
    total_tax = 0
    for i, item in enumerate(st.session_state.cart):
        cols = st.columns([3, 1, 1, 1])
        cols[0].write(item['name'])
        item["qty"] = cols[1].number_input("Q", 1, 99, item["qty"], key=f"q_{i}")
        
        price = float(item.get("selling_price", 0))
        tax = float(item.get("tax_rate", 0))
        line = price * item["qty"]
        tax_amt = line * (tax / 100)
        
        cols[2].write(f"{(line + tax_amt):,.0f}")
        if cols[3].button("🗑", key=f"d_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()
        subtotal += line
        total_tax += tax_amt

    total_payable = subtotal + total_tax
    st.markdown(f"### Total: {total_payable:,.0f} MMK")

    if st.button("💳 Pay & Print", type="primary"):
        # Format Data
        prepared = [{
            "id": i["id"], "qty": i["qty"], "selling_price": float(i["selling_price"]),
            "tax_rate": float(i.get("tax_rate", 0)), "discount_allowed": bool(i.get("discount_allowed", False))
        } for i in st.session_state.cart]
        
        result = checkout_sale_rpc(prepared, total_payable, None)
        
        if result and result.get("success"):
            st.success("Transaction Successful!")
            # Receipt Simulation (Show in expander)
            with st.expander("🧾 View Receipt"):
                st.write(f"Receipt No: {result.get('receipt_no')}")
                st.write(f"Grand Total: {total_payable:,.0f} MMK")
            st.session_state.cart = []
            st.rerun()
        else:
            st.error("Checkout Failed")
