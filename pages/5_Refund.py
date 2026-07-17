# ==============================================================================
# pages/5_Refund.py
# ERP ENTERPRISE REFUND SYSTEM v4.5 - STABLE
# ==============================================================================

import streamlit as st
# Project Structure အရ database.py မှ supabase ကိုသာ သုံးရန်
from database import supabase 

st.set_page_config(page_title="Refund System", layout="wide")
st.title("↩️ Refund System (ERP Mode)")

# ==========================================
# SESSION INIT
# ==========================================
if "selected_sale" not in st.session_state: st.session_state.selected_sale = None
if "refund_cart" not in st.session_state: st.session_state.refund_cart = []

# ==========================================
# SEARCH SALE
# ==========================================
sale_id = st.text_input("🔍 Enter Sale ID")

if st.button("Search Sale"):
    if not sale_id:
        st.warning("Please enter sale ID")
    else:
        try:
            # Table name 'sales' ဖြစ်ကြောင်း သေချာပါစေ
            sale_resp = supabase.table("sales").select("*").eq("id", sale_id).single().execute()
            
            if sale_resp.data:
                st.session_state.selected_sale = sale_resp.data
                items_resp = supabase.table("sale_items").select("*").eq("sale_id", sale_id).execute()
                st.session_state.selected_sale["items"] = items_resp.data or []
                st.session_state.refund_cart = [] # Reset cart
                st.success("Sale loaded successfully")
                st.rerun()
            else:
                st.error("Sale not found")
        except Exception as e:
            st.error(f"Search Error: {e}")

# ==========================================
# DISPLAY SALE & ITEMS
# ==========================================
sale = st.session_state.selected_sale

if sale:
    st.subheader(f"Sale ID: {sale['id']}")
    st.write("Total:", f"{sale['total']:,.0f} MMK")
    st.divider()
    
    st.subheader("Items to Refund")
    
    for item in sale["items"]:
        col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
        with col1: st.write(f"Product: {item['product_id']}")
        with col2: st.write(f"Sold Qty: {item['quantity']}")
        with col3: st.write(f"Unit: {item['unit_price']:,.0f}")
        
        with col4:
            # Handle Refund Cart Logic (Anti-Duplicate)
            qty = st.number_input(
                f"Refund Qty ({item['id']})", 
                min_value=0, 
                max_value=item["quantity"], 
                key=f"qty_{item['id']}"
            )
            
            # Logic: Update existing or append new
            existing = next((x for x in st.session_state.refund_cart if x["sale_item_id"] == item["id"]), None)
            
            if qty > 0:
                if existing:
                    existing["qty"] = int(qty)
                else:
                    st.session_state.refund_cart.append({"sale_item_id": item["id"], "qty": int(qty)})
            else:
                if existing:
                    st.session_state.refund_cart = [x for x in st.session_state.refund_cart if x["sale_item_id"] != item["id"]]

    st.divider()
    
    # ==========================================
    # REFUND SECTION
    # ==========================================
    reason = st.text_input("Refund Reason (optional)")
    cashier_id = st.text_input("Cashier ID (optional)")
    
    if st.button("Process Refund", type="primary"):
        if not st.session_state.refund_cart:
            st.error("No items selected for refund")
        else:
            try:
                result = supabase.rpc(
                    "refund_sale_rpc", 
                    {
                        "p_sale_id": int(sale["id"]), 
                        "p_items": st.session_state.refund_cart, 
                        "p_reason": reason, 
                        "p_cashier_id": int(cashier_id) if cashier_id else None
                    }
                ).execute()
                
                # result.data က RPC မှ ပြန်လာသော JSON ဖြစ်သည်
                if result.data and isinstance(result.data, dict) and result.data.get("success"):
                    st.success("Refund Completed Successfully 🎉")
                    st.session_state.refund_cart = []
                    st.session_state.selected_sale = None
                else:
                    st.error(f"Refund failed: {result.data.get('message', 'Unknown Error')}")
            except Exception as e:
                st.error(f"System Error: {e}")
