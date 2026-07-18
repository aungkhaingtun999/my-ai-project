Import sys
import os
import pandas as pd
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from database import get_products, checkout_sale_rpc, get_setting, get_default_warehouse_id
from auth import is_authenticated
from language import t, language_selector

try: from utils.thermal_receipt import print_thermal
except: print_thermal = None
try: from utils.receipt_pdf import generate_pdf
except: generate_pdf = None

st.set_page_config(page_title="Enterprise POS", layout="wide")
language_selector()
if not is_authenticated(): st.stop()

# --- Session State ---
if "cart" not in st.session_state: st.session_state.cart = []
if "show_receipt" not in st.session_state: st.session_state.show_receipt = False
if "processing" not in st.session_state: st.session_state.processing = False
if "sale_data" not in st.session_state: st.session_state.sale_data = None
if "tax_rate" not in st.session_state: st.session_state.tax_rate = float(get_setting("default_tax_rate", 0))

warehouse_id = get_default_warehouse_id()
products = get_products(warehouse_id=warehouse_id)

st.title(f"🛒 {t('app.pos_system')}")

if not st.session_state.show_receipt:
    # 1. Improved Search Logic
    col1, col2 = st.columns(2)
    with col1: name_search = st.text_input(t("search.product_name"))
    with col2: sku_search = st.text_input("🔍 Search by SKU/Barcode")

    matches = []
    for p in products:
        name_ok = True
        sku_ok = True
        if name_search: name_ok = (name_search.lower() in p["name"].lower())
        if sku_search:
            search = sku_search.lower()
            sku_ok = (search in str(p.get("sku", "")).lower() or search in str(p.get("barcode", "")).lower())
        if name_ok and sku_ok: matches.append(p)

    if matches:
        selected = st.selectbox(t("search.choose"), matches, format_func=lambda x: f"{x.get('sku', '')} - {x['name']} (Stock: {x['stock']})")
        qty = st.number_input(t("cart.qty"), min_value=1, value=1)
        if st.button(t("cart.add")):
            current_qty = sum(item["qty"] for item in st.session_state.cart if item["id"] == selected["id"])
            if current_qty + qty > selected["stock"]: st.error(f"Insufficient Stock! Available {selected['stock']}")
            else:
                found = False
                for item in st.session_state.cart:
                    if item["id"] == selected["id"]:
                        item["qty"] += int(qty)
                        found = True
                        break
                if not found:
                    price = float(selected["selling_price"])
                    st.session_state.cart.append({"id": selected["id"], "name": selected["name"], "sku": selected.get("sku",""), "selling_price": price, "price": price, "qty": int(qty)})
                st.rerun()

    # 2. Cart Table & Remove Logic
    if st.session_state.cart:
        df = pd.DataFrame([{"Product": i["name"], "Qty": i["qty"], "Unit Price": f"{i['selling_price']:,.0f} MMK", "Amount": f"{(i['selling_price']*i['qty']):,.0f} MMK"} for i in st.session_state.cart])
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        cart_subtotal = sum(i["selling_price"] * i["qty"] for i in st.session_state.cart)
        st.write(f"### 🛒 Cart Summary\nProduct Line : **{len(st.session_state.cart)}** | Total Quantity : **{sum(i['qty'] for i in st.session_state.cart)}** | Subtotal : **{cart_subtotal:,.0f} MMK**")

        st.subheader("❌ Remove Item")
        for index, item in enumerate(st.session_state.cart):
            c1, c2 = st.columns([4, 1])
            with c1: st.write(f"{item['name']} x {item['qty']}")
            with c2:
                if st.button("❌", key=f"remove_{index}"):
                    st.session_state.cart.pop(index)
                    st.rerun()

        # Checkout
        st.session_state.tax_rate = st.number_input("Tax Rate (%)", value=st.session_state.tax_rate)
        discount = st.number_input(t("payment.discount"), value=0.0)
        total = cart_subtotal + round(cart_subtotal * st.session_state.tax_rate / 100, 2) - discount
        method = st.selectbox("Payment Method", ["Cash", "Card", "Mobile"])
        received = st.number_input("Received Amount", min_value=float(total), value=float(total)) if method == "Cash" else total

        if st.button(t("payment.confirm"), disabled=st.session_state.processing):
            st.session_state.processing = True
            try:
                result = checkout_sale_rpc(cart=[{"id": i["id"], "qty": int(i["qty"]), "selling_price": float(i["selling_price"])} for i in st.session_state.cart], 
                                           paid_amount=received, warehouse_id=warehouse_id, cashier_id=st.session_state.get("user_id"), 
                                           payment_method=method.lower(), tax_rate=st.session_state.tax_rate, discount=discount)
                
                if result.get("success"):
                    d = result.get("data", {})
                    if isinstance(d, list): d = d[0] if d else {}
                    inv = d.get("invoice_no") or d.get("invoice") or d.get("sale_no") or d.get("receipt_no") or result.get("invoice_no") or result.get("invoice") or result.get("sale_no") or "INV-" + datetime.now().strftime("%Y%m%d%H%M%S")
                    
                    st.session_state.sale_data = {
                        "invoice_no": inv, "invoice": inv, "receipt_no": inv, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "cashier": st.session_state.get("username", "Admin"), "items": list(st.session_state.cart), "cart": list(st.session_state.cart),
                        "subtotal": cart_subtotal, "discount": discount, "tax_rate": st.session_state.tax_rate,
                        "tax_amount": round(cart_subtotal * st.session_state.tax_rate / 100, 2), "total": total, "grand_total": total,
                        "paid": received, "change": max(0, received - total)
                    }
                    st.session_state.show_receipt = True
                    st.session_state.processing = False
                    st.rerun()
                else:
                    st.session_state.processing = False
                    st.error(result.get("message", "Sale Failed"))
            except Exception as e:
                st.session_state.processing = False
                st.error(str(e))

# --- Receipt Preview ---
if st.session_state.show_receipt:
    data = st.session_state.sale_data
    st.info(f"Receipt No : {data['invoice_no']}\n\nDate : {data['date']}\n\nCashier : {data['cashier']}")
    st.subheader("🧾 Receipt Preview")
    for item in data["items"]:
        st.write(f"{item['name']} | Qty: {item['qty']} × {item['selling_price']:,.0f} | Amount: {(item['selling_price']*item['qty']):,.0f} MMK")
    st.divider()
    st.write(f"Subtotal: {data['subtotal']:,.0f} MMK | Tax ({data['tax_rate']}%): {data['tax_amount']:,.0f} MMK\n\n## GRAND TOTAL: {data['grand_total']:,.0f} MMK\n\nPaid: {data['paid']:,.0f} MMK | Change: {data['change']:,.0f} MMK")

    c1,c2,c3 = st.columns(3)
    if c1.button("🖨 Print Receipt"): print_thermal(data) if print_thermal else st.warning("Thermal printer not configured")
    if c2.button("📄 PDF Receipt"): generate_pdf(data) if generate_pdf else st.warning("PDF module missing")
    if c3.button("🆕 New Sale"):
        st.session_state.update({"cart":[], "sale_data":None, "show_receipt":False, "processing":False, "tax_rate": float(get_setting("default_tax_rate", 0))})
        st.rerun()
