# ==============================================================================
# database.py
# ERP Enterprise Root Database Wrapper
# Compatibility Layer
# ==============================================================================

print("DATABASE ROOT WRAPPER LOADING...")

# ==============================================================================
# BASE CONNECTION
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

# Compatibility alias
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
# EXCEPTIONS
# ==============================================================================

from erp_core.exceptions import *

# ==============================================================================
# RPC ENGINE
# ==============================================================================

from erp_core.rpc_engine import RPCEngine

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

    require_login,

    get_warehouses,
    get_suppliers,
    get_customers,
    get_products,
)

# ==============================================================================
# HELPER
# ==============================================================================

def get_db_client():
    """Compatibility alias."""
    return db()

# ==============================================================================
# VERSION
# ==============================================================================

DATABASE_VERSION = "ERP V30 ROOT WRAPPER"

print("DATABASE ROOT WRAPPER LOADED")
