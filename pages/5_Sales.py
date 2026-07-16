import streamlit as st
import datetime
from database import get_supabase

# Session State စတင်ခြင်း
if 'sale_processed' not in st.session_state:
    st.session_state.sale_processed = False
    st.session_state.last_invoice = ""
    st.session_state.last_total = 0.0
    st.session_state.last_method = ""
    st.session_state.last_change = 0.0

supabase = get_supabase()

# =========================
# အရောင်းပြီးနောက် Receipt ပြခြင်း
# =========================
if st.session_state.sale_processed:
    st.success("✅ Sale completed successfully!")
    st.subheader("🧾 SPORTWORLD Receipt")
    st.write(f"**Invoice No:** {st.session_state.last_invoice}")
    st.write(f"**Method:** {st.session_state.last_method}")
    st.write(f"**Total Amount:** {st.session_state.last_total:,.2f} MMK")
    if st.session_state.last_method == "Cash":
        st.write(f"**Change Given:** {st.session_state.last_change:,.2f} MMK")
    
    if st.button("New Sale"):
        st.session_state.sale_processed = False
        st.rerun()
    st.stop()

# =========================
# POS UI (Main Screen)
# =========================
st.title("🛒 Enterprise POS")

products = supabase.table("products").select("*").execute().data or []
product_map = {f"{p.get('name', 'Unknown')} ({p.get('sku', '')})": p for p in products}

col_left, col_right = st.columns(2)

with col_left:
    search_query = st.text_input("🔍 Search Product")
    filtered_keys = [k for k in product_map.keys() if search_query.lower() in k.lower()]
    selected_key = st.selectbox("Select product:", filtered_keys)
    qty = st.number_input("Quantity", min_value=1, value=1)
    
    # ငွေပေးချေမှုရွေးချယ်ခြင်း
    payment_method = st.radio("Payment Method", ["Cash", "Card", "Mobile Banking", "Credit", "Installment"])

with col_right:
    st.subheader("📋 Order Summary")
    product = product_map[selected_key]
    price = float(product.get("selling_price") or 0)
    line_total = float(price * qty)
    
    st.write(f"**Item:** {product.get('name')}")
    st.write(f"**Grand Total:** {line_total:,.2f} MMK")
    
    # ဤနေရာတွင် Payment Method အလိုက် Logic ကို သီးသန့်ခွဲထားသည်
    amount_given = 0.0
    change_due = 0.0
    
    if payment_method == "Cash":
        amount_given = st.number_input("Amount Received (ပေးငွေ)", min_value=0.0, value=line_total)
        change_due = max(0, amount_given - line_total)
        st.info(f"💰 Change to return: {change_due:,.2f} MMK")
    else:
        st.info(f"✅ Payment method selected: {payment_method}")
        amount_given = line_total # Cash မဟုတ်လျှင် ပေးငွေသည် total နှင့် ညီသည်

# အရောင်းအတည်ပြုခြင်း
if st.button("Process Sale", type="primary"):
    try:
        # Cash ပေးငွေ လုံလောက်မှုစစ်ဆေးခြင်း
        if payment_method == "Cash" and amount_given < line_total:
            st.error("Error: Insufficient cash provided!")
            st.stop()

        now = datetime.datetime.now()
        invoice_no = f"INV-{now.strftime('%Y%m%d%H%M%S')}"
        payment_status = "pending" if payment_method in ["Credit", "Installment"] else "paid"

        # အရောင်းတင်ခြင်း
        sale_header = supabase.table("sales").insert({
            "invoice_no": invoice_no,
            "subtotal": line_total,
            "total": line_total,
            "payment_method": payment_method,
            "payment_status": payment_status,
            "status": "Completed",
            "created_at": now.isoformat()
        }).execute().data[0]
        
        supabase.table("sale_items").insert({
            "sale_id": sale_header["id"],           
            "product_id": product["id"],  
            "quantity": int(qty),         
            "unit_price": price,          
            "total": line_total           
        }).execute()

        # Session State သို့ ပို့ပေးခြင်း
        st.session_state.sale_processed = True
        st.session_state.last_invoice = invoice_no
        st.session_state.last_total = line_total
        st.session_state.last_method = payment_method
        st.session_state.last_change = change_due if payment_method == "Cash" else 0.0
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
        
