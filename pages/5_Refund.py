# ==============================================================================
# pages/5_Refund.py
# ERP ENTERPRISE REFUND SYSTEM v4.7 (Robust Version)
# ==============================================================================

import streamlit as st
from database import db

st.set_page_config(page_title="Refund System", layout="wide")

st.title("↩️ Refund System (ERP Mode)")

# ==========================================
# SESSION INITIALIZATION
# ==========================================
if "selected_sale" not in st.session_state:
    st.session_state.selected_sale = None
if "refund_cart" not in st.session_state:
    st.session_state.refund_cart = []

# ==========================================
# SEARCH SALE
# ==========================================
sale_id = st.text_input("🔍 Enter Sale ID", key="refund_sale_id")

if st.button("Search Sale", key="btn_search_sale"):
    if not sale_id or not sale_id.isdigit():
        st.warning("Please enter a valid Numeric Sale ID")
    else:
        try:
            # 1. Fetch Sale with connection check
            response = db().table("sales").select("*").eq("id", int(sale_id)).maybe_single().execute()
            
            if response is None:
                st.error("Database connection error or timeout.")
            elif not response.data:
                st.error("Sale not found.")
            else:
                sale = response.data
                
                # 2. Fetch Items
                items_resp = db().table("sale_items").select("*").eq("sale_id", int(sale_id)).execute()
                sale["items"] = items_resp.data if items_resp and items_resp.data else []

                st.session_state.selected_sale = sale
                st.session_state.refund_cart = []
                st.rerun()
                
        except Exception as e:
            st.error(f"Search Error: {e}")

# ==========================================
# REFUND DISPLAY
# ==========================================
sale = st.session_state.selected_sale

if sale:
    st.divider()
    st.subheader(f"Sale ID : {sale.get('id')}")
    st.write(f"**Original Total:** {sale.get('total', 0):,.0f} MMK")
    st.divider()

    refund_total = 0
    
    # Iterate through sale items
    for item in sale.get("items", []):
        qty_sold = int(item.get("qty", item.get("quantity", 0)))
        price = float(item.get("selling_price", item.get("unit_price", 0)))
        
        col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
        
        with col1: st.write(f"Product ID: {item.get('product_id')}")
        with col2: st.write(f"Sold Qty: {qty_sold}")
        with col3: st.write(f"Price: {price:,.0f}")
        
        with col4:
            qty = st.number_input(f"Refund Qty {item.get('id')}", min_value=0, max_value=qty_sold, 
                                  value=0, key=f"refund_{item.get('id')}")
            
            existing = next((x for x in st.session_state.refund_cart if x["sale_item_id"] == item.get("id")), None)
            
            if qty > 0:
                refund_total += (qty * price)
                if existing:
                    existing["qty"] = int(qty)
                else:
                    st.session_state.refund_cart.append({"sale_item_id": item.get("id"), "qty": int(qty)})
            elif existing:
                st.session_state.refund_cart.remove(existing)

    st.divider()
    st.info(f"### Total Refund Amount : {refund_total:,.0f} MMK")

    reason = st.text_input("Refund Reason")
    cashier_id = st.session_state.get("user_id")

    if st.button("Process Refund", type="primary"):
        if not st.session_state.refund_cart:
            st.error("No items selected for refund")
        else:
            try:
                # Call RPC
                result = db().rpc("refund_sale_rpc", {
                    "p_sale_id": int(sale["id"]),
                    "p_items": st.session_state.refund_cart,
                    "p_reason": reason,
                    "p_cashier_id": cashier_id
                }).execute()
                
                # Check response safely
                # Result.data က dict ဖြစ်နိုင်သလို boolean ဖြစ်နိုင်လို့ အဆင်ပြေအောင် စစ်ထားပါတယ်
                res_data = result.data
                if res_data is True or (isinstance(res_data, dict) and res_data.get("success")):
                    st.success("Refund Completed Successfully 🎉")
                    st.session_state.refund_cart = []
                    st.session_state.selected_sale = None
                    st.rerun()
                else:
                    st.error(f"Refund Failed: {res_data}")
            except Exception as e:
                st.error(f"RPC Error: {e}")
        
