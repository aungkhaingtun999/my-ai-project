# ==========================================
# database.py (ERP ENTERPRISE WORLD CLASS v5 - CLEANED)
# ==========================================

from supabase import create_client, Client
import streamlit as st
from typing import List, Dict, Any, Optional
from decimal import Decimal, ROUND_HALF_UP
import logging

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
    """
    World Class Checkout Engine:
    1. Validates input
    2. Calls RPC with correct parameter mapping
    3. Handles receipt and logging
    """
    if not cart:
        return {"error": "ခြင်းတောင်း ဗလာဖြစ်နေပါသည်"}

    # 1. RPC Call (Map parameters precisely to DB Function)
    try:
        # p_cart, p_paid_amount, p_cashier_id (3 parameters)
        payload = {
            "p_cart": cart, 
            "p_paid_amount": money(paid_amount),
            "p_cashier_id": cashier_id
        }
        
        result = supabase.rpc("checkout_sale_rpc", payload).execute()
        
        if not result.data:
            return {"error": "Database returned no response"}
            
        sale_data = result.data
        sale_id = sale_data.get("sale_id") # Database ကနေ ပြန်လာမယ့် ID
        
        # 2. Receipt Creation
        total_amount = money(sale_data.get("total", sum(i["selling_price"] * i["qty"] for i in cart)))
        receipt = {
            "receipt_no": f"RCP-{sale_id}",
            "sale_id": sale_id,
            "total": total_amount,
            "paid_amount": money(paid_amount),
            "change_amount": money(paid_amount - total_amount)
        }
        
        supabase.table("receipts").insert(receipt).execute()
        
        return {"success": True, "sale_id": sale_id, "receipt_no": receipt["receipt_no"]}

    except Exception as e:
        log_error(e)
        return {"error": f"Checkout Failed: {str(e)}"}

# ======================================================
# PRODUCTS MODULE
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
