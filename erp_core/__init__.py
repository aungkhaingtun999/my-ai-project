# ==============================================================================
# erp_core/__init__.py
# ERP ENTERPRISE CORE PACKAGE v30.12
# CLEAN LAZY ARCHITECTURE
# LOADERS + SERVICES + RPC SAFE EXPORT
# ==============================================================================


"""
ERP Core Package v30.12

Safe import architecture.

Pages
 |
 └── erp_core
       |
       ├── loaders
       ├── services
       ├── rpc
       └── repositories

"""



# ==============================================================================
# CORE IMPORTS
# ==============================================================================

from .exceptions import *


from .config import (

    Tables,

    TABLE_PRODUCT_VIEW,

    DEFAULT_PAGE_SIZE,

    log_error

)



from .context import (

    ERPContext,

    CacheManager,

    generate_tx_id,

    generate_transaction_id

)



from .base_repo import (

    get_supabase,

    db,

    get_connection,

    DatabaseHealth,

    database_health_check,

    money,

    money_float,

    validate_uuid,

    serialize_json,

    safe_execute

)



from .repositories import (

    RepositoryCoordinator,

    BaseRepository,

    ProductRepository,

    WarehouseRepository,

    CustomerRepository,

    SupplierRepository,

    SalesRepository

)



# RPC ENGINE ONLY

from .rpc.engine import RPCEngine





ERP_CORE_VERSION = "30.12 SAFE LAZY RPC ARCHITECTURE"





# ==============================================================================
# LAZY EXPORT MAP
# ==============================================================================


_EXPORTS = {


    # -------------------------
    # LOADERS
    # -------------------------

    "get_setting":
        ("loaders", "get_setting"),


    "get_products":
        ("loaders", "get_products"),


    "get_inventory_view":
        ("loaders", "get_inventory_view"),


    "get_warehouses":
        ("loaders", "get_warehouses"),


    "get_default_warehouse_id":
        ("loaders", "get_default_warehouse_id"),


    "get_suppliers":
        ("loaders", "get_suppliers"),


    "get_customers":
        ("loaders", "get_customers"),



    # -------------------------
    # SERVICES
    # -------------------------

    "AccountingLedgerService":
        ("services", "AccountingLedgerService"),


    "CustomerService":
        ("services", "CustomerService"),


    "SalesService":
        ("services", "SalesService"),


    "InventoryService":
        ("services", "InventoryService"),


    "PurchaseService":
        ("services", "PurchaseService"),


    "RefundService":
        ("services", "RefundService"),


    "DashboardService":
        ("services", "DashboardService"),


    "AuditService":
        ("services", "AuditService"),



    # -------------------------
    # RPC
    # -------------------------

    "checkout_sale_rpc":
        ("rpc.checkout_rpc", "checkout_sale_rpc"),


    "purchase_receive_rpc":
        ("rpc.purchase_rpc", "purchase_receive_rpc"),


    "refund_sale_rpc":
        ("rpc.refund_rpc", "refund_sale_rpc"),


    "stock_adjustment_rpc":
        ("rpc.stock_rpc", "stock_adjustment_rpc"),



    # -------------------------
    # HELPERS
    # -------------------------

    "get_fifo_cogs":
        ("services", "get_fifo_cogs"),


    "create_audit_log":
        ("services", "create_audit_log"),

}






# ==============================================================================
# SAFE LAZY LOADER
# ==============================================================================


def __getattr__(name):


    if name not in _EXPORTS:

        raise AttributeError(
            f"module 'erp_core' has no attribute '{name}'"
        )



    module_name, object_name = _EXPORTS[name]



    # RPC DIRECT IMPORT

    if module_name.startswith("rpc."):

        module = __import__(
            f"erp_core.{module_name}",
            fromlist=[object_name]
        )


        return getattr(
            module,
            object_name
        )



    # SERVICES

    if module_name == "services":

        from . import services

        return getattr(
            services,
            object_name
        )



    # LOADERS

    if module_name == "loaders":

        from . import loaders

        return getattr(
            loaders,
            object_name
        )



    raise AttributeError(name)







# ==============================================================================
# PUBLIC EXPORTS
# ==============================================================================


__all__ = [


    "ERP_CORE_VERSION",


    "db",

    "get_supabase",

    "get_connection",


    "money",

    "money_float",


    "Tables",

    "TABLE_PRODUCT_VIEW",


    "ERPContext",

    "CacheManager",


    "RPCEngine",



    "get_setting",

    "get_products",

    "get_inventory_view",

    "get_warehouses",

    "get_default_warehouse_id",

    "get_suppliers",

    "get_customers",



    "checkout_sale_rpc",

    "purchase_receive_rpc",

    "refund_sale_rpc",

    "stock_adjustment_rpc",



    "AccountingLedgerService",

    "CustomerService",

    "SalesService",

    "InventoryService",

    "PurchaseService",

    "RefundService",

    "DashboardService",

    "AuditService",


    "get_fifo_cogs",

    "create_audit_log"

]



print(
    "ERP_CORE v30.12 SAFE LAZY RPC ARCHITECTURE LOADED"
)
