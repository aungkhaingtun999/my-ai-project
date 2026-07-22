# ==============================================================================
# erp_core/__init__.py
# ERP ENTERPRISE CORE PACKAGE v30.11
# CLEAN ARCHITECTURE + LOADERS + RPC EXPORT
# ==============================================================================


"""
ERP Core Package v30.11

Architecture:

Pages
 |
 └── erp_core
       |
       ├── loaders
       |      └── data loading
       |
       ├── services
       |      └── business logic
       |
       ├── rpc
       |      └── transaction wrappers
       |
       └── repositories
              └── database access

"""


# ==============================================================================
# EXCEPTIONS
# ==============================================================================

from .exceptions import *



# ==============================================================================
# CONFIG
# ==============================================================================

from .config import (
    Tables,
    TABLE_PRODUCT_VIEW,
    DEFAULT_PAGE_SIZE,
    log_error
)



# ==============================================================================
# CONTEXT
# ==============================================================================

from .context import (
    ERPContext,
    CacheManager,
    generate_tx_id,
    generate_transaction_id
)



# ==============================================================================
# DATABASE CORE
# ==============================================================================

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



# ==============================================================================
# REPOSITORIES
# ==============================================================================

from .repositories import (

    RepositoryCoordinator,

    BaseRepository,

    ProductRepository,

    WarehouseRepository,

    CustomerRepository,

    SupplierRepository,

    SalesRepository

)



# ==============================================================================
# RPC ENGINE
# ==============================================================================

from .rpc.engine import (

    RPCEngine

)



# ==============================================================================
# RPC EXPORT
# IMPORTANT: direct import
# ==============================================================================

from .rpc import (

    checkout_sale_rpc,

    purchase_receive_rpc,

    refund_sale_rpc,

    stock_adjustment_rpc

)



# ==============================================================================
# VERSION
# ==============================================================================

ERP_CORE_VERSION = "30.11 LOADERS + RPC STABLE"





# ==============================================================================
# LAZY LOADER
# ==============================================================================


def __getattr__(name):


    exports = {


        # ==========================================================
        # LOADERS
        # ==========================================================

        "get_setting":
            ("loaders","get_setting"),


        "get_products":
            ("loaders","get_products"),


        "get_inventory_view":
            ("loaders","get_inventory_view"),


        "get_warehouses":
            ("loaders","get_warehouses"),


        "get_default_warehouse_id":
            ("loaders","get_default_warehouse_id"),


        "get_suppliers":
            ("loaders","get_suppliers"),


        "get_customers":
            ("loaders","get_customers"),



        # ==========================================================
        # SERVICES
        # ==========================================================

        "AccountingLedgerService":
            ("services","AccountingLedgerService"),


        "CustomerService":
            ("services","CustomerService"),


        "SalesService":
            ("services","SalesService"),


        "InventoryService":
            ("services","InventoryService"),


        "PurchaseService":
            ("services","PurchaseService"),


        "RefundService":
            ("services","RefundService"),


        "DashboardService":
            ("services","DashboardService"),


        "AuditService":
            ("services","AuditService"),



        # ==========================================================
        # SERVICE HELPERS
        # ==========================================================

        "get_fifo_cogs":
            ("services","get_fifo_cogs"),


        "create_audit_log":
            ("services","create_audit_log"),

    }



    if name in exports:


        package_name, object_name = exports[name]



        if package_name == "loaders":

            from . import loaders

            return getattr(
                loaders,
                object_name
            )



        if package_name == "services":

            from . import services

            return getattr(
                services,
                object_name
            )



    raise AttributeError(
        f"module 'erp_core' has no attribute '{name}'"
    )





# ==============================================================================
# PUBLIC EXPORTS
# ==============================================================================


__all__ = [


    # VERSION

    "ERP_CORE_VERSION",



    # DATABASE

    "db",

    "get_supabase",

    "get_connection",



    # MONEY

    "money",

    "money_float",



    # CONTEXT

    "ERPContext",

    "CacheManager",



    # CONFIG

    "Tables",

    "TABLE_PRODUCT_VIEW",



    # RPC

    "RPCEngine",

    "checkout_sale_rpc",

    "purchase_receive_rpc",

    "refund_sale_rpc",

    "stock_adjustment_rpc",



    # LOADERS

    "get_setting",

    "get_products",

    "get_inventory_view",

    "get_warehouses",

    "get_default_warehouse_id",

    "get_suppliers",

    "get_customers",



    # SERVICES

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
    "ERP_CORE v30.11 LOADERS + RPC STABLE LOADED"
)
