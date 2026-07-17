# ==========================================
# database.py (ERP ENTERPRISE v14.5 - STABLE)
# ==========================================

import streamlit as st
import logging
import uuid
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional
from supabase import create_client, Client

# Logging Setup
logging.basicConfig(filename="erp_db.log", level=logging.ERROR, format="%(asctime)s %(levelname)s %(message)s")

def log_error(err: Exception):
    logging.error(f"Error: {str(err)}")

@st.cache_resource
def get_supabase() -> Client:
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception as e:
        st.error("Supabase Credentials မတွေ့ရှိပါ။ st.secrets ကို စစ်ဆေးပေးပါ။")
        raise e

# Lazy Loading Pattern
def db() -> Client:
    return get_supabase()

def money(value) -> float:
    try: return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    except: return 0.0

def validate_uuid(value):
    try: return str(uuid.UUID(str(value)))
    except: return None

# ==========================================
# DATA FETCHERS
# ==========================================

def get_products(active_only=True):
    try:
        query = db().table("products").select("id, barcode, sku, name, purchase_price, selling_price, stock, is_active")
        if active_only: query = query.eq("is_active", True)
        return query.execute().data or []
    except Exception as e: 
        log_error(e)
        return []

def get_suppliers():
    try: return db().table("suppliers").select("id,name,phone").execute().data or []
    except Exception as e: 
        log_error(e)
        return []

def get_warehouses():
    try:
        return db().table("warehouses").select("id, code, name, branch").eq("is_active", True).execute().data or []
    except Exception as e: 
        log_error(e)
        return []

# ==========================================
# RPC & AUDIT LOG
# ==========================================

def purchase_receive_rpc(p_id: int, s_id: int, w_id: int, qty: int, price: float, notes="", uid=None):
    payload = {
        "p_product_id": p_id, "p_supplier_id": s_id, "p_warehouse_id": w_id, 
        "p_qty": qty, "p_price": money(price), "p_notes": notes, "p_created_by": validate_uuid(uid)
    }
    try:
        res = db().rpc("purchase_receive_rpc", payload).execute()
        return res.data
    except Exception as e:
        log_error(e)
        return {"success": False, "message": str(e)}

def transfer_stock_rpc(p_id: int, from_w: int, to_w: int, qty: int, uid: str):
    try:
        res = db().rpc("transfer_stock_rpc", {
            "p_product_id": p_id, "p_from_w": from_w, "p_to_w": to_w, "p_qty": qty, "p_user_id": validate_uuid(uid)
        }).execute()
        return res.data
    except Exception as e:
        log_error(e)
        return {"success": False, "message": str(e)}

def create_audit_log(user_id, action, details):
    try:
        res = db().table("audit_logs").insert({
            "user_id": validate_uuid(user_id),
            "action": action,
            "details": details
        }).execute()
        return {"success": True, "data": res.data}
    except Exception as e:
        log_error(e)
        return {"success": False, "message": str(e)}

print("DATABASE v14.5 IMPORT SUCCESS")
