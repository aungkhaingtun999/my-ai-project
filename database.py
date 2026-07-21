# ==============================================================================
# database.py
# ERP ENTERPRISE DATABASE COMPATIBILITY LAYER V30.5
# Lazy-Loaded Resilient Root Wrapper
# ==============================================================================

print("DATABASE ROOT WRAPPER LOADING V30.5...")

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
# SERVICE LAZY LOADER (PREVENTS CIRCULAR IMPORTS)
# ==============================================================================

def _services():
    from erp_core import services
    return services


def get_products(*args, **kwargs):
    try:
        return _services().get_products(*args, **kwargs)
    except Exception:
        return []


def get_warehouses(*args, **kwargs):
    try:
        return _services().get_warehouses(*args, **kwargs)
    except Exception:
        return []


def get_customers(*args, **kwargs):
    try:
        return _services().get_customers(*args, **kwargs)
    except Exception:
        return []


def get_suppliers(*args, **kwargs):
    try:
        return _services().get_suppliers(*args, **kwargs)
    except Exception:
        return []


def get_setting(key, default=None):
    try:
        return _services().get_setting(key, default)
    except Exception:
        return default


def checkout_sale_rpc(*args, **kwargs):
    return _services().checkout_sale_rpc(*args, **kwargs)


def purchase_receive_rpc(*args, **kwargs):
    return _services().purchase_receive_rpc(*args, **kwargs)


def refund_sale_rpc(*args, **kwargs):
    return _services().refund_sale_rpc(*args, **kwargs)


def get_fifo_cogs(*args, **kwargs):
    try:
        return _services().get_fifo_cogs(*args, **kwargs)
    except Exception:
        return Decimal("0.00")


def create_audit_log(*args, **kwargs):
    try:
        return _services().create_audit_log(*args, **kwargs)
    except Exception:
        return False


def require_login():
    try:
        return _services().require_login()
    except Exception:
        ctx = ERPContext.get_current()
        if not ctx.current_user:
            return None
        return ctx.current_user


# ==============================================================================
# LEGACY & COMPATIBILITY LAYER
# ==============================================================================


def get_db_client():
    return db()


def get_default_warehouse_id():
    """
    Return current ERP default warehouse.
    Used by POS / Inventory / Purchase pages.
    """
    try:
        ctx = ERPContext.get_current()
        if ctx.current_warehouse_id:
            return int(ctx.current_warehouse_id)
    except Exception:
        pass
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
            return user.get("role", "cashier")
    except Exception:
        pass
    return "cashier"


def get_company_settings():
    return {
        "name": get_setting("company_name", "Enterprise ERP"),
        "currency": get_setting("currency", "MMK"),
        "tax_rate": get_setting("default_tax_rate", 0),
        "address": get_setting("company_address", ""),
        "phone": get_setting("company_phone", ""),
    }


def get_products_by_barcode(barcode, warehouse_id=None):
    try:
        warehouse_id = warehouse_id or get_default_warehouse_id()
        products = get_products(warehouse_id=warehouse_id, limit=5000)
        for product in products:
            if str(product.get("barcode")) == str(barcode) or str(product.get("sku")) == str(barcode):
                return product
    except Exception:
        pass
    return None


def get_receipt(invoice_no):
    try:
        table_sales = getattr(Tables, "SALES", "sales")
        result = (
            db()
            .table(table_sales)
            .select("*,sale_items(*)")
            .eq("invoice_no", str(invoice_no))
            .maybe_single()
            .execute()
        )
        return result.data
    except Exception:
        try:
            # Fallback without join if relationship name differs
            table_sales = getattr(Tables, "SALES", "sales")
            result = (
                db()
                .table(table_sales)
                .select("*")
                .eq("invoice_no", str(invoice_no))
                .maybe_single()
                .execute()
            )
            return result.data
        except Exception:
            return None


# ==============================================================================
# INVENTORY VIEW COMPATIBILITY
# ==============================================================================

def get_inventory_view(warehouse_id=None):
    """
    Return inventory stock view.
    Used by:
    - Inventory Page
    - Dashboard
    - Reports
    """
    try:
        client = db()
        table_name = globals().get(
            "TABLE_PRODUCT_VIEW",
            "products"
        )
        query = client.table(table_name).select("*")
        if warehouse_id:
            query = query.eq("warehouse_id", int(warehouse_id))
        result = query.execute()
        return result.data or []
    except Exception:
        return []


# ==============================================================================
# EXTENDED LEGACY API COMPATIBILITY ALIASES & WRAPPERS
# ==============================================================================

get_inventory = get_inventory_view
get_stock_view = get_inventory_view


def get_products_list(
    warehouse_id=None,
    offset=0,
    limit=100
):
    return get_products(
        warehouse_id=warehouse_id,
        offset=offset,
        limit=limit
    )


def get_stock(
    warehouse_id=None
):
    return get_inventory_view(
        warehouse_id
    )


def get_settings():
    return get_company_settings()


def current_user():
    return get_current_user()


def get_sales_summary(start_date=None, end_date=None, warehouse_id=None):
    try:
        client = db()
        table_sales = getattr(Tables, "SALES", "sales")
        query = client.table(table_sales).select("*")
        if warehouse_id:
            query = query.eq("warehouse_id", int(warehouse_id))
        if start_date:
            query = query.gte("created_at", str(start_date))
        if end_date:
            query = query.lte("created_at", str(end_date))
        res = query.execute()
        return res.data or []
    except Exception:
        return []


def get_dashboard_stats(warehouse_id=None):
    try:
        repo = RepositoryCoordinator(db())
        products = repo.products.get_products(
            warehouse_id=warehouse_id,
            limit=1000
        )
        return {
            "total_products": len(products),
            "low_stock_count": sum(
                1
                for p in products
                if p.get("stock", 0) <= p.get("minimum_stock", 5)
            ),
            "warehouse_id": warehouse_id or get_default_warehouse_id()
        }
    except Exception:
        return {
            "total_products": 0,
            "low_stock_count": 0,
            "warehouse_id": 1
        }


def get_users():
    try:
        table_users = getattr(Tables, "USERS", "users")
        res = db().table(table_users).select("*").execute()
        return res.data or []
    except Exception:
        return []


def get_roles():
    try:
        table_roles = getattr(Tables, "ROLES", "roles")
        res = (
            db()
            .table(table_roles)
            .select("*")
            .execute()
        )
        return res.data or []
    except Exception:
        try:
            table_perms = getattr(Tables, "ROLE_PERMISSIONS", "role_permissions")
            res = (
                db()
                .table(table_perms)
                .select("*")
                .execute()
            )
            return res.data or []
        except Exception:
            return []


def save_setting(key, value):
    try:
        client = db()
        table_settings = getattr(Tables, "SETTINGS", "settings")
        existing = client.table(table_settings).select("id").eq("key", key).maybe_single().execute()
        if existing and existing.data:
            client.table(table_settings).update({"value": value}).eq("key", key).execute()
        else:
            client.table(table_settings).insert({"key": key, "value": value}).execute()
        return True
    except Exception:
        return False


# ==============================================================================
# EXTRA LEGACY COMPATIBILITY
# ==============================================================================


def get_sales():
    return get_sales_summary()


def get_inventory_items(
    warehouse_id=None
):
    return get_inventory_view(
        warehouse_id
    )


def get_low_stock_products(
    warehouse_id=None
):
    products = get_inventory_view(
        warehouse_id
    )
    return [
        p for p in products
        if p.get("stock", 0)
        <=
        p.get("minimum_stock", 5)
    ]


def get_active_products():
    return get_products()


def get_active_users():
    return get_users()


# ==============================================================================
# VERSION
# ==============================================================================

DATABASE_VERSION = "ERP V30.5 COMPATIBILITY"

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
