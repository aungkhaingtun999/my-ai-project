# ==============================================================================
# pages/1_POS.py
# ERP ENTERPRISE POS v4.5 - WAREHOUSE & PERFORMANCE OPTIMIZED
# ==============================================================================

import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
from database import (
    get_products,
    checkout_sale_rpc,
    get_setting,
    get_default_warehouse
)
from auth import is_authenticated
from language import t, language_selector

# ==============================================================================
# PRINT MODULES
# ==============================================================================
try:
    from utils.thermal_receipt import print_thermal
except ImportError:
    def print_thermal(data): st.warning("Thermal printer utility missing.")

try:
    from utils.receipt_pdf import generate_pdf
except ImportError:
    def generate_pdf(data): st.warning("PDF generator missing.")

# ==============================================================================
# PAGE CONFIG & AUTH
# ==============================================================================
st.set_page_config(page_title="Enterprise POS", page_icon="🛒", layout="wide")
language_selector()

if not is_authenticated():
    st.error(t("auth.login_required"))
    st.stop()

# ==============================================================================
# SESSION STATE & WAREHOUSE CONTEXT
# ==============================================================================
if "cart" not in st.session_state: st.session_state.cart = []
if "show_receipt" not in st.session_state: st.session_state.show_receipt = False
if "sale_data" not in st.session_state: st.session_state.sale_data = None

# Default Warehouse ဆွဲထုတ်ခြင်း
default_wh = get_default_warehouse()
if not default_wh:
    st.error("No active warehouse found. Please contact Admin.")
    st.stop()

warehouse_id = default_wh["id"]
st.sidebar.info(f"📍 Warehouse: {default_wh['name']}")

def get_mst_now():
    return datetime.now(ZoneInfo("Asia/Yangon")).strftime("%Y-%m-%d %H:%M:%S")

# ==============================================================================
# LOAD PRODUCTS (With Warehouse Context)
# ==============================================================================
products = get_products(warehouse_id=warehouse_id) or []
if not products:
    st.warning(t("app.no_product"))
    st.stop()

st.title(f"🛒 {t('app.pos_system')}")

# ==============================================================================
# SEARCH & ADD
# ==============================================================================
c1, c2 = st.columns(2)
name_search = c1.text_input(t("search.product_name"))
barcode_search = c2.text_input(t("search.barcode"))
selected_product = None

if name_search:
    matches = [p for p in products if name_search.lower() in p["name"].lower()]
    if matches: selected_product = st.selectbox(t("search.choose"), matches, format_func=lambda x: f"{x['name']} | Stock: {x['qty']}")
elif barcode_search:
    matches = [p for p in products if barcode_search.lower() in str(p.get("barcode","")).lower()]
    if matches: selected_product = matches[0]

if selected_product:
    qty = st.number_input(t("cart.qty"), min_value=1, value=1)
    current_stock = selected_product.get("qty", 0)
    
    if st.button(t("cart.add"), type="primary"):
        if int(qty) > current_stock:
            st.error(f"Not enough stock! Available: {current_stock}")
        else:
            found = False
            for item in st.session_state.cart:
                if item["id"] == selected_product["id"]:
                    item["qty"] += int(qty)
                    found = True
                    break
            if not found:
                st.session_state.cart.append({
                    "id": selected_product["id"],
                    "name": selected_product["name"],
                    "selling_price": float(selected_product["selling_price"]),
                    "qty": int(qty),
                    "stock": current_stock
                })
            st.rerun()

# ==============================================================================
# CART & CHECKOUT
# ==============================================================================
if st.session_state.cart and not st.session_state.show_receipt:
    st.divider()
    st.subheader(t("cart.title"))
    subtotal = 0
    for index, item in enumerate(st.session_state.cart.copy()):
        a, b, c, d = st.columns([4, 1, 2, 1])
        a.write(item["name"])
        new_qty = b.number_input(t("cart.qty_short"), 1, item["stock"], item["qty"], key=f"qty_{item['id']}")
        st.session_state.cart[index]["qty"] = int(new_qty)
        amount = item["selling_price"] * new_qty
        c.write(f"{amount:,.0f}")
        subtotal += amount
        if d.button("🗑", key=f"del_{item['id']}"):
            st.session_state.cart.pop(index)
            st.rerun()

    default_tax = float(get_setting("default_tax_rate", 0))
    x, y = st.columns(2)
    tax_rate = x.number_input(t("payment.tax_rate"), value=default_tax)
    discount = y.number_input(t("payment.discount"), min_value=0.0)
    tax_amount = (subtotal * tax_rate / 100)
    total = max(0, subtotal - discount + tax_amount)
    
    st.success(f"{t('payment.total')} : {total:,.0f} MMK")
    
    payment_map = {t("payment.cash"): "cash", t("payment.card"): "card", t("payment.mobile"): "mobile"}
    payment_label = st.radio(t("payment.method"), list(payment_map.keys()), horizontal=True)
    payment_code = payment_map[payment_label]
    
    paid = total
    if payment_code == "cash":
        paid = st.number_input(t("payment.received"), min_value=0.0, value=float(total))
        st.info(f"{t('payment.change')} : {max(0, paid-total):,.0f}")

    if st.button(t("payment.confirm"), type="primary"):
        if paid < total:
            st.error(t("error.insufficient"))
        else:
            cart_payload = [{"id": i["id"], "qty": int(i["qty"]), "selling_price": float(i["selling_price"])} for i in st.session_state.cart]
            
            # Warehouse ID ပို့ပေးရမည့်အချက် အရေးကြီးသည်
            result = checkout_sale_rpc(
                cart_payload, 
                paid, 
                warehouse_id, 
                cashier_id=st.session_state.get("user_id")
            )

            if isinstance(result, dict) and result.get("success"):
                st.session_state.sale_data = {
                    "receipt_no": result.get("invoice_no"),
                    "items": st.session_state.cart.copy(),
                    "total": float(total),
                    "timestamp": get_mst_now()
                }
                st.session_state.show_receipt = True
                st.rerun()
            else:
                st.error(f"{t('error.checkout_failed')}: {result.get('message', 'Unknown Error')}")

# ==============================================================================
# RECEIPT
# ==============================================================================
if st.session_state.show_receipt:
    data = st.session_state.sale_data
    st.success(f"Successfully Checkout! No: {data['receipt_no']}")
    if st.button(t("receipt.new_sale")):
        st.session_state.cart = []
        st.session_state.sale_data = None
        st.session_state.show_receipt = False
        st.rerun()
        
