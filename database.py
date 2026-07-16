# ==========================================
# database.py
# ERP ENTERPRISE WORLD CLASS v7
# FINAL STABLE
# ==========================================

from supabase import create_client, Client
import streamlit as st

from typing import List, Dict, Any, Optional
from decimal import Decimal, ROUND_HALF_UP
import logging
import uuid


# ==========================================
# LOGGING
# ==========================================

logging.basicConfig(
    filename="erp_db.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s"
)


def log_error(err: Exception):
    logging.error(str(err))
    print("DB ERROR:", err)



# ==========================================
# SUPABASE CONNECTION
# ==========================================

@st.cache_resource
def get_supabase() -> Client:

    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


supabase = get_supabase()



# ==========================================
# MONEY FORMAT
# ==========================================

def money(value) -> float:

    try:
        return float(
            Decimal(str(value))
            .quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )
        )

    except Exception:

        return 0.0



# ==========================================
# UUID VALIDATOR
# ==========================================

def validate_uuid(value):

    if not value:
        return None

    try:

        return str(
            uuid.UUID(str(value))
        )

    except Exception:

        return None



# ==========================================
# CHECKOUT RPC
# ==========================================

def checkout_sale_rpc(
    cart: List[Dict[str, Any]],
    paid_amount: float,
    cashier_id: Optional[str] = None
):

    if not cart:

        return {
            "error": "ခြင်းတောင်း ဗလာဖြစ်နေပါသည်"
        }


    try:

        final_cashier_id = validate_uuid(
            cashier_id
        )


        payload = {

            "p_cart": cart,

            "p_paid_amount":
                money(paid_amount),

            "p_cashier_id":
                final_cashier_id
        }



        result = (
            supabase
            .rpc(
                "checkout_sale_rpc",
                payload
            )
            .execute()
        )



        if not result or not result.data:

            return {
                "error":
                "Database မှ တုံ့ပြန်ချက် မရရှိပါ"
            }



        sale_data = result.data



        # Supabase JSON return
        if isinstance(
            sale_data,
            dict
        ):


            if sale_data.get(
                "success"
            ):


                return {

                    "success": True,

                    "receipt_no":
                        sale_data.get(
                            "receipt_no"
                        )
                        or
                        sale_data.get(
                            "invoice_no"
                        ),

                    "sale_id":
                        sale_data.get(
                            "sale_id"
                        )
                }


            else:

                return {

                    "error":
                    sale_data.get(
                        "error",
                        "Unknown DB Error"
                    )
                }



        return {

            "error":
            "Invalid database response"

        }



    except Exception as e:

        log_error(e)

        return {

            "error":
            f"Checkout Failed: {str(e)}"

        }



# ==========================================
# PRODUCTS
# ==========================================

def get_products(
    active_only: bool = True
):

    try:

        query = (
            supabase
            .table("products")
            .select(
                """
                id,
                barcode,
                sku,
                name,
                selling_price,
                tax_rate,
                discount_allowed,
                stock,
                is_active
                """
            )
        )


        if active_only:

            query = query.eq(
                "is_active",
                True
            )


        return (
            query
            .execute()
            .data
            or []
        )


    except Exception as e:

        log_error(e)

        return []



# ==========================================
# RECEIPT
# ==========================================

def get_receipt(
    receipt_no: str
):

    try:

        return (
            supabase
            .table("sales")
            .select("*")
            .eq(
                "invoice_no",
                receipt_no
            )
            .single()
            .execute()
            .data
        )


    except Exception as e:

        log_error(e)

        return None



# ==========================================
# SALE ITEMS
# ==========================================

def get_sale_items(
    sale_id: str
):

    try:

        return (
            supabase
            .table("sale_items")
            .select("*")
            .eq(
                "sale_id",
                sale_id
            )
            .execute()
            .data
            or []
        )


    except Exception as e:

        log_error(e)

        return []
