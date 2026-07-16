# ==========================================
# database.py
# ERP ENTERPRISE WORLD CLASS v8
# RECEIPT + CHECKOUT STABLE
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



def log_error(err):

    logging.error(
        str(err)
    )

    print(
        "DB ERROR:",
        err
    )



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
# MONEY
# ==========================================

def money(value):

    try:

        return float(
            Decimal(
                str(value)
            )
            .quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )
        )

    except:

        return 0.0



# ==========================================
# UUID VALIDATOR
# ==========================================

def validate_uuid(value):

    if not value:

        return None


    try:

        return str(
            uuid.UUID(
                str(value)
            )
        )


    except:

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
            "error":
            "Cart is empty"
        }



    try:


        payload = {

            "p_cart":
                cart,


            "p_paid_amount":
                money(
                    paid_amount
                ),


            "p_cashier_id":
                validate_uuid(
                    cashier_id
                )

        }



        response = (
            supabase
            .rpc(
                "checkout_sale_rpc",
                payload
            )
            .execute()
        )



        data = response.data



        if not data:

            return {
                "error":
                "No database response"
            }



        if isinstance(data, dict):


            if data.get("success"):


                return {

                    "success":
                    True,


                    "receipt_no":
                    data.get(
                        "invoice_no"
                    )
                    or
                    data.get(
                        "receipt_no"
                    ),


                    "sale_id":
                    data.get(
                        "sale_id"
                    )

                }


            return {

                "error":
                data.get(
                    "error",
                    "Checkout failed"
                )

            }



        return {

            "error":
            "Invalid RPC response"

        }



    except Exception as e:


        log_error(e)


        return {

            "error":
            f"Checkout Failed: {e}"

        }



# ==========================================
# PRODUCTS
# ==========================================

def get_products(
    active_only=True
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
# RECEIPT HEADER
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
                receipt_no.strip()
            )
            .single()
            .execute()
            .data

        )



    except Exception as e:


        log_error(e)

        return None



# ==========================================
# RECEIPT DETAIL
# ==========================================

def get_receipt_detail(
    receipt_no: str
):


    try:


        sale = get_receipt(
            receipt_no
        )


        if not sale:

            return None



        items = get_sale_items(
            sale["id"]
        )


        sale["items"] = items


        return sale



    except Exception as e:


        log_error(e)

        return None




# ==========================================
# SALE ITEMS
# ==========================================

def get_sale_items(
    sale_id
):


    try:


        return (

            supabase
            .table("sale_items")
            .select(
                """
                id,
                product_id,
                quantity,
                unit_price,
                discount,
                total,
                products(
                    name,
                    barcode,
                    sku
                )
                """
            )
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



# ==========================================
# END
# ==========================================
