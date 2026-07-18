# ==============================================================================
# pages/1_POS.py v4.7.5 - FINAL RECEIPT FIX
# ==============================================================================
import sys
import os
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from database import get_products, checkout_sale_rpc, get_setting, get_default_warehouse_id
from auth import is_authenticated
from language import t, language_selector

# --- Optional Utils ---
try: from utils.thermal_receipt import print_thermal
except: print_thermal = None
try: from utils.receipt_pdf import generate_pdf
except: generate_pdf = None

st.set_page_config(page_title="Enterprise POS", layout="wide")
language_selector()

if not is_authenticated(): st.stop()

# --- 1. Session State Initialization ---
if "cart" not in st.session_state: st.session_state.cart = []
if "show_receipt" not in st.session_state: st.session_state.show_receipt = False
if "processing" not in st.session_state: st.session_state.processing = False
if "sale_data" not in st.session_state: st.session_state.sale_data = None
if "tax_rate" not in st.session_state:
    st.session_state.tax_rate = float(get_setting("default_tax_rate", 0))

warehouse_id = get_default_warehouse_id()
products = get_products(warehouse_id=warehouse_id)

st.title(f"🛒 {t('app.pos_system')}")

# --- 2. Product Search ---
col1, col2 = st.columns(2)
with col1:
    name_search = st.text_input(t("search.product_name"))
with col2:
    sku_search = st.text_input("🔍 Search by SKU/Barcode")

matches = []
if name_search:
    matches = [p for p in products if name_search.lower() in p["name"].lower()]
elif sku_search:
    search = sku_search.lower()
    matches = [p for p in products if search in str(p.get("sku", "")).lower() or search in str(p.get("barcode", "")).lower()]

if matches:
    selected = st.selectbox(t("search.choose"), matches, format_func=lambda x: f"{x.get('sku', '')} - {x['name']} (Stock: {x['stock']})")
    qty = st.number_input(t("cart.qty"), min_value=1, value=1)
    
    if st.button(t("cart.add")):
        current_in_cart = sum(item["qty"] for item in st.session_state.cart if item["id"] == selected["id"])
        if current_in_cart + int(qty) > selected["stock"]:
            st.error(f"Insufficient stock! Available: {selected['stock']}")
        else:
            found = False
            for item in st.session_state.cart:
                if item["id"] == selected["id"]:
                    item["qty"] += int(qty)
                    found = True
                    break
            if not found:
                price = float(selected["selling_price"])
                st.session_state.cart.append({
                    "id": selected["id"], "name": selected["name"],
                    "price": price, "selling_price": price, "qty": int(qty)
                })
            st.rerun()

# --- 3. Checkout UI ---
if st.session_state.cart and not st.session_state.show_receipt:
    st.divider()
    subtotal = sum(i["selling_price"] * i["qty"] for i in st.session_state.cart)
    st.session_state.tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, value=st.session_state.tax_rate, step=0.5)
    discount = st.number_input(t("payment.discount"), min_value=0.0, value=0.0)
    
    tax_amount = round(subtotal * st.session_state.tax_rate / 100, 2)
    total = subtotal + tax_amount - discount
    
    st.write(f"### Total: {total:,.0f} MMK")
    
    payment_map = {"Cash": "cash", "Card": "card", "Mobile": "mobile"}
    payment_code = payment_map[st.radio(t("payment.method"), ["Cash", "Card", "Mobile"])]
    received = st.number_input(t("payment.received"), value=float(total)) if payment_code == "cash" else total

    if st.button(t("payment.confirm"), disabled=st.session_state.processing):
        st.session_state.processing = True
        try:
            cart_payload = [{"id": i["id"], "qty": int(i["qty"]), "selling_price": float(i["selling_price"])} for i in st.session_state.cart]
            
            result = checkout_sale_rpc(
                cart=cart_payload, paid_amount=received, warehouse_id=warehouse_id,
                cashier_id=st.session_state.get("user_id"), payment_method=payment_code,
                tax_rate=st.session_state.tax_rate, discount=discount
            )
            
            if result.get("success"):
                raw_data = result.get("data", {})
                inv = raw_data.get("invoice_no") or raw_data.get("invoice") or "INV-PENDING"
                
                # Receipt Data Structure (Compatible with all engines)
                st.session_state.sale_data = {
                    "invoice_no": inv, "receipt_no": inv,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "cashier": st.session_state.get("username", "Admin"),
                    "cashier_name": st.session_state.get("username", "Admin"),
                    "items": list(st.session_state.cart),
                    "subtotal": subtotal, "discount": discount,
                    "tax_rate": st.session_state.tax_rate,
                    "tax_amount": tax_amount, "tax": tax_amount,
                    "total": total, "grand_total": total,
                    "paid": received, "change": max(0, received - total)
                }
                st.session_state.show_receipt = True
                st.rerun()
            else: raise Exception(result.get("message", "Transaction failed"))
        except Exception as e:
            st.session_state.processing = False
            st.error(str(e))

# --- 4. Receipt Section ---
if st.session_state.show_receipt:
    data = st.session_state.sale_data
    st.success(f"Invoice : {data['invoice_no']}")
    
    col_a, col_b, col_c = st.columns(3)
    if print_thermal and col_a.button("🖨 Print Thermal"): print_thermal(data)
    if generate_pdf and col_b.button("📄 PDF Receipt"): generate_pdf(data)
    if col_c.button("🆕 New Sale"):
        st.session_state.update({"cart": [], "show_receipt": False, "processing": False, "sale_data": None})
        st.rerun()


