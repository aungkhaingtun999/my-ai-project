import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS", layout="centered", initial_sidebar_state="collapsed")

# Compact CSS
st.markdown("""
<style>
    .stButton>button { font-size: 12px; padding: 5px; }
    .stNumberInput input { font-size: 13px; }
    div[data-testid="stExpander"] { font-size: 12px; }
</style>
""", unsafe_allow_html=True)

if "cart" not in st.session_state: st.session_state.cart = []

products = get_products() or []
product_map = {f"{p['name']} | {float(p.get('selling_price',0)):,.0f}": p for p in products}

st.subheader("🛒 POS System")

# --- SEARCH ---
search_selection = st.selectbox("🔍 Select Product", [""] + list(product_map.keys()))

if search_selection:
    selected = product_map[search_selection]
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        col1.markdown(f"**{selected['name']}**")
        col1.caption(f"💰 {float(selected.get('selling_price',0)):,.0f} | Tax: {selected.get('tax_rate',0)}% | Disc: {'Yes' if selected.get('discount_allowed') else 'No'}")
        qty = col2.number_input("Qty", 1, 99, 1, key="q_input")
        if col2.button("➕ Add"):
            item = {**selected, "qty": qty}
            found = False
            for c in st.session_state.cart:
                if c["id"] == item["id"]: c["qty"] += qty; found = True
            if not found: st.session_state.cart.append(item)
            st.rerun()

# --- CART ---
if st.session_state.cart:
    st.divider()
    subtotal = 0
    total_tax = 0
    
    for i, item in enumerate(st.session_state.cart):
        p = float(item.get('selling_price', 0))
        t = float(item.get('tax_rate', 0))
        l_total = p * item['qty']
        t_amt = l_total * (t / 100)
        
        cols = st.columns([2, 1, 1, 1])
        cols[0].write(f"• {item['name'][:15]}...")
        cols[1].write(f"x{item['qty']}")
        cols[2].write(f"{(l_total+t_amt):,.0f}")
        if cols[3].button("🗑", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()
        subtotal += l_total
        total_tax += t_amt

    st.markdown(f"**Subtotal:** {subtotal:,.0f} | **Tax:** {total_tax:,.0f}")
    st.markdown(f"### Total: {(subtotal + total_tax):,.0f} MMK")

    if st.button("💳 Pay & Print", type="primary"):
        prepared = [{
            "id": i["id"], "qty": i["qty"], "selling_price": float(i["selling_price"]),
            "tax_rate": float(i.get("tax_rate", 0)), "discount_allowed": bool(i.get("discount_allowed", False))
        } for i in st.session_state.cart]
        
        res = checkout_sale_rpc(prepared, subtotal + total_tax, None)
        
        if res and res.get("success"):
            st.success("Success!")
            # Receipt Display
            st.info(f"🧾 Receipt: {res.get('receipt_no')}\n\nTotal: {(subtotal + total_tax):,.0f} MMK")
            st.session_state.cart = []
            if st.button("OK"): st.rerun()
        else:
            st.error("Checkout Failed")
