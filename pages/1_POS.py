import streamlit as st
import time
from database import get_products, checkout_sale_rpc
from auth import is_authenticated
from thermal_receipt import print_thermal
from receipt_pdf import generate_pdf

# 1. Page Config & Security
st.set_page_config(page_title="Enterprise POS", layout="wide")

if not is_authenticated():
    st.error("ကျေးဇူးပြု၍ Login အရင်ဝင်ပေးပါ။")
    st.stop()

# 2. Professional CSS Styling
st.markdown("""
<style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
    .cart-box { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# 3. Session State Initialization
if "cart" not in st.session_state: st.session_state.cart = []
if "show_receipt" not in st.session_state: st.session_state.show_receipt = False

# 4. Data Loading
@st.cache_data(ttl=60)
def load_products():
    return get_products() or []

products = load_products()

# 5. Smart Search Engine
st.subheader("🛒 Enterprise POS")
search_query = st.text_input("🔍 Search by Name, SKU or Barcode", key="search_in")

selected_product = None
if search_query:
    search_query_lower = search_query.lower()
    matches = [
        p for p in products 
        if search_query_lower in str(p.get('barcode', '')).lower() 
        or search_query_lower in str(p.get('sku', '')).lower()
        or search_query_lower in p['name'].lower()
    ]
    
    if len(matches) == 1:
        selected_product = matches[0]
    elif len(matches) > 1:
        selected_product = st.selectbox("Select product from results:", matches, format_func=lambda x: f"{x['name']} ({x['sku']})")

# 6. Add to Cart Logic
if selected_product:
    qty = st.number_input("Quantity", min_value=1, value=1, key="qty_in")
    if st.button("➕ Add to Cart", type="primary"):
        if qty > selected_product.get('stock', 0):
            st.warning("⚠️ Stock မလုံလောက်ပါ။")
        else:
            existing = next((item for item in st.session_state.cart if item["id"] == selected_product["id"]), None)
            if existing:
                existing["qty"] += qty
            else:
                st.session_state.cart.append({**selected_product, "qty": qty})
            st.rerun()

# 7. Cart Grid & Management
if st.session_state.cart and not st.session_state.show_receipt:
    st.divider()
    st.markdown("### 🛒 Current Cart")
    
    subtotal = 0
    for i, item in enumerate(st.session_state.cart):
        c = st.columns([3, 1, 1, 1])
        c[0].write(f"{item['name']} ({item['sku']})")
        new_qty = c[1].number_input("Qty", 1, 99, item['qty'], key=f"q_{item['id']}")
        item['qty'] = new_qty
        row_total = float(item['selling_price']) * item['qty']
        c[2].write(f"{row_total:,.0f}")
        if c[3].button("🗑", key=f"del_{item['id']}"):
            st.session_state.cart.pop(i)
            st.rerun()
        subtotal += row_total

    st.divider()
    col1, col2 = st.columns(2)
    tax_rate = col1.number_input("Tax %", 0.0, 100.0, 0.0)
    discount = col2.number_input("Total Discount", 0.0, 100000.0, 0.0)
    
    tax_amount = (subtotal - discount) * (tax_rate / 100)
    final_total = subtotal - discount + tax_amount
    
    st.markdown(f"### Grand Total: {final_total:,.0f} MMK")
    
    if st.button("💳 Pay & Print", type="primary"):
        prepared_cart = [{"id": item["id"], "qty": int(item["qty"]), "selling_price": float(item["selling_price"]), "tax_rate": float(item.get("tax_rate", 0))} for item in st.session_state.cart]
        with st.spinner("Processing Sale..."):
            res = checkout_sale_rpc(prepared_cart, final_total, None)
            if res and res.get("success"):
                st.session_state.sale_data = {"cart": st.session_state.cart, "subtotal": subtotal, "discount": discount, "tax": tax_amount, "total": final_total, "receipt_no": res.get("receipt_no")}
                st.session_state.show_receipt = True
                st.rerun()
            else:
                st.error(f"Error: {res.get('error', 'Unknown Error')}")

# 8. Receipt Module
if st.session_state.show_receipt and "sale_data" in st.session_state:
    data = st.session_state.sale_data
    st.success(f"✅ Sale Successful! Receipt: {data['receipt_no']}")
    
    # Receipt Preview Logic here (as previously defined)
    col_p1, col_p2, col_p3 = st.columns(3)
    if col_p1.button("🖨 Print (Thermal)"): print_thermal(data)
    if col_p2.button("📄 Export PDF"): 
        pdf_file = generate_pdf(data)
        st.download_button("Download PDF", pdf_file, "receipt.pdf")
    if col_p3.button("🔄 New Sale"):
        st.session_state.cart = []
        st.session_state.show_receipt = False
        if "sale_data" in st.session_state: del st.session_state.sale_data
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("Enterprise POS v2.0 | Stable")
