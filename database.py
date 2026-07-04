# ==========================================
# database.py (ERP ENTERPRISE v4 - FINAL)
# ==========================================

from supabase import create_client, Client
import streamlit as st
from typing import List, Dict, Any, Optional, Tuple

# ======================================================
# CONNECTION LAYER (SINGLETON SAFE)
# ======================================================

@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

supabase = get_supabase()


# ======================================================
# SAFE EXECUTION WRAPPER
# ======================================================

def safe_execute(query):
    """
    Always returns:
    - result.data (if success)
    - None (if fail)
    """
    try:
        res = query.execute()
        return res.data
    except Exception as e:
        print("DB ERROR:", e)
        return None


# ======================================================
# FLOAT SAFE HELPER (ERP MONEY SAFE)
# ======================================================

def to_float(value, default=0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except:
        return default


# ======================================================
# PRODUCTS MODULE
# ======================================================

def get_products(active_only: bool = True):
    query = supabase.table("products").select(
        "id, barcode, sku, name, purchase_price, selling_price, stock, minimum_stock, unit, is_active, category_id"
    )

    if active_only:
        query = query.eq("is_active", True)

    query = query.order("name")

    return safe_execute(query)


def get_product(product_id: int):
    return safe_execute(
        supabase.table("products")
        .select("*")
        .eq("id", product_id)
        .single()
    )


# ======================================================
# INVENTORY MODULE
# ======================================================

def add_inventory_log(data: Dict[str, Any]):
    return safe_execute(
        supabase.table("inventory_logs").insert(data)
    )


# ======================================================
# RECEIPTS MODULE
# ======================================================

def create_receipt(data: Dict[str, Any]):
    return safe_execute(
        supabase.table("receipts").insert(data)
    )


def get_receipt(receipt_no: str):
    return safe_execute(
        supabase.table("receipts")
        .select("*")
        .eq("receipt_no", receipt_no)
        .single()
    )


# ======================================================
# STOCK VALIDATION (STRICT ERP RULE)
# ======================================================

def validate_stock(cart: List[Dict[str, Any]]) -> Tuple[bool, str]:

    for item in cart:

        product = supabase.table("products") \
            .select("id, stock, name") \
            .eq("id", item["id"]) \
            .single() \
            .execute()

        if not product.data:
            return False, f"Product not found: {item.get('name')}"

        db_stock = to_float(product.data["stock"])
        qty = to_float(item.get("qty"))

        if db_stock < qty:
            return False, f"Not enough stock: {product.data.get('name')}"

    return True, "OK"


# ======================================================
# CHECKOUT ENGINE (CORE ERP FLOW)
# ======================================================

def checkout_sale_rpc(
    cart: List[Dict[str, Any]],
    paid_amount: float,
    cashier_id: Optional[str] = None
):

    # --------------------------
    # CART VALIDATION
    # --------------------------
    if not cart:
        return {"error": "Cart is empty"}

    # --------------------------
    # TOTAL CALCULATION (FLOAT SAFE)
    # --------------------------
    total = sum(
        to_float(i.get("selling_price")) * to_float(i.get("qty"))
        for i in cart
    )

    paid_amount = to_float(paid_amount)

    if paid_amount < total:
        return {"error": "Insufficient payment"}

    # --------------------------
    # STOCK CHECK
    # --------------------------
    ok, msg = validate_stock(cart)
    if not ok:
        return {"error": msg}

    # --------------------------
    # RPC CALL (SUPABASE)
    # --------------------------
    result = supabase.rpc("checkout_sale_rpc", {
        "p_cart": [
            {
                "id": i["id"],
                "qty": to_float(i["qty"]),
                "selling_price": to_float(i["selling_price"])
            }
            for i in cart
        ],
        "p_paid_amount": paid_amount,
        "p_cashier_id": cashier_id
    }).execute()

    if not result.data:
        return {"error": "Checkout failed (RPC returned empty)"}

    sale = result.data

    sale_id = sale.get("sale_id")
    db_total = to_float(sale.get("total", total))

    if not sale_id:
        return {"error": "Invalid sale response from DB"}

    # --------------------------
    # RECEIPT CREATE
    # --------------------------
    receipt = {
        "receipt_no": f"RCP-{sale_id}",
        "sale_id": sale_id,
        "total": db_total,
        "paid_amount": paid_amount,
        "change_amount": paid_amount - db_total
    }

    create_receipt(receipt)

    # --------------------------
    # OPTIONAL PRINT HOOK
    # --------------------------
    try:
        from utils.thermal_receipt import print_receipt
        print_receipt(receipt, cart)
    except Exception as e:
        print("Printer skipped:", e)

    # --------------------------
    # FINAL RESPONSE
    # --------------------------
    return {
        "success": True,
        "sale_id": sale_id,
        "total": db_total,
        "receipt_no": receipt["receipt_no"]
    }
