import streamlit as st
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
        # A. အရောင်းခေါင်းစဉ်အသစ်တစ်ခု ဖန်တီးခြင်း (Sales Table)
        # သင့် database တွင် 'status' သို့မဟုတ် 'total' လိုအပ်ပါက ထည့်ပေးပါ
        sale_header = supabase.table("sales").insert({
            "total": price * qty,
            "status": "completed"
        }).execute().data[0]
        
        sale_id = sale_header["id"] # ဖန်တီးလိုက်သော sale ၏ ID ကိုယူခြင်း

        # B. ပစ္စည်းအသေးစိတ်ထည့်ခြင်း (Sale_Items Table)
        supabase.table("sale_items").insert({
            "sale_id": sale_id,           # အထက်ကရလာသော ID
            "product_id": product["id"],  # Product ID
            "quantity": int(qty),         # Quantity
            "unit_price": price,          # Unit Price
            "total": price * qty          # Total (Not Null ဖြစ်၍ မဖြစ်မနေထည့်ရန်)
        }).execute()

        st.success(f"Sale completed successfully! (Receipt ID: {sale_id})")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error occurred: {e}")
        
