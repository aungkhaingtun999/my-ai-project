# database.py
# Root Wrapper with Explicit Imports for 100% Reliability

import streamlit as st
import logging
from decimal import Decimal
from typing import Dict, List, Any, Optional, Callable

# 1. Import Everything from erp_core package
from erp_core import *

# 2. Explicitly Re-export Critical Functions & Services to prevent import errors
from erp_core.base_repo import (
    db, get_connection, database_health_check, DatabaseHealth, 
    money, money_float, validate_uuid, serialize_json, safe_execute, CacheManager
)

from erp_core.context import (
    ERPContext, generate_tx_id, generate_transaction_id
)

from erp_core.exceptions import (
    ERPException, DatabaseError, ValidationError, PermissionDeniedError,
    TransactionError, DuplicateTransactionError, AccountingError,
    CreditLimitError, CreditLimitExceededError, RPCError
)

from erp_core.config import (
    ERP_VERSION, DEBUG, DEFAULT_PAGE_SIZE, CURRENCY, Tables,
    TABLE_USERS, TABLE_ROLE_PERMISSIONS, TABLE_PRODUCT_VIEW,
    TABLE_WAREHOUSES, TABLE_CUSTOMERS, TABLE_SUPPLIERS, TABLE_SALES,
    log_error, sanitize_payload
)

from erp_core.repositories import (
    RepositoryCoordinator, BaseRepository, ProductRepository,
    WarehouseRepository, CustomerRepository, SupplierRepository, SalesRepository
)

from erp_core.rpc_engine import RPCEngine

from erp_core.services import (
    AccountingLedgerService, CustomerService, SalesService,
    InventoryService, PurchaseService, RefundService,
    DashboardService, AuditService,
    checkout_sale_rpc, purchase_receive_rpc, refund_sale_rpc,
    get_fifo_cogs, create_audit_log, require_login,
    get_warehouses, get_suppliers, get_customers, get_products
)

# 3. Fallback Alias Helpers
def get_db_client():
    """Fallback alias for database client connection."""
    try:
        return db()
    except Exception:
        return None

