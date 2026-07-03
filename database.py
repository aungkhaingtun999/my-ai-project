# ==========================================
# database.py (PRODUCTION ERP POS)
# ==========================================

from supabase import create_client, Client
import streamlit as st

# ==========================
# CONNECTION
# ==========================

@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

supabase = get_supabase()


# ==========================
# SAFE EXECUTOR
# ==========================

def safe_execute(query):
    try:
        return query.execute()
    except Exception as e:
        print("Database Error:", e)
        return None


# ======================================================
# PRODUCTS
# ======================================================

def get_products(active_only=True):
    query = supabase.table("products").select("""
        id,
        barcode,
        sku,
        name,
        purchase_price,
        selling_price,
        stock,
        minimum_stock,
        unit,
        is_active,
        category_id
    """)

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
# INVENTORY
# ======================================================

def add_inventory_log(data: dict):
    return safe_execute(
        supabase.table("inventory_logs").insert(data)
    )


# ======================================================
# RECEIPTS
# ======================================================

def create_receipt(data: dict):
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
# PRINTER HOOK (SAFE)
# ======================================================

def print_receipt_if_available(receipt, items):
    try:
        from utils.thermal_receipt import print_receipt
        print_receipt(receipt, items)
    except Exception as e:
        print("Printer skipped:", e)


# ======================================================
# STOCK VALIDATION (SEPARATE LAYER)
# ======================================================

def validate_stock(cart):
    for item in cart:

        product = supabase.table("products") \
            .select("id, stock, name") \
            .eq("id", item["id"]) \
            .single() \
            .execute()

        if not product.data:
            return False, f"Product not found: {item['name']}"

        if product.data["stock"] < item["qty"]:
            return False, f"Not enough stock: {item['name']}"

    return True, "OK"


# ======================================================
# CHECKOUT ENGINE (ERP SAFE FLOW)
# ======================================================

def checkout_sale_rpc(cart, paid_amount, cashier_id=None):

    # --------------------------
    # VALIDATION
    # --------------------------
    if not cart:
        return {"error": "Cart is empty"}

    total = sum(i["selling_price"] * i["qty"] for i in cart)

    if paid_amount < total:
        return {"error": "Insufficient payment"}

    # --------------------------
    # STOCK CHECK (CLEAN)
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
                "qty": i["qty"],
                "selling_price": i["selling_price"]
            }
            for i in cart
        ],
        "p_paid_amount": paid_amount,
        "p_cashier_id": cashier_id
    }).execute()

    if not result.data:
        return {"error": "Checkout failed (RPC error)"}

    sale = result.data

    sale_id = sale.get("sale_id")
    total = sale.get("total")

    if not sale_id:
        return {"error": "Invalid sale response"}

    # --------------------------
    # RECEIPT
    # --------------------------
    receipt = {
        "receipt_no": f"RCP-{sale_id}",
        "sale_id": sale_id,
        "total": total,
        "paid_amount": paid_amount,
        "change_amount": paid_amount - total
    }

    create_receipt(receipt)

    # --------------------------
    # PRINT
    # --------------------------
    print_receipt_if_available(receipt, cart)

    # --------------------------
    # RESPONSE
    # --------------------------
    return {
        "success": True,
        "sale_id": sale_id,
        "total": total,
        "receipt_no": receipt["receipt_no"]
    }
