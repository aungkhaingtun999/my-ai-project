import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v8 Smart ERP", layout="wide")

# --- 1. SESSION STATE INITIALIZATION ---
if "cart" not in st.session_state:
    st.session_state.cart = []

# Helpers
def safe_float(v):
    try: return float(v) if v is not None else 0.0
    except: return 0.0

products = get_products() or []
st.title("🛒 POS v8 Smart POS")

# --- 2. SEARCH & ADD TO CART ---
c1, c2 = st.columns(2)
product_options = {f"{p['name']} | {safe_float(p.get('selling_price')):,.0f} MMK": p for p in products}

with c1:
    selected_label = st.selectbox("🔍 Search by Name", options=[""] + list(product_options.keys()), index=0)
with c2:
    code_input = st.text_input("📟 Barcode / SKU Scan", key="barcode_scan")

selected_product = None
if selected_label:
    selected_product = product_options[selected_label]
elif code_input:
    selected_product = next((p for p in products if code_input in [str(p.get('barcode', '')), str(p.get('sku', ''))]), None)

if selected_product:
    st.divider()
    col_d1, col_d2, col_d3 = st.columns([3, 1, 1])
    col_d1.write(f"**{selected_product['name']}**")
    qty = col_d2.number_input("Qty", min_value=1, value=1, key="q_input")
    
    if col_d3.button("➕ Add to Cart", type="primary"):
        cart_item = {
            "id": selected_product["id"],
            "name": selected_product["name"],
            "selling_price": safe_float(selected_product.get("selling_price")),
            "tax_rate": safe_float(selected_product.get("tax_rate", 0)),
            "discount_allowed": bool(selected_product.get("discount_allowed", False)),
            "qty": qty
        }
        
        found = False
        for item in st.session_state.cart:
            if item["id"] == cart_item["id"]:
                item["qty"] += qty
                found = True
        if not found:
            st.session_state.cart.append(cart_item)
        st.rerun()

# --- 3. CART DISPLAY & CALCULATION ---
st.divider()
st.subheader("🧾 Cart")

if st.session_state.cart:
    total_tax = 0
    subtotal = 0
    
    for i, item in enumerate(st.session_state.cart):
        col_c1, col_c2, col_c3, col_c4 = st.columns([4, 2, 2, 1])
        col_c1.write(item["name"])
        item["qty"] = col_c2.number_input("Qty", 1, 99, item["qty"], key=f"q_{i}")
        
        # တွက်ချက်ခြင်း
        tax_rate = safe_float(item.get("tax_rate", 0))
        line_total = item['selling_price'] * item['qty']
        tax_amount = line_total * (tax_rate / 100)
        
        col_c3.write(f"{(line_total + tax_amount):,.0f} MMK")
        if col_c4.button("🗑", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()
            
        subtotal += line_total
        total_tax += tax_amount

    st.markdown(f"### Total: {(subtotal + total_tax):,.0f} MMK")
    
    # --- 4. PAY & PRINT ---
    if st.button("💳 Pay & Print", type="primary"):
        # Data စစ်ဆေးခြင်း
        if not st.session_state.cart:
            st.warning("ခြင်းတောင်း ဗလာဖြစ်နေပါသည်။")
            st.stop()

        # Database ပို့ရန် Data ပြင်ဆင်ခြင်း (Tax & Discount ပါဝင်သည်)
        prepared_cart = []
        for item in st.session_state.cart:
            prepared_cart.append({
                "id": int(item["id"]),
                "qty": int(item["qty"]),
                "selling_price": float(item["selling_price"]),
                "tax_rate": float(item.get("tax_rate", 0)),
                "discount_allowed": bool(item.get("discount_allowed", False))
            })

        # Database သို့ ပို့ခြင်း
        with st.spinner("အရောင်း စာရင်းသွင်းနေသည်..."):
            result = checkout_sale_rpc(prepared_cart, float(subtotal + total_tax), None)
        
        # ရလဒ် စစ်ဆေးခြင်း
        if result and isinstance(result, dict) and result.get("success"):
            st.success("အရောင်း အောင်မြင်ပါသည်။")
            st.session_state.cart = [] # အောင်မြင်မှ ခြင်းတောင်းကို ရှင်းခြင်း
            st.rerun() 
        elif result and isinstance(result, dict) and "error" in result:
            st.error(f"DB Error: {result['error']}")
        else:
            st.error("အရောင်း စာရင်းသွင်းရာတွင် အမှားတစ်ခုခု ဖြစ်နေပါသည်။")
else:
    st.info("ခြင်းတောင်း ဗလာဖြစ်နေပါသည်။")
