# ==========================================
# database.py (ERP ENTERPRISE WORLD CLASS v5)
# ==========================================

from supabase import create_client, Client
import streamlit as st
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP
import time
import logging
import json

# checkout_sale_rpc ထဲမှာ execute မလုပ်ခင် ဒီလိုလုပ်ပါ
def checkout_sale_rpc(prepared_cart, paid_amount):
    # Data ထဲမှာ float တစ်ခုမှ မကျန်အောင် အဓိက force လုပ်တာပါ
    clean_data = []
    for item in prepared_cart:
        clean_data.append({
            "id": int(item["id"]),
            "qty": int(item["qty"]),
            "selling_price": float(item["selling_price"])
        })
    
    # postgrest-py မှာ json ပို့တဲ့အခါ ဒီလို သေချာပို့ပေးပါ
    return supabase.rpc("your_rpc_name", {
        "cart_items": clean_data, # List of dict ကို တိုက်ရိုက်ပို့ပါ
        "paid_amount": float(paid_amount)
    }).execute()

# ======================================================
# LOGGER (PRODUCTION DEBUG SAFE)
# ======================================================

logging.basicConfig(
    filename="erp_db.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s"
)

def log_error(err: Exception):
    logging.error(str(err))
    print("DB ERROR:", err)


# ======================================================
# CONNECTION LAYER (SINGLETON)
# ======================================================

@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

supabase = get_supabase()


# ======================================================
# SAFE EXECUTION (WITH RETRY)
# ======================================================

def safe_execute(query, retries: int = 2):
    """
    ERP SAFE EXECUTOR:
    - retries on failure
    - logs error
    """
    for attempt in range(retries + 1):
        try:
            res = query.execute()
            return res.data
        except Exception as e:
            log_error(e)
            if attempt < retries:
                time.sleep(0.5)
                continue
            return None


# ======================================================
# MONEY ENGINE (100% ERP SAFE PRECISION)
# ======================================================

def money(value) -> float:
    try:
        return float(
            Decimal(str(value)).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )
        )
    except:
        return 0.0


# ======================================================
# PRODUCTS MODULE
# ======================================================

def get_products(active_only: bool = True):
    query = supabase.table("products").select(
        "id, barcode, sku, name, purchase_price, selling_price, stock, minimum_stock, unit, is_active, category_id"
    )

    if active_only:
        query = query.eq("is_active", True)

    return safe_execute(query.order("name"))


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
# STOCK VALIDATION (STRICT)
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

        db_stock = money(product.data["stock"])
        qty = money(item.get("qty"))

        if db_stock < qty:
            return False, f"Not enough stock: {product.data.get('name')}"

    return True, "OK"


# ======================================================
# CHECKOUT ENGINE (WORLD CLASS CORE FLOW)
# ======================================================

# database.py အတွင်းရှိ function
def checkout_sale_rpc(cart_data, paid_amount):
    # data ကို list အဖြစ်ပို့တာထက် dict အဖြစ် ပို့တာ ပိုကောင်းပါတယ်
    payload = {
        "cart_items": cart_data,
        "paid_amount": float(paid_amount)
    }
    # .execute() မလုပ်ခင် ဒီ payload ကို print ထုတ်ကြည့်နိုင်ပါတယ်
    # print(payload) 
    return supabase.rpc("your_rpc_function_name", payload).execute()
    # --------------------------
    # CART VALIDATION
    # --------------------------
    if not cart:
        return {"error": "Cart is empty"}

    # --------------------------
    # TOTAL CALCULATION (PRECISION SAFE)
    # --------------------------
    total = sum(
        money(i.get("selling_price")) * money(i.get("qty"))
        for i in cart
    )

    paid_amount = money(paid_amount)

    if paid_amount < total:
        return {"error": "Insufficient payment"}

    # --------------------------
    # STOCK CHECK
    # --------------------------
    ok, msg = validate_stock(cart)
    if not ok:
        return {"error": msg}

    # --------------------------
    # RPC CALL
    # --------------------------
    result = supabase.rpc("checkout_sale_rpc", {
        "p_cart": [
            {
                "id": i["id"],
                "qty": money(i["qty"]),
                "selling_price": money(i["selling_price"])
            }
            for i in cart
        ],
        "p_paid_amount": paid_amount,
        "p_cashier_id": cashier_id
    }).execute()

    if not result.data:
        return {"error": "Checkout failed (RPC empty response)"}

    sale = result.data
    sale_id = sale.get("sale_id")

    if not sale_id:
        return {"error": "Invalid DB response"}

    db_total = money(sale.get("total", total))

    # --------------------------
    # RECEIPT
    # --------------------------
    receipt = {
        "receipt_no": f"RCP-{sale_id}",
        "sale_id": sale_id,
        "total": db_total,
        "paid_amount": paid_amount,
        "change_amount": money(paid_amount - db_total)
    }

    create_receipt(receipt)

    # --------------------------
    # OPTIONAL PRINT (SAFE HOOK)
    # --------------------------
    try:
        from utils.thermal_receipt import print_receipt
        print_receipt(receipt, cart)
    except Exception as e:
        log_error(e)

    # --------------------------
    # RESPONSE
    # --------------------------
    return {
        "success": True,
        "sale_id": sale_id,
        "total": db_total,
        "receipt_no": receipt["receipt_no"]
    }
