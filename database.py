# ==========================================
# database.py (ERP ENTERPRISE WORLD CLASS v5 - STABLE)
# ==========================================

from supabase import create_client, Client
import streamlit as st
from typing import List, Dict, Any, Optional
from decimal import Decimal, ROUND_HALF_UP
import logging
import uuid # UUID format စစ်ဆေးရန် ထည့်သွင်းခြင်း

# Logger Setup
logging.basicConfig(filename="erp_db.log", level=logging.ERROR, format="%(asctime)s %(levelname)s %(message)s")

def log_error(err: Exception):
    logging.error(str(err))
    print("DB ERROR:", err)

# Singleton Connection
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
        # UUID Format စစ်ဆေးခြင်း (invalid syntax error မတက်စေရန်)
        valid_cashier_id = None
        if cashier_id:
            try:
                # string တစ်ခုကို uuid အဖြစ်ပြောင်းကြည့်ခြင်း
                val = uuid.UUID(str(cashier_id))
                valid_cashier_id = str(val)
            except ValueError:
                # မဟုတ်ပါက None အဖြစ်ထားမည်
                valid_cashier_id = None
        
        # RPC အတွက် Payload
        payload = {
            "p_cart": cart, 
            "p_paid_amount": money(paid_amount),
            "p_cashier_id": valid_cashier_id # စစ်ဆေးပြီးသား ID ကိုသာ ပို့ပါ
        }
        
        # RPC ခေါ်ဆိုခြင်း
        result = supabase.rpc("checkout_sale_rpc", payload).execute()
        
        if not result.data:
            return {"error": "Database မှ တုံ့ပြန်ချက်မရရှိပါ"}
            
        sale_data = result.data
        if not sale_data.get("success"):
            return {"error": sale_data.get("error", "Unknown DB Error")}
            
        return {
            "success": True, 
            "receipt_no": sale_data.get("receipt_no"),
            "sale_id": sale_data.get("sale_id")
        }

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
     
