# ==============================================================================
# erp_core/database.py
# ERP ENTERPRISE DATABASE GATEWAY v31
# CORE DATABASE CONNECTION + COMPATIBILITY LAYER
# ==============================================================================


import streamlit as st

from typing import Any


from supabase import (
    create_client,
    Client
)


from .config import (
    Tables,
    log_error
)


from .exceptions import (
    DatabaseError
)


# ==============================================================================
# VERSION
# ==============================================================================

ERP_DATABASE_VERSION = "31.0 Gateway"


# ==============================================================================
# SUPABASE CONNECTION
# ==============================================================================


@st.cache_resource
def get_supabase() -> Client:

    """
    Create and cache Supabase client.

    Single database connection gateway.
    """

    try:

        return create_client(

            st.secrets["SUPABASE_URL"],

            st.secrets["SUPABASE_KEY"]

        )


    except Exception as e:

        log_error(

            message="Supabase connection failed",

            exception=e

        )

        raise DatabaseError(
            "Cannot connect database"
        )





def db() -> Client:

    """
    Main database accessor.
    """

    return get_supabase()



# legacy alias

get_connection = db



# ==============================================================================
# DATABASE HEALTH CHECK
# ==============================================================================


class DatabaseHealth:


    @staticmethod
    def check() -> bool:


        try:

            result = (

                db()

                .table(
                    Tables.PRODUCTS
                )

                .select(
                    "id"
                )

                .limit(
                    1
                )

                .execute()

            )


            return result is not None



        except Exception as e:


            log_error(

                message=
                "Database health check failed",

                exception=e

            )


            return False





def database_health_check():

    return DatabaseHealth.check()



# ==============================================================================
# COMPATIBILITY EXPORTS
# ==============================================================================
#
# Old pages may still use:
#
# from erp_core.database import get_products
#
# Keep these bridges during migration.
#
# ==============================================================================



# -------------------------
# Loaders
# -------------------------


try:

    from .loaders import (

        get_products,

        get_customers,

        get_suppliers,

        get_warehouses,

        get_inventory_view,

        get_setting

    )


except Exception:


    get_products = None

    get_customers = None

    get_suppliers = None

    get_warehouses = None

    get_inventory_view = None

    get_setting = None





# -------------------------
# RPC
# -------------------------


try:

    from .rpc import (

        checkout_sale_rpc,

        purchase_receive_rpc,

        refund_sale_rpc,

        stock_adjustment_rpc

    )


except Exception:


    checkout_sale_rpc = None

    purchase_receive_rpc = None

    refund_sale_rpc = None

    stock_adjustment_rpc = None





# -------------------------
# Services
# -------------------------


try:

    from .services import (

        SalesService,

        PurchaseService,

        InventoryService,

        RefundService

    )


    def get_sales_service():

        return SalesService(
            db()
        )



    def get_purchase_service():

        return PurchaseService(
            db()
        )



    def get_inventory_service():

        return InventoryService(
            db()
        )



    def get_refund_service():

        return RefundService(
            db()
        )



except Exception:


    SalesService = None

    PurchaseService = None

    InventoryService = None

    RefundService = None





# ==============================================================================
# EXPORTS
# ==============================================================================


__all__ = [


    # database

    "db",

    "get_supabase",

    "get_connection",

    "DatabaseHealth",

    "database_health_check",



    # loaders

    "get_products",

    "get_customers",

    "get_suppliers",

    "get_warehouses",

    "get_inventory_view",

    "get_setting",



    # rpc

    "checkout_sale_rpc",

    "purchase_receive_rpc",

    "refund_sale_rpc",

    "stock_adjustment_rpc",



    # service factory

    "get_sales_service",

    "get_purchase_service",

    "get_inventory_service",

    "get_refund_service",


]


print(
    "ERP DATABASE GATEWAY v31 LOADED SUCCESSFULLY"
)
