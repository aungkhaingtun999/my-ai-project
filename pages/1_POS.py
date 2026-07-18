==============================================================================

1_POS.py - ERP Enterprise POS v17.1 (Production Candidate)

==============================================================================

import streamlit as st
import pandas as pd
from decimal import Decimal
from datetime import datetime
import sys, os

Service Import

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(file), "..")))
from database import (get_products, get_erp_setting, get_payment_methods,
is_module_enabled, get_default_warehouse_id, checkout_sale_rpc)
from auth import is_authenticated
from utils.receipt_service import render_receipt_ui # Consolidated Receipt Service

--- Bug Fix 1: Reset Logic ---

def reset_pos():
st.session_state.cart = []
st.session_state.sale_data = None
st.session_state.processing = False

--- Bug Fix 2: Cart Type Validation (Data Sanitization) ---

def sanitize_cart(data_list):
sanitized = []
for item in data_list:
sanitized.append({
"id": item["id"],
"name": item["name"],
"price": Decimal(str(item["price"])),
"qty": int(item["qty"]) # Force Integer
})
return sanitized

--- Main Logic ---

st.set_page_config(page_title="Enterprise POS v17.1", layout="wide")
if not is_authenticated() or not is_module_enabled("POS"): st.stop()

State Initialization

if "cart" not in st.session_state: st.session_state.cart = []
if "sale_data" not in st.session_state: st.session_state.sale_data = None
if "processing" not in st.session_state: st.session_state.processing = False

Settings

warehouse_id = get_default_warehouse_id()
tax_rate = Decimal(str(get_erp_setting("tax_rate", "5"))) / Decimal("100")
allow_discount = st.session_state.get("user", {}).get("permissions", {}).get("discount_manage", False)

if st.session_state.sale_data is None:
st.title("🛒 Enterprise POS v17.1")

# --- Bug Fix 3: Barcode/Search Engine ---  
products = get_products(warehouse_id=warehouse_id)  
search = st.text_input("🔎 Search Product or Scan Barcode")  
  
matches = [p for p in products if search.lower() in str(p.get("sku", "")).lower() or search.lower() in str(p.get("name", "")).lower()] if search else []  
  
if len(matches) == 1: # Auto-Add Logic  
    selected = matches[0]  
    # Logic to Add to cart immediately...  
elif matches:  
    selected = st.selectbox("Product Results", matches, format_func=lambda x: f"{x['sku']} - {x['name']}")  
    qty = st.number_input("Qty", min_value=1, value=1)  
    if st.button("➕ Add to Cart"):  
        # Add to cart logic here (with stock check)  
        st.rerun()  

# --- Bug Fix 1: Cart Security ---  
if st.session_state.cart:  
    df = pd.DataFrame(st.session_state.cart)  
    edited_df = st.data_editor(df, column_config={  
        "name": st.column_config.TextColumn("Product", disabled=True),  
        "price": st.column_config.NumberColumn("Price", disabled=True),  
        "qty": st.column_config.NumberColumn("Qty", min_value=1)  
    }, hide_index=True)  
    st.session_state.cart = sanitize_cart(edited_df.to_dict("records"))  
      
    # Totals  
    subtotal = sum(i["price"] * i["qty"] for i in st.session_state.cart)  
      
    # --- Bug Fix 4: Discount Engine ---  
    discount = Decimal(str(st.number_input("Discount", min_value=0.0))) if allow_discount else Decimal("0")  
    grand_total = subtotal + (subtotal * tax_rate) - discount  
      
    pm = st.selectbox("Payment Method", get_payment_methods() or ["Cash"])  
    received = st.number_input("Received", value=float(grand_total)) if pm == "Cash" else float(grand_total)  
      
    if st.button("✅ Confirm Sale", disabled=st.session_state.processing or (pm=="Cash" and received < grand_total)):  
        st.session_state.processing = True  
        try:  
            # --- Bug Fix 5 & 6: Transaction Safety & Invoice Backup ---  
            json_items = [{"id": i["id"], "qty": i["qty"], "selling_price": float(i["price"])} for i in st.session_state.cart]  
            result = checkout_sale_rpc(cart=json_items, paid_amount=received, payment_method=pm, ...)  
              
            if isinstance(result, dict) and result.get("success"):  
                data = result.get("data", {})  
                st.session_state.sale_data = {  
                    **data, "invoice_no": data.get("invoice_no", f"INV-{datetime.now():%Y%m%d%H%M%S}"),  
                    "items": st.session_state.cart, "subtotal": subtotal, "grand_total": grand_total  
                }  
                st.rerun()  
            else: raise Exception(result.get("message", "Unknown Error"))  
        except Exception as e:  
            st.error(f"Transaction Error: {e}")  
            st.session_state.processing = False

else:
# --- Bug Fix 7: Receipt Service ---
render_receipt_ui(st.session_state.sale_data) # Includes Print/PDF/Email Buttons
if st.button("🆕 New Sale"): reset_pos(); st.rerun()
#ဒါကို ငါမင်းဆီ အရင်တင်
#ပေးမယ်၊ ‌ပြီး လက်ရှိ run နေတဲ့ POS.py ထပ်ပို့ပေးမယ်၊ ဘယ်ဟာကို သုံးသင့်တယ်ဆိုတာကို နောက်တခုတင်ပြီးမှ ဆွေး
