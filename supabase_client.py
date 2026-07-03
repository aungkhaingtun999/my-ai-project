from supabase import create_client, Client
import streamlit as st
import logging
import uuid
from datetime import datetime

# =========================
# LOGGING (ERP GRADE)
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# =========================
# CONNECTION SINGLETON
# =========================
@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

supabase = get_supabase()

# =========================
# STANDARD RESPONSE FORMAT
# =========================
def response(success: bool, data=None, error=None, action="UNKNOWN"):
    trace_id = str(uuid.uuid4())[:8]

    if success:
        logging.info(f"[{action}] SUCCESS | trace={trace_id}")
    else:
        logging.error(f"[{action}] FAILED | trace={trace_id} | {error}")

    return {
        "success": success,
        "data": data,
        "error": error,
        "trace_id": trace_id
    }

# =========================
# SAFE EXECUTOR
# =========================
def safe_execute(query, action="DB_ACTION"):
    try:
        result = query.execute()
        return response(True, result.data, None, action)

    except Exception as e:
        return response(False, None, str(e), action)

# =========================
# QUERY HELPER
# =========================
def table(name: str):
    return supabase.table(name)

# ======================================================
# PRODUCTS MODULE
# ======================================================

def get_products(active_only: bool = True):
    q = table("products").select("*")

    if active_only:
        q = q.eq("is_active", True)

    return safe_execute(q.order("name"), "GET_PRODUCTS")


def get_product(product_id: int):
    return safe_execute(
        table("products")
        .select("*")
        .eq("id", product_id)
        .single(),
        "GET_PRODUCT"
    )


def add_product(data: dict):
    return safe_execute(
        table("products").insert(data),
        "ADD_PRODUCT"
    )


def update_product(product_id: int, data: dict):
    return safe_execute(
        table("products")
        .update(data)
        .eq("id", product_id),
        "UPDATE_PRODUCT"
    )


def delete_product(product_id: int):
    return safe_execute(
        table("products")
        .delete()
        .eq("id", product_id),
        "DELETE_PRODUCT"
    )

# ======================================================
# INVENTORY MODULE
# ======================================================

def add_inventory_log(data: dict):
    return safe_execute(
        table("inventory_logs").insert(data),
        "ADD_INVENTORY_LOG"
    )

# ======================================================
# SALES MODULE
# ======================================================

def create_sale(data: dict):
    return safe_execute(
        table("sales").insert(data),
        "CREATE_SALE"
    )


def get_sales(limit: int = 100):
    return safe_execute(
        table("sales")
        .select("*")
        .order("id", desc=True)
        .limit(limit),
        "GET_SALES"
    )

# ======================================================
# RECEIPT MODULE
# ======================================================

def create_receipt(data: dict):
    return safe_execute(
        table("receipts").insert(data),
        "CREATE_RECEIPT"
    )


def get_receipt(receipt_no: str):
    return safe_execute(
        table("receipts")
        .select("*")
        .eq("receipt_no", receipt_no)
        .single(),
        "GET_RECEIPT"
    )

# ======================================================
# RAW ACCESS (ADVANCED ONLY)
# ======================================================

def db():
    """
    Direct Supabase client access (use carefully)
    """
    return supabase