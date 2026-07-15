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
product = product_map[selected_name]
price = float(product.get("selling_price") or 0)
line_total = float(price * qty)

# ၃။ အရောင်းလုပ်ဆောင်ခြင်း
if st.button("Process Sale"):
    try:
        # Invoice နံပါတ်နှင့် အချိန်
        now = datetime.datetime.now()
        invoice_no = f"INV-{now.strftime('%Y%m%d%H%M%S')}"

        # A. အရောင်းခေါင်းစဉ်အသစ်တစ်ခု ဖန်တီးခြင်း (Sales Table)
        # Database Schema အရ မဖြစ်မနေ လိုအပ်သော fields များအားလုံး ထည့်ထားသည်
        sale_header = supabase.table("sales").insert({
            "invoice_no": invoice_no,
            "subtotal": line_total,     # NOT NULL အတွက် ထည့်ပေးရန်
            "total": line_total,        # NOT NULL အတွက် ထည့်ပေးရန်
            "status": "Completed",      # Error ရှောင်ရန် သေချာထည့်ပေးထားသည်
            "created_at": now.isoformat()
        }).execute().data[0]
        
        sale_id = sale_header["id"] 

        # B. ပစ္စည်းအသေးစိတ်ထည့်ခြင်း (Sale_Items Table)
        supabase.table("sale_items").insert({
            "sale_id": sale_id,           
            "product_id": product["id"],  
            "quantity": int(qty),         
            "unit_price": price,          
            "total": line_total           
        }).execute()

        st.success(f"Sale completed successfully! (Invoice: {invoice_no})")
        
        # C. Receipt ပြသခြင်း (အင်္ဂလိပ်/မြန်မာ နှစ်ဘာသာ)
        st.markdown("---")
        st.subheader("🧾 SPORTWORLD Receipt")
        st.write(f"**Invoice No:** {invoice_no}")
        st.write(f"**Date:** {now.strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown("---")
        
        st.write(f"**Item / ပစ္စည်း:** {selected_name}")
        st.write(f"**Qty / အရေအတွက်:** {qty}")
        st.write(f"**Amount / စုစုပေါင်း:** {line_total:,.2f}")
        
        st.markdown("---")
        st.write("ขอบคุณที่ใช้บริการ / ကျေးဇူးတင်ပါသည် / THANK YOU")
        
        if st.button("New Sale"):
            st.rerun()
        
    except Exception as e:
        st.error(f"Error occurred: {e}")

