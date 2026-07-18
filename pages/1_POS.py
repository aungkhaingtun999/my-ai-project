==============================================================================

pages/1_POS.py v4.6.8 - PRODUCTION FROZEN RELEASE

==============================================================================

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(file), '..')))

import streamlit as st
from database import (
get_products, checkout_sale_rpc, get_setting, get_default_warehouse_id
)
from auth import is_authenticated
from language import t, language_selector

--- Utilities ---

try: from utils.thermal_receipt import print_thermal
except: print_thermal = None
try: from utils.receipt_pdf import generate_pdf
except: generate_pdf = None

st.set_page_config(page_title="Enterprise POS", layout="wide")
language_selector()

if not is_authenticated():
st.warning(t("auth.login_required"))
st.stop()

--- Session State ---

if "cart" not in st.session_state: st.session_state.cart = []
if "show_receipt" not in st.session_state: st.session_state.show_receipt = False
if "processing" not in st.session_state: st.session_state.processing = False
if "sale_data" not in st.session_state: st.session_state.sale_data = None

warehouse_id = get_default_warehouse_id()
products = get_products(warehouse_id=warehouse_id)

if not products:
st.error(t("app.no_product"))
st.stop()

st.title(f"🛒 {t('app.pos_system')}")

--- Product Search & Add to Cart ---

name_search = st.text_input(t("search.product_name"))
selected = None
if name_search:
matches = [p for p in products if name_search.lower() in p["name"].lower()]
selected = st.selectbox(t("search.choose"), matches, format_func=lambda x: f"{x['name']} (Stock: {x['stock']})") if matches else None

if selected:
qty = st.number_input(t("cart.qty"), min_value=1, value=1)
if st.button(t("cart.add")):
current_cart_qty = sum(item["qty"] for item in st.session_state.cart if item["id"] == selected["id"])
if current_cart_qty + int(qty) > selected["stock"]:
st.error("Insufficient stock!")
else:
found = False
for item in st.session_state.cart:
if item["id"] == selected["id"]:
item["qty"] += int(qty)
found = True
break
if not found:
st.session_state.cart.append({
"id": selected["id"],
"name": selected["name"],
"selling_price": float(selected["selling_price"]),
"qty": int(qty),
"stock": selected["stock"]
})
st.rerun()

--- Checkout Logic (Clean Payload & ERP Standard) ---

if st.session_state.cart and not st.session_state.show_receipt:
subtotal = sum(i["selling_price"] * i["qty"] for i in st.session_state.cart)
tax_rate = float(get_setting("default_tax_rate", 0))
discount = st.number_input(t("payment.discount"), min_value=0.0, value=0.0)
total = subtotal + (subtotal * tax_rate / 100) - discount

st.write(f"### Total: {total:,.0f} MMK")  
  
payment_code = {"cash": "cash", "card": "card", "mobile": "mobile"}[st.radio(t("payment.method"), ["cash", "card", "mobile"])]  
received = st.number_input(t("payment.received"), value=float(total)) if payment_code == "cash" else total  

if st.button(t("payment.confirm"), disabled=st.session_state.processing):  
    st.session_state.processing = True  
    try:  
        # 1. Clean RPC Payload Construction  
        cart_payload = [  
            {"id": i["id"], "qty": int(i["qty"]), "selling_price": float(i["selling_price"])}  
            for i in st.session_state.cart  
        ]  
          
        # 2. RPC with Tax/Discount Sync  
        result = checkout_sale_rpc(  
            cart=cart_payload,  
            paid_amount=received,  
            warehouse_id=warehouse_id,  
            cashier_id=st.session_state.get("user_id"),  
            payment_method=payment_code,  
            tax_rate=tax_rate,    # Sync to DB  
            discount=discount     # Sync to DB  
        )  
          
        if result.get("success"):  
            st.session_state.sale_data = {"invoice_no": result.get("data", {}).get("invoice_no"), "total": total}  
            st.session_state.show_receipt = True  
            st.rerun()  
        else: raise Exception(result.get("message"))  
    except Exception as e:  
        st.session_state.processing = False  
        st.error(str(e))

--- Receipt Section ---

if st.session_state.show_receipt:
st.success(f"Invoice: {st.session_state.sale_data['invoice_no']}")
if print_thermal and st.button("🖨 Print Thermal"): print_thermal(st.session_state.sale_data)
if generate_pdf and st.button("📄 PDF Receipt"): generate_pdf(st.session_state.sale_data)
if st.button(t("receipt.new_sale")):
st.session_state.update({"cart": [], "show_receipt": False, "processing": False, "sale_data": None})
st.rerun()
