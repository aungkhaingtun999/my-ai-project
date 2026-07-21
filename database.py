# ==============================================================================
# database.py
# ERP Enterprise Root Database Wrapper V30
# Stable Compatibility Layer
# ==============================================================================


print("DATABASE ROOT WRAPPER LOADING...")


# ==============================================================================
# DATABASE CORE
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
# EXCEPTIONS
# ==============================================================================

from erp_core.exceptions import *



# ==============================================================================
# RPC
# ==============================================================================

from erp_core.rpc_engine import (
    RPCEngine
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

    # Settings
    get_setting,


    # Business Services
    AccountingLedgerService,
    CustomerService,
    SalesService,
    InventoryService,
    PurchaseService,
    RefundService,
    DashboardService,
    AuditService,


    # Transaction Functions
    checkout_sale_rpc,
    purchase_receive_rpc,
    refund_sale_rpc,


    # Helpers
    get_fifo_cogs,
    create_audit_log,


    # Authentication
    require_login,


    # Data Loaders
    get_warehouses,
    get_suppliers,
    get_customers,
    get_products,
)



# ==============================================================================
# COMPATIBILITY
# ==============================================================================

def get_db_client():
    return db()



DATABASE_VERSION = "ERP V30 ROOT WRAPPER"


print("DATABASE ROOT WRAPPER LOADED")
