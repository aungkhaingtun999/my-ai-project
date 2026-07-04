import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="Professional POS", layout="centered")

# --- UI Styling ---
st.markdown("""<style>
    .receipt-box { background: white; color: black; padding: 20px; border: 1px solid #333; 
                   font-family: 'Courier New', monospace; width: 320px; margin: auto; }
</style>""", unsafe_allow_html=True)

if "cart" not in st.session_state: st.session_state.cart = []

products = get_products() or []
product_map = {f"{p['name']} ({p.get('sku', '')})": p for p in products}

def clear_all(): st.session_state.cart = []

st.subheader("🛒 Professional POS")

# --- SEARCH & AUTO-ADD ---
c1, c2 = st.columns(2)
barcode = c1.text_input("📟 Barcode/SKU", key="bc_in")
name = c2.selectbox("🔍 Search Name", [""] + list(product_map.keys()), key="name_in")

# Logic: Barcode သို့မဟုတ် Name တစ်ခုခုမှန်လျှင် ချက်ချင်း Add လုပ်ရန်
selected = None
if barcode:
    selected = next((p for p in products if barcode in [str(p.get('barcode', '')), str(p.get('sku', ''))]), None)
elif name:
    selected = product_map[name]

if selected:
    # ချက်ချင်း ခြင်းတောင်းထဲ ထည့်ပြီး Search box တွေကို ပြန်ရှင်းပေးခြင်း
    st.session_state.cart.append({**selected, "qty": 1, "uid": f"{selected['id']}_{len(st.session_state.cart)}"})
    # Search box ရှင်းရန်အတွက် Rerun
    st.rerun()

# --- CART DISPLAY ---
if st.session_state.cart:
    st.divider()
    subtotal = 0
    
    def delete_item(uid): st.session_state.cart = [i for i in st.session_state.cart if i["uid"] != uid]
    
    for item in st.session_state.cart:
        c = st.columns([2, 1, 1, 0.5])
        c[0].write(item['name'])
        c[1].write(f"{float(item['selling_price']):,.0f}")
        c[2].number_input("Qty", 1, 99, item['qty'], key=f"q_{item['uid']}")
        c[3].button("🗑", key=f"del_{item['uid']}", on_click=delete_item, args=(item['uid'],))
        subtotal += float(item['selling_price']) * item['qty']

    st.divider()
    tax = st.number_input("Total Tax %", 0.0, 100.0, 0.0)
    disc = st.number_input("Total Discount", 0.0, 100000.0, 0.0)
    final_total = subtotal - disc + ((subtotal - disc) * tax / 100)
    
    st.markdown(f"### Total: {final_total:,.0f} MMK")
    
    if st.button("💳 Pay & Print", type="primary"):
        res = checkout_sale_rpc(st.session_state.cart, final_total, None)
        if res and res.get("success"):
            st.success("Success!")
            st.button("New Sale", on_click=clear_all)
