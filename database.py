# ==============================================================================
# database.py v15.2.5 LTS - IMPORT DEBUGGING VERSION
# ==============================================================================

print("DATABASE.PY START LOADING")

import streamlit as st
import logging
import uuid
import time
import json
from decimal import Decimal, ROUND_HALF_UP
from supabase import create_client, Client

try:
    from postgrest.exceptions import APIError
except ImportError:
    APIError = Exception

# --- Config ---
DEBUG = False
DEFAULT_PAGE_SIZE = 100
SENSITIVE_KEYS = ("password", "token", "secret", "authorization", "api_key", "jwt")
PRODUCT_FIELDS = "id,name,sku,barcode,selling_price,stock,warehouse_id,available_qty"

# --- Logging ---
logging.basicConfig(filename="erp_db.log", level=logging.ERROR, format="%(asctime)s %(levelname)s %(message)s", force=True)

def log_error(msg="ERP Database Error", rpc_name=None, payload=None, exception=None):
    safe_payload = {k: ("***" if any(s in k.lower() for s in SENSITIVE_KEYS) else v) for k, v in payload.items()} if isinstance(payload, dict) else payload
    logging.error(f"{msg} | RPC={rpc_name} | PAYLOAD={safe_payload} | ERROR={exception}")

# --- Connection ---
@st.cache_resource
def get_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def db(): return get_supabase()

# --- Helpers ---
def money(value):
    try: return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    except: return 0.0

def validate_uuid(value):
    if not value: return None
    try: return str(uuid.UUID(str(value)))
    except: return None

# --- ERP Settings ---
def get_setting(key, default=None):
    try:
        res = db().table("erp_settings").select("value").eq("key", key).maybe_single().execute()
        return res.data.get("value") if res.data else default
    except Exception as e:
        log_error(msg="get_setting failed", exception=e)
        return default

# --- Warehouse & Products ---
@st.cache_data(ttl=300)
def get_default_warehouse_id():
    try:
        res = db().table("warehouses").select("id").eq("is_active", True).order("id").limit(1).execute()
        return res.data[0]["id"] if res.data else 1
    except Exception as e:
        log_error(msg="Warehouse load failed", exception=e)
        return 1

def get_products(warehouse_id=None, offset=0, limit=DEFAULT_PAGE_SIZE):
    try:
        query = db().table("pos_products_view").select(PRODUCT_FIELDS).order("name")
        if warehouse_id is not None:
            query = query.eq("warehouse_id", int(warehouse_id))
        return query.range(offset, offset + limit - 1).execute().data or []
    except Exception as e:
        log_error(msg="get_products failed", exception=e)
        return []

# --- POS Checkout RPC ---
def checkout_sale_rpc(cart, paid_amount, warehouse_id=None, cashier_id=None, counter_id=1, payment_method="cash", tax_rate=0, discount=0):
    p_amount = money(paid_amount)
    if p_amount <= 0:
        return {"success": False, "message": "Invalid payment amount", "data": None}
    
    payload = {
        "p_cart": cart, 
        "p_paid_amount": p_amount, 
        "p_warehouse_id": int(warehouse_id) if warehouse_id is not None else get_default_warehouse_id(),
        "p_cashier_id": validate_uuid(cashier_id),
        "p_counter_id": int(counter_id),
        "p_payment_method": str(payment_method).lower(),
        "p_tax_rate": money(tax_rate),
        "p_discount": money(discount)
    }
    return execute_rpc("checkout_sale_rpc", payload)

# --- RPC Engine ---
def execute_rpc(rpc_name, payload):
    last_error = None
    for attempt in range(3):
        try:
            response = db().rpc(rpc_name, payload).execute()
            raw = response.data
            
            if raw is None: return {"success": False, "message": "Empty RPC response", "data": None}
            if isinstance(raw, str):
                try: raw = json.loads(raw)
                except: return {"success": False, "message": f"Malformed JSON: {raw}", "data": None}
            
            if isinstance(raw, list): raw = raw[0] if raw else {}
            if isinstance(raw, dict) and "response_json" in raw: raw = raw["response_json"]
            
            if isinstance(raw, dict):
                success = raw.get("success") is True or str(raw.get("status")).lower() in ("success", "completed", "ok")
                return {"success": success, "message": raw.get("message", "Operation completed"), "data": raw.get("data", raw)}
            
            return {"success": True, "message": "Operation completed", "data": raw}
            
        except APIError as e:
            last_error = e
            if "function" not in str(e).lower() and "column" not in str(e).lower() and attempt < 2:
                time.sleep(0.5)
                continue
            break
        except Exception as e:
            last_error = e
            if attempt < 2:
                time.sleep(0.5 * (attempt + 1))
                continue
            break

    log_error(msg="RPC Failed", rpc_name=rpc_name, payload=payload, exception=last_error)
    return {"success": False, "message": str(last_error) if last_error else "RPC Failed", "data": None}

print("DATABASE.PY FINISHED LOADING")

