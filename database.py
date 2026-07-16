# ==========================================
# database.py (ERP ENTERPRISE WORLD CLASS v6 - FINAL STABLE)
# ==========================================

from supabase import create_client, Client
import streamlit as st
from typing import List, Dict, Any, Optional
from decimal import Decimal, ROUND_HALF_UP
import logging
import uuid 

# Logger Setup
logging.basicConfig(filename="erp_db.log", level=logging.ERROR, format="%(asctime)s %(levelname)s %(message)s")

def log_error(err: Exception):
    logging.error(str(err))
    print("DB ERROR:", err)

@st.cache_resource
def get_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = get_supabase()

def money(value) -> float:
    try: return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    except: return 0.0

# ======================================================
# CHECKOUT ENGINE (CORE FLOW)
# ======================================================

def checkout_sale_rpc(cart: List[Dict[str, Any]], paid_amount: float, cashier_id: Optional[str] = None):
    if not cart:
        return {"error": "ခြင်းတောင်း ဗလာဖြစ်နေပါသည်"}

    try:
        # အရေးကြီးသော ပြင်ဆင်ချက်:
        # cashier_id က 36 character မပြည့်ရင် (သို့) UUID format မဟုတ်ရင် None သို့ အတင်းပြောင်းမည်
        valid_cashier_id = None
        if cashier_id:
            try:
                # UUID အဖြစ် အတည်ပြုခြင်း
                val = uuid.UUID(str(cashier_id))
                valid_cashier_id = str(val)
            except (ValueError, TypeError, AttributeError):
                # Integer သို့မဟုတ် တခြားမမှန်ကန်သော format များအတွက် None သို့ ပြောင်းခြင်း
                valid_cashier_id = None
        
        payload = {
            "p_cart": cart, 
            "p_paid_amount": money(paid_amount),
            "p_cashier_id": valid_cashier_id 
        }
        
        result = supabase.rpc("checkout_sale_rpc", payload).execute()
        
        if not result or not result.data:
            return {"error": "Database မှ တုံ့ပြန်ချက်မရရှိပါ"}
            
        sale_data = result.data
        
        # SQL Function က return အဖြစ် object ထုတ်ပေးသည်ကို စစ်ဆေးခြင်း
        if isinstance(sale_data, dict) and sale_data.get("success"):
            return {
                "success": True, 
                "receipt_no": sale_data.get("receipt_no"),
                "sale_id": sale_data.get("sale_id")
            }
        else:
            return {"error": sale_data.get("error", "Unknown DB Error")}

    except Exception as e:
        log_error(e)
        return {"error": f"Checkout Failed: {str(e)}"}

# ======================================================
# PRODUCTS & RECEIPTS MODULE
# ======================================================

def get_products(active_only: bool = True):
    query = supabase.table("products").select("id, barcode, sku, name, selling_price, tax_rate, discount_allowed, stock, is_active")
    if active_only:
        query = query.eq("is_active", True)
    try:
        return query.execute().data
    except Exception as e:
        log_error(e)
        return []

def get_receipt(receipt_no: str):
    try:
        result = supabase.table("sales").select("*").eq("invoice_no", receipt_no).single().execute()
        return result.data
    except Exception as e:
        log_error(e)
        return None

def get_sale_items(sale_id: str):
    try:
        result = supabase.table("sale_items").select("*").eq("sale_id", sale_id).execute()
        return result.data
    except Exception as e:
        log_error(e)
        return []
        
