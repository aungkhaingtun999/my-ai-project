# ==============================================================================
# database.py
# ERP ENTERPRISE v15.0 LTS - PRODUCTION STABLE
# Architecture: Frozen API Layer (Official Enterprise Baseline)
# ==============================================================================

import streamlit as st
import logging
import uuid
import time
from decimal import Decimal, ROUND_HALF_UP
from supabase import create_client, Client
from postgrest.exceptions import APIError

# --- Configuration ---
DEBUG = False 
DEFAULT_PAGE_SIZE = 100
SENSITIVE_KEYS = (
    "password", "token", "access_token", "refresh_token", 
    "secret", "authorization", "api_key", "jwt", "bearer_token"
)

# --- Constants ---
_FIELDS = ["id", "name", "sku", "barcode", "selling_price", "stock", "warehouse_id"]
PRODUCT_FIELDS = ",".join(_FIELDS)

# --- Logging ---
logging.basicConfig(
    filename="erp_db.log", 
    level=logging.ERROR, 
    format="%(asctime)s %(levelname)s %(message)s",
    force=True 
)

def log_error(msg="ERP Database Error", rpc_name=None, payload=None):
    """Structured logging with comprehensive sensitive data masking."""
    def mask_sensitive(data):
        if not isinstance(data, dict): return data
        masked = data.copy()
        for key in masked:
            if any(s_key in key.lower() for s_key in SENSITIVE_KEYS):
                masked[key] = "***MASKED***"
        return masked

    safe_payload = mask_sensitive(payload) if DEBUG else {"keys": list(payload.keys()) if isinstance(payload, dict) else "N/A"}
    extra = f" | RPC={rpc_name} | Payload={safe_payload}" if rpc_name else ""
    logging.exception(f"{msg}{extra}")

# --- Connection Management ---
@st.cache_resource
def get_supabase() -> Client:
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception:
        log_error()
        raise

def db():
    return get_supabase()

def ping_database():
    try:
        db().table("warehouses").select("id").limit(1).execute()
        return True
    except Exception:
        return False

# --- Helpers ---
def money(value):
    try: return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    except Exception:
        log_error(); return 0.0

def validate_uuid(value):
    try: return str(uuid.UUID(str(value)))
    except Exception:
        log_error(); return None

# --- 1. Settings & Core ---
def get_setting(key, default=None):
    try:
        res = db().table("erp_settings").select("value").eq("key", key).maybe_single().execute()
        return res.data.get("value") if res.data else default
    except Exception:
        log_error(); return default

@st.cache_data(ttl=300)
def get_default_warehouse_id():
    try:
        res = db().table("warehouses").select("id").eq("is_active", True).order("id").limit(1).execute()
        return res.data[0]['id'] if res.data else 1
    except Exception:
        log_error(); return 1

# --- 2. POS Module ---
def get_products(warehouse_id=None, offset=0, limit=DEFAULT_PAGE_SIZE):
    try:
        query = db().table("pos_products_view").select(PRODUCT_FIELDS).order("name")
        if warehouse_id is not None: query = query.eq("warehouse_id", int(warehouse_id))
        return query.range(offset, offset + limit - 1).execute().data or []
    except Exception:
        log_error(); return []

def checkout_sale_rpc(cart, paid_amount, warehouse_id=None, cashier_id=None, counter_id=1):
    payload = {
        "p_cart": cart, 
        "p_paid_amount": money(paid_amount), 
        "p_warehouse_id": int(warehouse_id) if warehouse_id is not None else get_default_warehouse_id(),
        "p_counter_id": int(counter_id),
        "p_cashier_id": validate_uuid(cashier_id)
    }
    return execute_rpc("checkout_sale_rpc", payload)

# --- 3. Inventory Module ---
def get_inventory_view(warehouse_id=None, search="", offset=0, limit=DEFAULT_PAGE_SIZE):
    try:
        query = db().table("pos_products_view").select("*")
        if warehouse_id is not None: query = query.eq("warehouse_id", int(warehouse_id))
        
        sanitized_search = search.strip()
        if sanitized_search: 
            query = query.or_(f"name.ilike.%{sanitized_search}%,sku.ilike.%{sanitized_search}%,barcode.ilike.%{sanitized_search}%")
        
        return query.range(offset, offset + limit - 1).execute().data or []
    except Exception:
        log_error(); return []

# --- 4. Core RPC Engine ---
def execute_rpc(rpc_name, payload):
    for attempt in range(3):
        try:
            res = db().rpc(rpc_name, payload).execute()
            raw_data = res.data
            
            if raw_data is None: return {"success": False, "message": "Empty response", "data": None}
            if isinstance(raw_data, list): raw_data = raw_data[0]
            if isinstance(raw_data, dict) and "response_json" in raw_data: raw_data = raw_data["response_json"]
            
            if not isinstance(raw_data, dict):
                return {"success": True, "message": "Operation completed", "data": raw_data}
            
            status = raw_data.get("status") or raw_data.get("success")
            return {
                "success": (status == "success" or status is True),
                "message": raw_data.get("message", "Operation completed"),
                "data": raw_data.get("data", raw_data)
            }
        except (APIError, TimeoutError, ConnectionError, OSError): # Transient errors
            if attempt < 2:
                time.sleep(0.2 * (attempt + 1))
                continue
            log_error(rpc_name=rpc_name, payload=payload)
            return {"success": False, "message": "RPC Connection Failed", "data": None}
        except Exception:
            log_error(rpc_name=rpc_name, payload=payload)
            return {"success": False, "message": "RPC Execution Error", "data": None}

print("DATABASE v15.0 LTS LOADED - OFFICIAL FROZEN BASELINE")
                                         
