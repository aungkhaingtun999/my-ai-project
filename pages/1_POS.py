import streamlit as st
import sys
import os

# ==========================================
# 1. PATH FIXING: ဤသည်မှာ သင့် utils ဖိုဒါကို မြင်အောင် လုပ်ပေးခြင်းဖြစ်သည်
# ==========================================
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# ==========================================
# 2. IMPORTS
# ==========================================
from database import get_products, checkout_sale_rpc
from auth import is_authenticated
from utils.thermal_receipt import print_thermal
from utils.receipt_pdf import generate_pdf

# ==========================================
# 3. PAGE CONFIG & SECURITY
# ==========================================
st.set_page_config(page_title="Enterprise POS", layout="wide", page_icon="🛒")

if not is_authenticated():
    st.error("ကျေးဇူးပြု၍ Login အရင်ဝင်ပေးပါ။")
    st.stop()

# ==========================================
# 4. PROFESSIONAL CSS STYLING
# ==========================================
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 5. SESSION STATE
# ==========================================
if "cart" not in st.session_state: st.session_state.cart = []
if "show_receipt" not in st.session_state: st.session_state.show_receipt = False

# ==========================================
# 6. DATA LOADING
# ==========================================
@st.cache_data(ttl=60)
def load_products():
    return get_products() or []

products = load_products()

# ==========================================
# 7. POS UI
# ==========================================
st.subheader("🛒 Enterprise POS")
search_query = st.text_input("🔍 Search by Name, SKU or Barcode")

selected_product = None
if search_query:
    query = search_query.lower()
    matches = [p for p in products if query in str(p.get('barcode', '')).lower() or query in str(p.get('sku', '')).lower() or query in p['name'].lower()]
    if len(matches) == 1:
        selected_product = matches[0]
    elif len(matches) > 1:
        selected_product = st.selectbox("Select product:", matches, format_func=lambda x: f"{x['name']} ({x['sku']})")

if selected_product:
    qty = st.number_input("Quantity", min_value=1, value=1)
    if st.button("➕ Add to Cart", type="primary"):
        if qty > selected_product.get('stock', 0):
            st.warning("⚠️ Stock မလုံလောက်ပါ။")
        else:
            existing = next((item for item in st.session_state.cart if item["id"] == selected_product["id"]), None)
            if existing: existing["qty"] += qty
            else: st.session_state.cart.append({**selected_product, "qty": qty})
            st.rerun()

# ==========================================
# 8. CART MANAGEMENT
# ==========================================
if st.session_state.cart and not st.session_state.show_receipt:
    st.divider()
    subtotal = 0
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        c1.write(f"**{item['name']}**")
        
        # Quantity Update
        item['qty'] = c2.number_input("Qty", 1, 99, item['qty'], key=f"q_{item['id']}")
        
        row_total = float(item['selling_price']) * item['qty']
        c3.write(f"{row_total:,.0f} MMK")
        
        if c4.button("🗑", key=f"del_{item['id']}"):
            st.session_state.cart.pop(i)
            st.rerun()
        subtotal += row_total

    # Tax & Discount
    col1, col2 = st.columns(2)
    tax_rate = col1.number_input("Tax %", 0.0, 100.0, 0.0)
    discount = col2.number_input("Total Discount", 0.0, 100000.0, 0.0)
    final_total = (subtotal - discount) * (1 + tax_rate/100)
    
    st.markdown(f"### Grand Total: {final_total:,.0f} MMK")
    
    if st.button("💳 Pay & Print", type="primary"):
        prepared_cart = [{"id": i["id"], "qty": int(i["qty"]), "selling_price": float(i["selling_price"])} for i in st.session_state.cart]
        res = checkout_sale_rpc(prepared_cart, final_total, None)
        if res and res.get("success"):
            st.session_state.sale_data = {
                "cart": st.session_state.cart, 
                "subtotal": subtotal, 
                "discount": discount, 
                "total": final_total, 
                "receipt_no": res.get("receipt_no")
            }
            st.session_state.show_receipt = True
            st.rerun()

# ==========================================
# 9. RECEIPT MODULE
# ==========================================
if st.session_state.show_receipt and "sale_data" in st.session_state:
    data = st.session_state.sale_data
    st.success(f"✅ Sale Successful! Receipt: {data['receipt_no']}")
    
    col_a, col_b, col_c = st.columns(3)
    if col_a.button("🖨 Print (Thermal)"): print_thermal(data)
    
    # Generate PDF link
    pdf_bytes = generate_pdf(data)
    col_b.download_button("📄 Export PDF", pdf_bytes, f"receipt_{data['receipt_no']}.pdf", "application/pdf")
    
    if col_c.button("🔄 New Sale"):
        st.session_state.cart = []
        st.session_state.show_receipt = False
        st.rerun()
