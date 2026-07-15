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

# ၃။ အရောင်းလုပ်ဆောင်ခြင်း
if st.button("Process Sale"):
    try:
        # A. Invoice နံပါတ် အတိုလေး ဖန်တီးခြင်း
        invoice_no = f"INV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        # B. အရောင်းခေါင်းစဉ်အသစ်တစ်ခု ဖန်တီးခြင်း (Sales Table)
        # သင့် Database Schema အရ လိုအပ်သော column များကို ထည့်ပေးထားသည်
        # 'status' ကို ဖြုတ်ပြီး 'invoice_no' ကို ထည့်ထားသည်
        sale_header = supabase.table("sales").insert({
            "invoice_no": invoice_no,
            "total": float(price * qty),
            "created_at": datetime.datetime.now().isoformat()
        }).execute().data[0]
        
        sale_id = sale_header["id"] # ဖန်တီးလိုက်သော sale ၏ ID ကိုယူခြင်း

        # C. ပစ္စည်းအသေးစိတ်ထည့်ခြင်း (Sale_Items Table)
        supabase.table("sale_items").insert({
            "sale_id": sale_id,           
            "product_id": product["id"],  
            "quantity": int(qty),         
            "unit_price": price,          
            "total": float(price * qty)   
        }).execute()

        st.success(f"Sale completed successfully! (Invoice: {invoice_no})")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error occurred: {e}")
        
