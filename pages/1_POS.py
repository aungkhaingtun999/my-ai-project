import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="Professional POS", layout="centered")

if "cart" not in st.session_state: st.session_state.cart = []
if "selection_pool" not in st.session_state: st.session_state.selection_pool = []

products = get_products() or []
search_options = [""] + [f"{p.get('barcode', '')} | {p['name']} ({p.get('sku', '')})" for p in products]

st.subheader("🛒 Professional POS")

# 1. Search Box
search_selection = st.selectbox("🔍 Search Barcode or Product Name", search_options, key="search_in")

if search_selection and search_selection != "":
    selected = next((p for p in products if f"{p.get('barcode', '')} | {p['name']} ({p.get('sku', '')})" == search_selection), None)
    if selected:
        uid = f"{selected['id']}_{len(st.session_state.selection_pool)}"
        st.session_state.selection_pool.append({**selected, "uid": uid})
        st.rerun()

# 2. Selection Pool (ယာယီစာရင်းကို ရှင်းလင်းစွာပြသခြင်း)
if st.session_state.selection_pool:
    st.write("--- ယာယီရွေးထားသော ပစ္စည်းများ ---")
    
    # ယာယီစာရင်းကို List ပုံစံပြပြီး ဖြုတ်လို့ရအောင်လုပ်ခြင်း
    for i, item in enumerate(st.session_state.selection_pool):
        c1, c2 = st.columns([4, 1])
        c1.write(f"{i+1}. {item['name']}")
        if c2.button("❌", key=f"del_pool_{item['uid']}"):
            st.session_state.selection_pool.pop(i)
            st.rerun()

    # Add & Clear Buttons
    col_a, col_b = st.columns(2)
    if col_a.button("📥 Add All to Cart", type="primary"):
        st.session_state.cart.extend(st.session_state.selection_pool)
        st.session_state.selection_pool = []
        st.rerun()
    if col_b.button("🗑 Clear All Selection"):
        st.session_state.selection_pool = []
        st.rerun()

# 3. Cart Display
if st.session_state.cart:
    st.divider()
    subtotal = 0
    def delete_item(uid): st.session_state.cart = [i for i in st.session_state.cart if i["uid"] != uid]
    
    for item in st.session_state.cart:
        c = st.columns([2, 1, 1, 0.5])
        c[0].write(item['name'])
        c[1].write(f"{float(item['selling_price']):,.0f}")
        item['qty'] = c[2].number_input("Qty", 1, 99, item.get('qty', 1), key=f"q_{item['uid']}")
        c[3].button("🗑", key=f"del_{item['uid']}", on_click=delete_item, args=(item['uid'],))
        subtotal += float(item['selling_price']) * item['qty']

    # Checkout Section... (ယခင်ကအတိုင်း Receipt ပုံစံ ဆက်ထားပါ)
    # ... (Checkout logic ထည့်ရန်)
    st.divider()
    tax_rate = st.number_input("Total Tax %", 0.0, 100.0, 0.0)
    discount = st.number_input("Total Discount", 0.0, 100000.0, 0.0)
    final_tax = (subtotal - discount) * (tax_rate / 100)
    final_total = subtotal - discount + final_tax
    
    st.markdown(f"### Grand Total: {final_total:,.0f} MMK")
    
    if st.button("💳 Pay & Print", type="primary"):
        res = checkout_sale_rpc(st.session_state.cart, final_total, None)
        if res and res.get("success"):
            st.success("Payment Successful!")
            # World Class Receipt Generation
            items_lines = "".join([f"{i['name'][:15]:<15} x{i['qty']} : {(float(i['selling_price'])*i['qty']):,.0f}\n" for i in st.session_state.cart])
            st.markdown(f"""
            <div class="receipt-box">
                <center><b>ENTERPRISE WORLD CLASS</b><br>Tachileik Branch<br>-------------------------------</center>
                <pre>{items_lines}</pre>
                -------------------------------<br>
                <b>SUBTOTAL :</b> {subtotal:,.0f}<br>
                <b>DISCOUNT :</b> {discount:,.0f}<br>
                <b>TAX ({tax_rate}%) :</b> {final_tax:,.0f}<br>
                <b>GRAND TOTAL : {final_total:,.0f} MMK</b><br>
                <center>Thank You!</center>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("New Sale"):
                st.session_state.cart = []
                st.rerun()
