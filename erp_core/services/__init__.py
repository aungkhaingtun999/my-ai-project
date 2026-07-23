# ==============================================================================
# erp_core/__init__.py
# ERP ENTERPRISE CORE PACKAGE v30.11
# CLEAN ARCHITECTURE
# LAZY LOADERS + SERVICES + RPC
# ==============================================================================


"""
ERP Core Package

Architecture:

Pages
 |
 ├── loaders
 |       └── data loading layer
 |
 ├── services
 |       └── business logic layer
 |
 └── rpc
         └── transaction gateway


All heavy modules are loaded lazily.
"""


# ==============================================================================
# EXCEPTIONS
# ==============================================================================





# ==============================================================================
# CONFIG
# ==============================================================================

from ..config import (
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
# RPC ENGINE ONLY
# (Do not import rpc package here)
# ==============================================================================

from .rpc.engine import (

    RPCEngine

)



# ==============================================================================
# VERSION
# ==============================================================================

ERP_CORE_VERSION = "30.11 LAZY LOADERS + SERVICES + RPC"





# ==============================================================================
# LAZY EXPORT MAP
# ==============================================================================


_EXPORTS = {


    # --------------------------------------------------
    # LOADERS
    # --------------------------------------------------

    "get_setting":
        ("loaders", "get_setting"),


    "get_products":
        ("loaders", "get_products"),


    "get_inventory_view":
        ("loaders", "get_inventory_view"),


    "get_warehouses":
        ("loaders", "get_warehouses"),


    "get_suppliers":
        ("loaders", "get_suppliers"),


    "get_customers":
        ("loaders", "get_customers"),


    "get_default_warehouse_id":
        ("loaders", "get_default_warehouse_id"),




    # --------------------------------------------------
    # SERVICES
    # --------------------------------------------------

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



    # --------------------------------------------------
    # RPC FUNCTIONS
    # --------------------------------------------------

    "checkout_sale_rpc":
        ("rpc", "checkout_sale_rpc"),


    "purchase_receive_rpc":
        ("rpc", "purchase_receive_rpc"),


    "refund_sale_rpc":
        ("rpc", "refund_sale_rpc"),


    "stock_adjustment_rpc":
        ("rpc", "stock_adjustment_rpc"),



    # --------------------------------------------------
    # OTHER FUNCTIONS
    # --------------------------------------------------

    "get_fifo_cogs":
        ("services", "get_fifo_cogs"),


    "create_audit_log":
        ("services", "create_audit_log"),

}





# ==============================================================================
# PYTHON LAZY IMPORT ENGINE
# ==============================================================================


def __getattr__(name):


    if name not in _EXPORTS:

        raise AttributeError(
            f"module 'erp_core' has no attribute '{name}'"
        )



    package_name, object_name = _EXPORTS[name]



    # --------------------------------------------------
    # LOADERS
    # --------------------------------------------------

    if package_name == "loaders":

        from . import loaders

        return getattr(
            loaders,
            object_name
        )



    # --------------------------------------------------
    # SERVICES
    # --------------------------------------------------

    if package_name == "services":

        from . import services

        return getattr(
            services,
            object_name
        )



    # --------------------------------------------------
    # RPC
    # --------------------------------------------------

    if package_name == "rpc":

        from . import rpc

        return getattr(
            rpc,
            object_name
        )





# ==============================================================================
# PUBLIC EXPORTS
# ==============================================================================


__all__ = [


    # Version

    "ERP_CORE_VERSION",



    # Database

    "db",

    "get_supabase",

    "get_connection",



    # Money

    "money",

    "money_float",



    # Validation

    "validate_uuid",

    "serialize_json",



    # Context

    "ERPContext",

    "CacheManager",



    # Config

    "Tables",

    "TABLE_PRODUCT_VIEW",



    # RPC Engine

    "RPCEngine",



    # Loaders

    "get_setting",

    "get_products",

    "get_inventory_view",

    "get_warehouses",

    "get_suppliers",

    "get_customers",

    "get_default_warehouse_id",



    # RPC

    "checkout_sale_rpc",

    "purchase_receive_rpc",

    "refund_sale_rpc",

    "stock_adjustment_rpc",



    # Services

    "AccountingLedgerService",

    "CustomerService",

    "SalesService",

    "InventoryService",

    "PurchaseService",

    "RefundService",

    "DashboardService",

    "AuditService",



    # Other

    "get_fifo_cogs",

    "create_audit_log",

]



print(
    "ERP_CORE v30.11 LAZY LOADERS + SERVICES + RPC LOADED"
)
