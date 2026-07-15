import streamlit as st
import datetime
from database import get_supabase

# Session State စတင်ခြင်း
if 'sale_processed' not in st.session_state:
    st.session_state.sale_processed = False

supabase = get_supabase()

st.title("🛒 Enterprise POS")

# ၁။ Product များထုတ်ယူခြင်း
products = supabase.table("products").select("*").execute().data or []
if not products:
    st.error("No products available")
    st.stop()

# Search Feature
search_query = st.text_input("🔍 Search by Name, SKU or Barcode")
filtered_products = [
    p for p in products 
    if search_query.lower() in str(p.get("name", "")).lower() 
    or search_query.lower() in str(p.get("sku", "")).lower()
]

if not filtered_products:
    st.warning("No products found.")
    st.stop()

product_map = {f"{p.get('name', 'Unknown')} ({p.get('sku', '')})": p for p in filtered_products}

# ၂။ Input များ
selected_key = st.selectbox("Select product:", list(product_map.keys()))
qty = st.number_input("Quantity", min_value=1, value=1)
payment_method = st.radio("Payment Method", ["Cash", "Card", "Mobile Banking", "Credit"])

product = product_map[selected_key]
price = float(product.get("selling_price") or 0)
line_total = float(price * qty)

# POS UI Calculation
st.markdown("---")
st.write(f"### 📋 Order Summary")
st.write(f"**Item:** {product.get('name', 'N/A')}")
st.write(f"**Grand Total:** {line_total:,.2f} MMK")

# ငွေပေးချေမှု စစ်ဆေးခြင်း
amount_given = line_total
if payment_method == "Cash":
    amount_given = st.number_input("Amount Received (ပေးငွေ)", min_value=0.0, value=line_total)
    change_due = amount_given - line_total
    st.info(f"💰 Change to return (ပြန်အမ်းငွေ): {max(0, change_due):,.2f} MMK")

# ၃။ အရောင်းလုပ်ဆောင်ခြင်း
if st.button("Process Sale"):
    try:
        if payment_method == "Cash" and amount_given < line_total:
            st.error("Error: Insufficient payment received!")
            st.stop()

        now = datetime.datetime.now()
        invoice_no = f"INV-{now.strftime('%Y%m%d%H%M%S')}"
        payment_status = "pending" if payment_method == "Credit" else "paid"

        # A. အရောင်းခေါင်းစဉ်
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

        # B. ပစ္စည်းအသေးစိတ်
        supabase.table("sale_items").insert({
            "sale_id": sale_id,           
            "product_id": product["id"],  
            "quantity": int(qty),         
            "unit_price": price,          
            "total": line_total           
        }).execute()

        # အောင်မြင်ကြောင်းပြပြီး Session State ပြောင်းလဲခြင်း
        st.session_state.sale_processed = True
        st.session_state.last_invoice = invoice_no
        st.session_state.last_total = line_total
        st.rerun() # UI အသစ်ပြန်ဖြစ်အောင် လုပ်ခြင်း
        
    except Exception as e:
        st.error(f"Error occurred: {e}")

# ၄။ အရောင်းပြီးနောက် Receipt ပြခြင်း
if st.session_state.sale_processed:
    st.success(f"Sale completed successfully!")
    st.markdown("---")
    st.subheader("🧾 SPORTWORLD Receipt")
    st.write(f"**Invoice No:** {st.session_state.last_invoice}")
    st.write(f"**Total Amount:** {st.session_state.last_total:,.2f} MMK")
    st.write("ขอบคุณที่ใช้บริการ / ကျေးဇူးတင်ပါသည် / THANK YOU")
    
    if st.button("New Sale"):
        st.session_state.sale_processed = False
        st.rerun()
        
