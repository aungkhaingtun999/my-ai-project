import streamlit as st
import datetime
from database import get_supabase

supabase = get_supabase()

st.title("🛒 Enterprise POS")

# ၁။ Product များထုတ်ယူခြင်း
products = supabase.table("products").select("*").execute().data or []
if not products:
    st.error("No products available")
    st.stop()

# Search Feature
search_query = st.text_input("🔍 Search by Name, SKU or Barcode")
filtered_products = [p for p in products if search_query.lower() in p["name"].lower() or search_query.lower() in p.get("sku", "").lower()]

product_map = {f"{p['name']} ({p.get('sku', '')})": p for p in filtered_products}
if not product_map:
    st.warning("No products found matching your search.")
    st.stop()

# ၂။ Input များ
selected_key = st.selectbox("Select product:", list(product_map.keys()))
qty = st.number_input("Quantity", min_value=1, value=1)

# ငွေပေးချေမှုပုံစံများ (Mobile Banking ကို ထပ်ထည့်ထားသည်)
payment_method = st.radio("Payment Method", ["Cash", "Card", "Mobile Banking", "Credit"])

product = product_map[selected_key]
price = float(product.get("selling_price") or 0)
line_total = float(price * qty)

# POS UI Calculation
st.markdown("---")
st.write(f"**Item:** {product['name']}")
st.write(f"**Grand Total:** {line_total:,.2f} MMK")

# ငွေပေးချေမှုစစ်ဆေးခြင်း
if payment_method == "Cash":
    amount_given = st.number_input("Amount Received (ပေးငွေ)", min_value=0.0, value=line_total)
    change_due = amount_given - line_total
    st.info(f"💰 Change to return (ပြန်အမ်းငွေ): {max(0, change_due):,.2f} MMK")
else:
    amount_given = line_total # Cash မဟုတ်လျှင် ပေးငွေသည် total နှင့် ညီသည်ဟု သတ်မှတ်သည်
    st.write(f"✅ Selected: {payment_method}")

# ၃။ အရောင်းလုပ်ဆောင်ခြင်း
if st.button("Process Sale"):
    try:
        if payment_method == "Cash" and amount_given < line_total:
            st.error("Error: Insufficient payment received!")
            st.stop()

        now = datetime.datetime.now()
        invoice_no = f"INV-{now.strftime('%Y%m%d%H%M%S')}"
        
        # Credit ဆိုရင် 'pending'၊ ကျန်တာ (Cash, Card, Mobile Banking) ဆိုရင် 'paid'
        payment_status = "pending" if payment_method == "Credit" else "paid"

        # A. အရောင်းခေါင်းစဉ် ဖန်တီးခြင်း
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

        # B. ပစ္စည်းအသေးစိတ်ထည့်ခြင်း
        supabase.table("sale_items").insert({
            "sale_id": sale_id,           
            "product_id": product["id"],  
            "quantity": int(qty),         
            "unit_price": price,          
            "total": line_total           
        }).execute()

        st.success(f"Sale completed successfully! (Invoice: {invoice_no})")
        
        # C. Receipt ပြသခြင်း
        st.markdown("---")
        st.subheader("🧾 SPORTWORLD Receipt")
        st.write(f"**Invoice No:** {invoice_no}")
        st.write(f"**Method:** {payment_method} | **Status:** {payment_status.upper()}")
        st.write(f"**Total Amount:** {line_total:,.2f} MMK")
        
        if payment_method == "Cash":
            st.write(f"**Change Given:** {max(0, change_due):,.2f} MMK")
        
        st.markdown("---")
        st.write("ขอบคุณที่ใช้บริการ / ကျေးဇူးတင်ပါသည် / THANK YOU")
        
    except Exception as e:
        st.error(f"Error occurred: {e}")
        
