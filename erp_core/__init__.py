# ==============================================================================
# erp_core/__init__.py
# ERP ENTERPRISE CORE PACKAGE v30.10
# CLEAN ARCHITECTURE + LAZY SERVICE + RPC EXPORT
# ==============================================================================


"""
ERP Core Package

Architecture:

auth.py
    |
    └── erp_core.base_repo


pages
    |
    └── erp_core.services


RPC
    |
    └── erp_core.rpc


Services and RPC loaded lazily.
"""



# ==============================================================================
# EXCEPTIONS
# ==============================================================================

from .exceptions import *



# ==============================================================================
# CONFIGURATION
# ==============================================================================

from .config import (

    Tables,

    TABLE_PRODUCT_VIEW,

    DEFAULT_PAGE_SIZE,

    log_error

)



# ==============================================================================
# CONTEXT ENGINE
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
# REPOSITORY LAYER
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
# VERSION
# ==============================================================================

ERP_CORE_VERSION = "30.10 LAZY SERVICE + RPC ARCHITECTURE"





# ==============================================================================
# LAZY LOADER
# ==============================================================================


def __getattr__(name):


    exports = {



        # ==============================================================
        # SERVICES
        # ==============================================================


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




        # ==============================================================
        # SERVICE FUNCTIONS
        # ==============================================================


        "get_setting":
            ("services", "get_setting"),


        "get_products":
            ("services", "get_products"),


        "get_inventory_view":
            ("services", "get_inventory_view"),


        "get_warehouses":
            ("services", "get_warehouses"),


        "get_suppliers":
            ("services", "get_suppliers"),


        "get_customers":
            ("services", "get_customers"),


        "get_default_warehouse_id":
            ("services", "get_default_warehouse_id"),



        # ==============================================================
        # RPC FUNCTIONS
        # ==============================================================


        "checkout_sale_rpc":
            ("rpc", "checkout_sale_rpc"),


        "purchase_receive_rpc":
            ("rpc", "purchase_receive_rpc"),


        "refund_sale_rpc":
            ("rpc", "refund_sale_rpc"),


        "stock_adjustment_rpc":
            ("rpc", "stock_adjustment_rpc"),




        # ==============================================================
        # INVENTORY / ACCOUNTING
        # ==============================================================


        "get_fifo_cogs":
            ("services", "get_fifo_cogs"),



        # ==============================================================
        # AUDIT
        # ==============================================================


        "create_audit_log":
            ("services", "create_audit_log"),


    }



    if name in exports:


        package_name, object_name = exports[name]


        if package_name == "services":

            from . import services

            return getattr(
                services,
                object_name
            )



        if package_name == "rpc":

            from . import rpc

            return getattr(
                rpc,
                object_name
            )



    raise AttributeError(
        f"module 'erp_core' has no attribute '{name}'"
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



    # RPC

    "RPCEngine",



    # Config

    "Tables",

    "TABLE_PRODUCT_VIEW",



    # Lazy exports

    "get_setting",

    "get_products",

    "get_inventory_view",

    "get_warehouses",

    "get_suppliers",

    "get_customers",

    "get_default_warehouse_id",



    # RPC wrappers

    "checkout_sale_rpc",

    "purchase_receive_rpc",

    "refund_sale_rpc",

    "stock_adjustment_rpc",



    # Services

    "get_fifo_cogs",

    "create_audit_log"


]



print(
    "ERP_CORE v30.10 LAZY SERVICE + RPC ARCHITECTURE LOADED"
)
