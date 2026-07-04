import streamlit as st
from database import get_products, checkout_sale_rpc

st.set_page_config(page_title="POS v8 Smart ERP", layout="wide")

# Helpers
def safe_float(v):
    try: return float(v) if v is not None else 0.0
    except: return 0.0

# Session State
if "cart" not in st.session_state: st.session_state.cart = []

products = get_products() or []
st.title("🛒 POS v8 Smart POS")

# SEARCH SECTION
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

# Add to Cart
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
            "discount_allowed": selected_product.get("discount_allowed", False),
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

# CART SECTION
st.divider()
st.subheader("🧾 Cart")

if st.session_state.cart:
    total_tax = 0
    subtotal = 0
    
    for i, item in enumerate(st.session_state.cart):
        col_c1, col_c2, col_c3, col_c4 = st.columns([4, 2, 2, 1])
        col_c1.write(item["name"])
        item["qty"] = col_c2.number_input("Qty", 1, 99, item["qty"], key=f"q_{i}")
        
        tax_rate = safe_float(item.get("tax_rate", 0))
        line_total = item['selling_price'] * item['qty']
        tax_amount = line_total * (tax_rate / 100)
        
        col_c3.write(f"{(line_total + tax_amount):,.0f} MMK")
        if col_c4.button("🗑", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()
            
        subtotal += line_total
        total_tax += tax_amount

    st.markdown(f"### Subtotal: {subtotal:,.0f} MMK")
    st.markdown(f"### Tax: {total_tax:,.0f} MMK")
    st.markdown(f"## Total: {(subtotal + total_tax):,.0f} MMK")
    
   if st.button("💳 Pay & Print", type="primary"):
        prepared_cart = []
        for item in st.session_state.cart:
            prepared_cart.append({
                "id": int(item["id"]),
                "qty": int(item["qty"]),
                "selling_price": float(item["selling_price"]),
                "tax_rate": float(item.get("tax_rate", 0)),
                "discount_allowed": bool(item.get("discount_allowed", False))
            })

        try:
            # function ကို ခေါ်ခြင်း (parameter ၃ ခုလုံး ထည့်ပါ)
            # database.py ထဲက checkout_sale_rpc ကိုလည်း payload 3 ခုပို့နိုင်အောင် ပြင်ထားဖို့ လိုပါမယ်
            result = checkout_sale_rpc(prepared_cart, float(subtotal + total_tax))
            
            # စစ်ဆေးခြင်း
            if result and hasattr(result, 'error') and result.error:
                st.error(f"DB Error: {result.error}")
            else:
                st.success("အရောင်း အောင်မြင်ပါသည်။")
                st.session_state.cart = []
                st.rerun()
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            else:
                st.success("အရောင်း အောင်မြင်ပါသည်။")
                st.session_state.cart = []
                st.rerun()
        except Exception as e:
            st.error(f"API Error: {str(e)}")
else:
    st.info("ခြင်းတောင်း ဗလာဖြစ်နေပါသည်။")
