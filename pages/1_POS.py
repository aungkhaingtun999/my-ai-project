# ==============================================================================
# pages/1_POS.py v4.6.4 - PRODUCTION FREEZE
# ==============================================================================

import streamlit as st
from database import (
    get_products, checkout_sale_rpc, get_setting, get_default_warehouse_id
)
from auth import is_authenticated
from language import t, language_selector

# --- Utilities ---
try: from utils.thermal_receipt import print_thermal
except: print_thermal = None
try: from utils.receipt_pdf import generate_pdf
except: generate_pdf = None

# --- Page Setup ---
st.set_page_config(page_title="Enterprise POS", layout="wide")
language_selector()

if not is_authenticated(): st.stop()

# --- Session State ---
if "cart" not in st.session_state: st.session_state.cart = []
if "show_receipt" not in st.session_state: st.session_state.show_receipt = False
if "processing" not in st.session_state: st.session_state.processing = False
if "sale_data" not in st.session_state: st.session_state.sale_data = None

warehouse_id = get_default_warehouse_id()

# --- Checkout Logic ---
if st.session_state.cart and not st.session_state.show_receipt:
    # ... (Calculation: total) ...
    
    payment_map = {t("payment.cash"): "cash", t("payment.card"): "card", t("payment.mobile"): "mobile"}
    payment_label = st.radio(t("payment.method"), list(payment_map.keys()), horizontal=True)
    payment_code = payment_map[payment_label]
    
    received_amount = total
    if payment_code == "cash":
        received_amount = st.number_input(t("payment.received"), min_value=0.0, value=float(total))
        st.info(f"{t('payment.change')} : {max(0, received_amount - total):,.0f}")

    # Payment Validation Block
    if received_amount < total and payment_code == "cash":
        st.error(t("payment.insufficient"))
        st.stop()

    if st.button(t("payment.confirm"), type="primary", disabled=st.session_state.processing):
        st.session_state.processing = True
        
        try:
            cart_payload = [{"id": i["id"], "qty": int(i["qty"]), "selling_price": float(i["selling_price"])} for i in st.session_state.cart]
            
            # RPC Call with Exception Handling
            result = checkout_sale_rpc(
                cart=cart_payload,
                paid_amount=received_amount,
                warehouse_id=warehouse_id,
                cashier_id=st.session_state.get("user_id"),
                payment_method=payment_code
            )
            
            if result.get("success"):
                st.session_state.sale_data = {"invoice_no": result.get("data", {}).get("invoice_no", "N/A")}
                st.session_state.processing = False # Reset before rerun
                st.session_state.show_receipt = True
                st.rerun()
            else:
                raise Exception(result.get("message", "Checkout failed"))
        
        except Exception as e:
            st.session_state.processing = False
            st.error(f"System Error: {str(e)}")
            st.stop()

# --- Receipt Section ---
if st.session_state.show_receipt:
    # ... (Thermal & PDF Buttons) ...
            
    if st.button(t("receipt.new_sale")):
        # Comprehensive Reset
        st.session_state.update({"cart": [], "show_receipt": False, "processing": False, "sale_data": None})
        st.rerun()
        
