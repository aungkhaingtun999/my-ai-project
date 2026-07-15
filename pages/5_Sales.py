import streamlit as st
import datetime
from database import get_supabase

supabase = get_supabase()

st.title("🛒 Sales Management")

# ၁။ Product များထုတ်ယူခြင်း
products = supabase.table("products").select("*").execute().data or []
if not products:
    st.error("No products available")
    st.stop()

product_map = {p["name"]: p for p in products}

# ၂။ Input များ
selected_name = st.selectbox("Select Product", list(product_map.keys()))
qty = st.number_input("Quantity", min_value=1, value=1)

# ငွေပေးချေမှုပုံစံ ရွေးချယ်ခြင်း
payment_method = st.radio("Payment Method", ["Cash", "Card", "Credit"])

product = product_map[selected_name]
price = float(product.get("selling_price") or 0)
line_total = float(price * qty)

# ၃။ အရောင်းလုပ်ဆောင်ခြင်း
if st.button("Process Sale"):
    try:
        now = datetime.datetime.now()
        invoice_no = f"INV-{now.strftime('%Y%m%d%H%M%S')}"
        
        # Credit ဆိုရင် 'pending'၊ ကျန်တာ 'paid'
        payment_status = "pending" if payment_method == "Credit" else "paid"

        # A. အရောင်းခေါင်းစဉ် (Sales Table)
        sale_header = supabase.table("sales").insert({
            "invoice_no": invoice_no,
            "subtotal": line_total,
            "total": line_total,
            "payment_method": payment_method,
            "payment_status": payment_status,
            "status": "Completed",
            "created_at": now.isoformat()
        }).execute().data[0]
        
        sale_id = sale_header["id"] 

        # B. ပစ္စည်းအသေးစိတ် (Sale_Items Table)
        supabase.table("sale_items").insert({
            "sale_id": sale_id,           
            "product_id": product["id"],  
            "quantity": int(qty),         
            "unit_price": price,          
            "total": line_total           
        }).execute()

        st.success(f"Sale completed! (Invoice: {invoice_no})")
        
        # C. Receipt ပြသခြင်း
        st.markdown("---")
        st.subheader("🧾 SPORTWORLD Receipt")
        st.write(f"**Invoice No:** {invoice_no}")
        st.write(f"**Payment Method:** {payment_method}")
        st.write(f"**Status:** {payment_status.upper()}")
        st.markdown("---")
        
        st.write(f"**Item:** {selected_name}")
        st.write(f"**Qty:** {qty}")
        st.write(f"**Total Amount:** {line_total:,.2f}")
        
        st.markdown("---")
        st.write("ขอบคุณที่ใช้บริการ / ကျေးဇူးတင်ပါသည် / THANK YOU")
        
        if st.button("New Sale"):
            st.rerun()
        
    except Exception as e:
        st.error(f"Error occurred: {e}")
        
