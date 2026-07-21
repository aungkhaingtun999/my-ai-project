# ==============================================================================
# erp_core/__init__.py
# ERP ENTERPRISE CORE PACKAGE v30.10
# CLEAN ARCHITECTURE + LAZY SERVICE EXPORT
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


IMPORTANT:
Services are loaded lazily.
Never import services during package initialization.
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

from .rpc_engine import (

    RPCEngine

)



# ==============================================================================
# VERSION
# ==============================================================================

ERP_CORE_VERSION = "30.10 LAZY SERVICE ARCHITECTURE"



# ==============================================================================
# LAZY SERVICE LOADER
# ==============================================================================


def __getattr__(name):

    """
    Lazy import services.

    Prevent:

        auth
          ↓
        erp_core
          ↓
        services
          ↓
        auth

    circular import.
    """


    service_exports = {


        # Settings
        "get_setting": "get_setting",


        # Service Classes
        "AccountingLedgerService":
            "AccountingLedgerService",

        "CustomerService":
            "CustomerService",

        "SalesService":
            "SalesService",

        "InventoryService":
            "InventoryService",

        "PurchaseService":
            "PurchaseService",

        "RefundService":
            "RefundService",

        "DashboardService":
            "DashboardService",

        "AuditService":
            "AuditService",



        # RPC Wrappers
        "checkout_sale_rpc":
            "checkout_sale_rpc",

        "purchase_receive_rpc":
            "purchase_receive_rpc",

        "refund_sale_rpc":
            "refund_sale_rpc",

        "stock_adjustment_rpc":
            "stock_adjustment_rpc",



        # Inventory / Dashboard
        "get_fifo_cogs":
            "get_fifo_cogs",

        "get_inventory_view":
            "get_inventory_view",



        # Loaders
        "get_products":
            "get_products",

        "get_warehouses":
            "get_warehouses",

        "get_suppliers":
            "get_suppliers",

        "get_customers":
            "get_customers",

        "get_default_warehouse_id":
            "get_default_warehouse_id",



        # Audit
        "create_audit_log":
            "create_audit_log"

    }



    if name in service_exports:


        from . import services


        return getattr(
            services,
            service_exports[name]
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



    # Services lazy

    "get_setting",

    "get_products",

    "get_inventory_view",

    "get_warehouses",

    "get_suppliers",

    "get_customers",

    "get_default_warehouse_id",

    "checkout_sale_rpc",

    "purchase_receive_rpc",

    "refund_sale_rpc",

    "stock_adjustment_rpc",

    "get_fifo_cogs",

    "create_audit_log"


]
