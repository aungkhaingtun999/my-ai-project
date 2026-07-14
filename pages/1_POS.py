import streamlit as st
import sys
import os

# ==========================================
# 1. PATH FIXING
# ==========================================
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# ==========================================
# 2. IMPORTS
# ==========================================
from database import get_products, checkout_sale_rpc
from auth import is_authenticated
try:
    from utils.thermal_receipt import print_thermal
    from utils.receipt_pdf import generate_pdf
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.stop()

# ==========================================
# 3. PAGE CONFIG & SECURITY
# ==========================================
st.set_page_config(page_title="Enterprise POS", layout="wide", page_icon="🛒")

if not is_authenticated():
    st.error("ကျေးဇူးပြု၍ Login အရင်ဝင်ပေးပါ။")
    st.stop()

st.markdown("<style>.stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }</style>", unsafe_allow_html=True)

# ==========================================
# 4. SESSION STATE
# ==========================================
if "cart" not in st.session_state: st.session_state.cart = []
if "show_receipt" not in st.session_state: st.session_state.show_receipt = False

@st.cache_data(ttl=60)
def load_products():
    return get_products() or []

products = load_products()

# ==========================================
# 5. POS UI - SEARCH & ADD TO CART
# ==========================================
st.subheader("🛒 Enterprise POS")

col_s1, col_s2 = st.columns(2)
name_query = col_s1.text_input("🔍 Search by Name", key="name_search")
code_query = col_s2.text_input("🔍 Search by SKU or Barcode", key="code_search")

selected_product = None

if name_query:
    matches = [p for p in products if name_query.lower() in p['name'].lower()]
    if matches:
        selected_product = st.selectbox("Select product:", matches, format_func=lambda x: f"{x['name']} ({x['sku']})")
elif code_query:
    matches = [p for p in products if code_query.lower() in str(p.get('barcode', '')).lower() or code_query.lower() in str(p.get('sku', '')).lower()]
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
# 6. CART MANAGEMENT
# ==========================================
if st.session_state.cart and not st.session_state.show_receipt:
    st.divider()
    subtotal = 0
    # Copy of cart to avoid modification issues during iteration
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        c1.write(f"**{item['name']}**")
        
        # Quantity Update
        new_qty = c2.number_input("Qty", 1, 99, item['qty'], key=f"q_{item['id']}")
        st.session_state.cart[i]['qty'] = new_qty
        
        row_total = float(item['selling_price']) * new_qty
        c3.write(f"{row_total:,.0f} MMK")
        
        if c4.button("🗑", key=f"del_{item['id']}"):
            st.session_state.cart.pop(i)
            st.rerun()
        subtotal += row_total

    col1, col2 = st.columns(2)
    tax_rate = col1.number_input("Tax %", 0.0, 100.0, 0.0)
    discount = col2.number_input("Total Discount", 0.0, 100000.0, 0.0)
    
    tax_amount = (subtotal - discount) * (tax_rate / 100)
    final_total = (subtotal - discount) + tax_amount
    
    st.markdown(f"### Grand Total: {final_total:,.0f} MMK")
    
    if st.button("💳 Pay & Print", type="primary"):
        # Data Preparation
        prepared_cart = [
            {"id": i["id"], "qty": int(i["qty"]), "selling_price": float(i["selling_price"])} 
            for i in st.session_state.cart
        ]
        cashier_id = str(st.session_state.get("user_id", "Admin"))
        
        # Database Execution
        res = checkout_sale_rpc(prepared_cart, final_total, cashier_id)
        
        if res and res.get("success"):
            # သိမ်းဆည်းမည့် Data
            st.session_state.sale_data = {
                "cart": list(st.session_state.cart), 
                "subtotal": subtotal, 
                "discount": discount, 
                "tax": tax_amount, 
                "total": final_total, 
                "receipt_no": res.get("receipt_no"),
                "cashier_name": st.session_state.get("username", "Admin")
            }
            st.session_state.show_receipt = True
            st.rerun() # Page ကို အချက်အလက်အသစ်နဲ့ ပြန်စခြင်း
        else:
            st.error(f"Checkout Failed: {res.get('error', 'Unknown Error')}")

# ==========================================
# 7. RECEIPT MODULE
# ==========================================
# show_receipt က True ဖြစ်မှ ဤအပိုင်း အလုပ်လုပ်မည်
if st.session_state.show_receipt and "sale_data" in st.session_state:
    data = st.session_state.sale_data
    st.success(f"✅ Sale Successful! Receipt: {data['receipt_no']}")
    
    c_a, c_b, c_c = st.columns(3)
    
    # Thermal Print
    if c_a.button("🖨 Print (Thermal)"):
        print_thermal(data)
    
    # PDF Download
    pdf_bytes = generate_pdf(data)
    c_b.download_button("📄 Export PDF", pdf_bytes, f"receipt_{data['receipt_no']}.pdf", "application/pdf")
    
    # Reset
    if c_c.button("🔄 New Sale"):
        st.session_state.cart = []
        st.session_state.sale_data = None
        st.session_state.show_receipt = False
        st.rerun()

                "total": final_total, 
                "receipt_no": res.get("receipt_no"),
                "cashier_name": st.session_state.get("username", "Admin") # Cashier Name ထည့်ပေးခြင်း
            }
            st.session_state.show_receipt = True
            st.rerun()

# ==========================================
# 7. RECEIPT MODULE
# ==========================================
if st.session_state.show_receipt and "sale_data" in st.session_state:
    data = st.session_state.sale_data
    st.success(f"✅ Sale Successful! Receipt: {data['receipt_no']}")
    
    c_a, c_b, c_c = st.columns(3)
    if c_a.button("🖨 Print (Thermal)"): print_thermal(data)
    
    pdf_bytes = generate_pdf(data)
    c_b.download_button("📄 Export PDF", pdf_bytes, f"receipt_{data['receipt_no']}.pdf", "application/pdf")
    
    if c_c.button("🔄 New Sale"):
        st.session_state.cart = []
        st.session_state.show_receipt = False
        st.rerun()
