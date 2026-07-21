# ==============================================================================
# erp_core/__init__.py
# ERP ENTERPRISE CORE EXPORT v30
# ==============================================================================


# Exceptions
from .exceptions import *


# Configuration
from .config import *


# Context
from .context import (
    ERPContext,
    CacheManager,
    generate_tx_id,
    generate_transaction_id
)


# Database Core
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


# Repository Layer
from .repositories import (
    RepositoryCoordinator,
    BaseRepository,
    ProductRepository,
    WarehouseRepository,
    CustomerRepository,
    SupplierRepository,
    SalesRepository
)


# RPC Engine
from .rpc_engine import (
    RPCEngine
)


# Service Layer

from .services import (

    # Settings
    get_setting,


    # Services
    AccountingLedgerService,
    CustomerService,
    SalesService,
    InventoryService,
    PurchaseService,
    RefundService,
    DashboardService,
    AuditService,


    # Functions
    checkout_sale_rpc,
    purchase_receive_rpc,
    refund_sale_rpc,

    get_fifo_cogs,
    create_audit_log,


    # Loaders
    get_warehouses,
    get_suppliers,
    get_customers,
    get_products,


    require_login
)
