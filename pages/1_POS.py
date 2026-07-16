import streamlit as st
import sys
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from database import get_products, checkout_sale_rpc
from auth import is_authenticated
try:
    from utils.thermal_receipt import print_thermal
    from utils.receipt_pdf import generate_pdf
except ImportError:
    pass

def get_mst_now():
    return datetime.now(ZoneInfo("Asia/Yangon")).strftime("%Y-%m-%d %H:%M:%S")

st.set_page_config(page_title="Enterprise POS", layout="wide", page_icon="🛒")

if not is_authenticated():
    st.error("ကျေးဇူးပြု၍ Login အရင်ဝင်ပေးပါ။")
    st.stop()

if "cart" not in st.session_state: st.session_state.cart = []
if "show_receipt" not in st.session_state: st.session_state.show_receipt = False

products = get_products() or []

st.subheader("🛒 Enterprise POS")

# Search & Add to Cart
col_s1, col_s2 = st.columns(2)
name_query = col_s1.text_input("🔍 Search by Name", key="name_search")
code_query = col_s2.text_input("🔍 Search by SKU or Barcode", key="code_search")

selected_product = None
if name_query:
    matches = [p for p in products if name_query.lower() in p['name'].lower()]
    if matches: selected_product = st.selectbox("Select product:", matches, format_func=lambda x: f"{x['name']} ({x['sku']})")
elif code_query:
    matches = [p for p in products if code_query.lower() in str(p.get('barcode', '')).lower() or code_query.lower() in str(p.get('sku', '')).lower()]
    if matches: selected_product = matches[0]

if selected_product:
    qty = st.number_input("Quantity", min_value=1, value=1)
    if st.button("➕ Add to Cart", type="primary"):
        existing = next((item for item in st.session_state.cart if item["id"] == selected_product["id"]), None)
        if existing: existing["qty"] += qty
        else: st.session_state.cart.append({**selected_product, "qty": qty})
        st.rerun()

# Cart Management & Payment
if st.session_state.cart and not st.session_state.show_receipt:
    st.divider()
    subtotal = 0
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        c1.write(f"**{item['name']}**")
        qty = c2.number_input("Qty", 1, 99, item['qty'], key=f"q_{item['id']}")
        st.session_state.cart[i]['qty'] = qty
        row_total = float(item['selling_price']) * qty
        c3.write(f"{row_total:,.0f} MMK")
        if c4.button("🗑", key=f"del_{item['id']}"):
            st.session_state.cart.pop(i)
            st.rerun()
        subtotal += row_total

    col1, col2 = st.columns(2)
    tax_rate = col1.number_input("Tax %", 0.0, 100.0, 0.0)
    discount = col2.number_input("Total Discount", 0.0, 100000.0, 0.0)
    
    final_total = (subtotal - discount) * (1 + tax_rate / 100)
    st.markdown(f"### Grand Total: {final_total:,.0f} MMK")

    # --- Payment System ---
    st.divider()
    st.subheader("💳 Payment Details")
    payment_method = st.radio("Payment Method", ["Cash", "Card", "Mobile Banking", "Credit", "Installment"])
    
    amount_given = final_total
    change_due = 0.0
    if payment_method == "Cash":
        amount_given = st.number_input("Amount Received (ပေးငွေ)", min_value=0.0, value=float(final_total))
        change_due = max(0, amount_given - final_total)
        st.info(f"💰 Change to return: {change_due:,.0f} MMK")

    if st.button("✅ Confirm Sale", type="primary"):
        if payment_method == "Cash" and amount_given < final_total:
            st.error("❌ ပေးငွေ မလုံလောက်ပါ။")
        else:
            prepared_cart = [{"id": i["id"], "qty": int(i["qty"]), "selling_price": float(i["selling_price"])} for i in st.session_state.cart]
            res = checkout_sale_rpc(prepared_cart, float(final_total), payment_method)
            
            if res and isinstance(res, dict) and res.get("success"):
                st.session_state.sale_data = {
                    "receipt_no": res.get("receipt_no"),
                    "total": final_total,
                    "method": payment_method,
                    "change": change_due,
                    "timestamp": get_mst_now()
                }
                st.session_state.show_receipt = True
# Receipt Module (ယခင်နေရာတွင် အောက်ပါအတိုင်း အစားထိုးပါ)
if st.session_state.show_receipt:
    data = st.session_state.sale_data
    st.success(f"✅ Sale Successful! Receipt: {data.get('receipt_no', 'N/A')}")
    
    # .get() ကို အသုံးပြု၍ KeyError မတက်အောင် ကာကွယ်ခြင်း
    method = data.get('method', 'N/A')
    change = data.get('change', 0.0)
    
    st.write(f"**Method:** {method} | **Change:** {change:,.0f} MMK")
    
    if st.button("🔄 New Sale"):
        st.session_state.cart = []
        st.session_state.sale_data = None
        st.session_state.show_receipt = False
        st.rerun()

