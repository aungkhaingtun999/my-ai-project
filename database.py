from supabase import create_client, Client
import streamlit as st

# ==========================
# Supabase Connection
# ==========================

@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

supabase = get_supabase()

# ==========================
# Helper
# ==========================

def safe_execute(query):
    try:
        return query.execute()
    except Exception as e:
        print("Database Error:", e)
        return None

# ==========================
# PRODUCTS
# ==========================

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

# ==========================
# INVENTORY
# ==========================

def add_inventory_log(data: dict):
    return safe_execute(
        supabase.table("inventory_logs").insert(data)
    )

# ==========================
# RECEIPT
# ==========================

def create_receipt(sale_id, total, paid_amount):

    receipt_no = f"RCP-{sale_id}"

    return safe_execute(
        supabase.table("receipts").insert({
            "sale_id": sale_id,
            "receipt_no": receipt_no,
            "total": total,
            "paid_amount": paid_amount,
            "change_amount": paid_amount - total
        })
    )


def get_receipt(receipt_no):
    return safe_execute(
        supabase.table("receipts")
        .select("*")
        .eq("receipt_no", receipt_no)
        .single()
    )

# ==========================
# THERMAL PRINTER HOOK (OPTIONAL)
# ==========================

def print_receipt_if_needed(receipt, cart):
    """
    This function is SAFE hook.
    If printer module exists → print
    If not → ignore (no crash)
    """

    try:
        from utils.thermal_receipt import print_receipt
        print_receipt(receipt, cart)
    except Exception as e:
        print("Printer not available:", e)

# ==========================
# RPC CHECKOUT (MAIN SYSTEM)
# ==========================

def checkout_sale_rpc(cart, paid_amount, cashier_id=None):

    if not cart:
        return {"error": "Cart is empty"}

    payload = [
        {
            "id": item["id"],
            "qty": item["qty"],
            "selling_price": item["selling_price"]
        }
        for item in cart
    ]

    result = supabase.rpc("checkout_sale_rpc", {
        "p_cart": payload,
        "p_paid_amount": paid_amount,
        "p_cashier_id": cashier_id
    }).execute()

    if not result.data:
        return {"error": "Checkout failed"}

    sale = result.data[0]

    # ==========================
    # RECEIPT CREATE
    # ==========================
    receipt = {
        "receipt_no": f"RCP-{sale['sale_id']}",
        "created_at": "NOW",
        "total": sale["total"],
        "paid_amount": paid_amount,
        "change_amount": paid_amount - sale["total"]
    }

    create_receipt(
        sale["sale_id"],
        sale["total"],
        paid_amount
    )

    # ==========================
    # THERMAL PRINT (AUTO HOOK)
    # ==========================
    print_receipt_if_needed(receipt, cart)

    return {
        "success": True,
        "sale_id": sale["sale_id"],
        "total": sale["total"],
        "receipt_no": receipt["receipt_no"]
    }