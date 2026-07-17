# ==========================================
# database.py
# ERP ENTERPRISE v14.7 - STABLE CORE
# POS + PURCHASE + RECEIPT READY
# ==========================================

import streamlit as st
import logging
import uuid

from decimal import Decimal, ROUND_HALF_UP
from supabase import create_client, Client


# ==========================================
# LOGGING
# ==========================================

logging.basicConfig(
    filename="erp_db.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s"
)


def log_error(err):
    logging.error(str(err))


# ==========================================
# SUPABASE CONNECTION
# ==========================================

@st.cache_resource
def get_supabase() -> Client:

    try:

        return create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )

    except Exception as e:

        st.error("Supabase connection error")
        log_error(e)
        raise e



def db():
    return get_supabase()



# ==========================================
# HELPERS
# ==========================================

def money(value):

    try:

        return float(
            Decimal(str(value))
            .quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )
        )

    except:

        return 0.0



def validate_uuid(value):

    try:
        return str(uuid.UUID(str(value)))

    except:

        return None



# ==========================================
# SETTINGS
# ==========================================

def get_setting(key, default=None):

    try:

        res = (
            db()
            .table("erp_settings")
            .select("value")
            .eq("key", key)
            .maybe_single()
            .execute()
        )

        if res.data:
            return res.data.get("value")

        return default


    except Exception as e:

        log_error(e)
        return default



# ==========================================
# PRODUCTS
# ==========================================

def get_products(active_only=True):

    try:

        query = (
            db()
            .table("products")
            .select(
                """
                id,
                barcode,
                sku,
                name,
                purchase_price,
                selling_price,
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


        return query.execute().data or []


    except Exception as e:

        log_error(e)
        return []



# ==========================================
# SUPPLIER
# ==========================================

def get_suppliers():

    try:

        return (
            db()
            .table("suppliers")
            .select(
                "id,name,phone"
            )
            .execute()
            .data
            or []
        )


    except Exception as e:

        log_error(e)
        return []



# ==========================================
# WAREHOUSE
# ==========================================

def get_warehouses():

    try:

        return (
            db()
            .table("warehouses")
            .select(
                "id,code,name,branch"
            )
            .eq(
                "is_active",
                True
            )
            .execute()
            .data
            or []
        )


    except Exception as e:

        log_error(e)
        return []



# ==========================================
# PURCHASE RECEIVE RPC
# ==========================================

def purchase_receive_rpc(
        p_id,
        s_id,
        w_id,
        qty,
        price,
        notes="",
        uid=None
):


    payload = {

        "p_product_id": p_id,

        "p_supplier_id": s_id,

        "p_warehouse_id": w_id,

        "p_qty": int(qty),

        "p_price": money(price),

        "p_notes": notes,

        "p_created_by": validate_uuid(uid)

    }


    try:

        res = (
            db()
            .rpc(
                "purchase_receive_rpc",
                payload
            )
            .execute()
        )


        return res.data



    except Exception as e:

        log_error(e)

        return {

            "success":False,

            "message":str(e)

        }



# ==========================================
# POS CHECKOUT RPC
# ==========================================

def checkout_sale_rpc(
        cart,
        paid_amount,
        cashier_id=None
):


    try:


        payload = {

            "p_cart": cart,

            "p_paid_amount": money(
                paid_amount
            ),

            "p_cashier_id":
                validate_uuid(
                    cashier_id
                )

        }


        res = (
            db()
            .rpc(
                "checkout_sale_rpc",
                payload
            )
            .execute()
        )


        if res.data is None:

            return {

                "success":False,

                "message":
                "Database function returned empty result"

            }


        return res.data



    except Exception as e:


        log_error(e)


        return {

            "success":False,

            "message":str(e)

        }



# ==========================================
# AUDIT LOG
# ==========================================

def create_audit_log(
        user_id,
        action,
        details
):


    try:


        res = (
            db()
            .table("audit_logs")
            .insert({

                "user_id":
                validate_uuid(user_id),

                "action":
                action,

                "details":
                details

            })
            .execute()
        )


        return {

            "success":True,

            "data":res.data

        }



    except Exception as e:


        log_error(e)


        return {

            "success":False,

            "message":str(e)

        }



# ==========================================
# RECEIPT
# ==========================================

def get_receipt(invoice_no):

    try:

        return (

            db()
            .table("sales")
            .select("*")
            .eq(
                "invoice_no",
                invoice_no
            )
            .maybe_single()
            .execute()
            .data

        )


    except Exception as e:

        log_error(e)

        return None



def get_sale_items(sale_id):

    try:

        return (

            db()
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



print("DATABASE v14.7 IMPORT SUCCESS")
