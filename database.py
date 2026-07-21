# ==============================================================================
# database.py
# ERP ENTERPRISE DATABASE COMPATIBILITY LAYER V30.1
# Stable Root Wrapper
# ==============================================================================


# ==============================================================================
# CORE
# ==============================================================================

from erp_core.base_repo import (
    get_supabase,
    db,
    get_connection,
    DatabaseHealth,
    database_health_check,
    money,
    money_float,
    validate_uuid,
    serialize_json,
    safe_execute,
)


safe_query = safe_execute



# ==============================================================================
# CONFIG
# ==============================================================================

from erp_core.config import *



# ==============================================================================
# CONTEXT
# ==============================================================================

from erp_core.context import (
    ERPContext,
    CacheManager,
    generate_tx_id,
    generate_transaction_id,
)



# ==============================================================================
# REPOSITORIES
# ==============================================================================

from erp_core.repositories import (
    BaseRepository,
    RepositoryCoordinator,
    ProductRepository,
    WarehouseRepository,
    CustomerRepository,
    SupplierRepository,
    SalesRepository,
)



# ==============================================================================
# SERVICES
# ==============================================================================

from erp_core.services import (

    get_setting,

    get_products,
    get_warehouses,
    get_customers,
    get_suppliers,

    get_fifo_cogs,

    create_audit_log,

    checkout_sale_rpc,
    purchase_receive_rpc,
    refund_sale_rpc,

    require_login,

)



# ==============================================================================
# LEGACY COMPATIBILITY
# ==============================================================================


def get_db_client():
    return db()



def get_default_warehouse_id():

    try:
        ctx = ERPContext.get_current()

        return int(
            ctx.current_warehouse_id
        )

    except Exception:

        return 1




def get_current_user():

    try:

        ctx = ERPContext.get_current()

        return ctx.current_user

    except Exception:

        return None




def get_user_role():

    try:

        user = get_current_user()

        if isinstance(user, dict):

            return user.get(
                "role",
                "cashier"
            )

    except Exception:
        pass


    return "cashier"




def get_company_settings():

    return {

        "name":
            get_setting(
                "company_name",
                "Enterprise ERP"
            ),


        "currency":
            get_setting(
                "currency",
                "MMK"
            ),


        "tax_rate":
            get_setting(
                "default_tax_rate",
                0
            ),


        "address":
            get_setting(
                "company_address",
                ""
            ),


        "phone":
            get_setting(
                "company_phone",
                ""
            ),

    }




def get_products_by_barcode(
    barcode,
    warehouse_id=None
):

    try:

        warehouse_id = (
            warehouse_id
            or
            get_default_warehouse_id()
        )


        products = get_products(
            warehouse_id=warehouse_id,
            limit=5000
        )


        for product in products:

            if (

                str(product.get("barcode"))
                ==
                str(barcode)

                or

                str(product.get("sku"))
                ==
                str(barcode)

            ):

                return product


    except Exception:

        pass


    return None




def get_receipt(invoice_no):

    try:

        result = (

            db()
            .table("sales")
            .select("*")
            .eq(
                "invoice_no",
                str(invoice_no)
            )
            .maybe_single()
            .execute()

        )


        return result.data


    except Exception:

        return None




# ==============================================================================
# VERSION
# ==============================================================================


DATABASE_VERSION = "ERP V30.1 COMPATIBILITY"
