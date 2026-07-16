import streamlit as st
from database import supabase # database.py မှ supabase instance ကို import လုပ်ပါ
from auth import is_authenticated

st.set_page_config(page_title="Mobile Inventory", layout="centered", page_icon="📦")

if not is_authenticated():
    st.error("ကျေးဇူးပြု၍ Login အရင်ဝင်ပါ။")
    st.stop()

st.title("📦 Mobile Inventory")

# ===============================
# FORM
# ===============================
with st.form("inventory_form", clear_on_submit=True):
    # Barcode Scan (Text input ပုံစံဖြင့် Camera နဲ့ တွဲသုံးနိုင်သည်)
    barcode = st.text_input("📷 Barcode / SKU")
    name = st.text_input("📝 Product Name")
    
    col1, col2 = st.columns(2)
    purchase_price = col1.number_input("💰 Purchase Price", min_value=0.0, step=100.0)
    selling_price = col2.number_input("💵 Selling Price", min_value=0.0, step=100.0)
    
    stock = st.number_input("📦 Opening Stock", min_value=0, step=1)
    
    # Category နှင့် Supplier ကို နောက်ပိုင်း dropdown ပြောင်းနိုင်သည်
    category = st.text_input("🏷️ Category")
    supplier = st.text_input("🏭 Supplier")
    unit = st.selectbox("Unit", ["pcs", "box", "kg", "pack"])

    submitted = st.form_submit_button("➕ Save Product")

    if submitted:
        if not name or not barcode:
            st.error("Barcode နှင့် Name မဖြစ်မနေလိုအပ်ပါသည်။")
        else:
            try:
                # 1. Barcode ရှိပြီးသားလား စစ်ဆေးခြင်း
                existing = supabase.table("products").select("id").eq("barcode", barcode).execute()
                
                if existing.data:
                    st.warning("⚠️ ဤ Barcode ရှိပြီးသားဖြစ်ပါသည်။ Update လုပ်ရန် လိုအပ်ပါသလား?")
                else:
                    # 2. Insert လုပ်ခြင်း
                    data = {
                        "barcode": barcode,
                        "sku": barcode, # Barcode ကို SKU အဖြစ်ပါ သုံးခြင်း
                        "name": name,
                        "purchase_price": purchase_price,
                        "selling_price": selling_price,
                        "stock": stock,
                        "unit": unit,
                        "is_active": True
                    }
                    supabase.table("products").insert(data).execute()
                    st.success(f"✅ {name} ကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ===============================
# FEATURES NOTE
# ===============================
st.divider()
st.info("""
💡 **Mobile Tips:**
- **Camera Scan:** ဖုန်း Browser ၏ 'Text Input' နေရာကို နှိပ်လိုက်ပါက Keyboard ပေါ်လာပြီး Camera icon (သို့) Barcode scanning tool ကို သုံးနိုင်ပါသည်။
- **Product Photo:** Photo upload feature ကို နောက်အဆင့်တွင် ထည့်သွင်းနိုင်ပါသည်။
""")
