# ==============================================================================
# erp_core/__init__.py
# ERP Enterprise Core Package
# ==============================================================================

# ------------------------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------------------------
from .exceptions import *

# ------------------------------------------------------------------------------
# Configuration / Constants
# ------------------------------------------------------------------------------
from .config import *

# ------------------------------------------------------------------------------
# Context & Cache
# ------------------------------------------------------------------------------
from .context import (
    ERPContext,
    CacheManager,
    generate_tx_id,
    generate_transaction_id,
)

# ------------------------------------------------------------------------------
# Database Core
# ------------------------------------------------------------------------------
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
    safe_execute,
)

# ------------------------------------------------------------------------------
# Repository Layer
# ------------------------------------------------------------------------------
from .repositories import (
    BaseRepository,
    RepositoryCoordinator,
    ProductRepository,
    WarehouseRepository,
    CustomerRepository,
    SupplierRepository,
    SalesRepository,
)

# ------------------------------------------------------------------------------
# RPC Engine
# ------------------------------------------------------------------------------
from .rpc_engine import RPCEngine

# ------------------------------------------------------------------------------
# Service Layer
# ------------------------------------------------------------------------------
from .services import (
    AccountingLedgerService,
    CustomerService,
    SalesService,
    InventoryService,
    PurchaseService,
    RefundService,
    DashboardService,
    AuditService,

    checkout_sale_rpc,
    purchase_receive_rpc,
    refund_sale_rpc,

    get_fifo_cogs,
    create_audit_log,

    get_products,
    get_customers,
    get_suppliers,
    get_warehouses,

    get_setting,

    require_login,
)

# ------------------------------------------------------------------------------
# Public Export List
# ------------------------------------------------------------------------------

__all__ = [

    # database
    "get_supabase",
    "db",
    "get_connection",
    "DatabaseHealth",
    "database_health_check",
    "money",
    "money_float",
    "validate_uuid",
    "serialize_json",
    "safe_execute",

    # context
    "ERPContext",
    "CacheManager",
    "generate_tx_id",
    "generate_transaction_id",

    # repositories
    "BaseRepository",
    "RepositoryCoordinator",
    "ProductRepository",
    "WarehouseRepository",
    "CustomerRepository",
    "SupplierRepository",
    "SalesRepository",

    # services
    "AccountingLedgerService",
    "CustomerService",
    "SalesService",
    "InventoryService",
    "PurchaseService",
    "RefundService",
    "DashboardService",
    "AuditService",

    "checkout_sale_rpc",
    "purchase_receive_rpc",
    "refund_sale_rpc",

    "get_fifo_cogs",
    "create_audit_log",

    "get_products",
    "get_customers",
    "get_suppliers",
    "get_warehouses",

    "require_login",

    # rpc
    "RPCEngine",
]
