# ==============================================================================
# erp_core/__init__.py
# ERP ENTERPRISE CORE PACKAGE v30.9
# CLEAN EXPORT - NO CIRCULAR IMPORT
# ==============================================================================


"""
ERP Core Package

IMPORTANT:
Keep this file lightweight.
Do NOT import services here.

Reason:
auth.py -> database.py -> erp_core
can create circular imports.
"""


# ==============================================================================
# Exceptions
# ==============================================================================

from .exceptions import *



# ==============================================================================
# Configuration
# ==============================================================================

from .config import (
    Tables,
    TABLE_PRODUCT_VIEW,
    DEFAULT_PAGE_SIZE,
    log_error
)



# ==============================================================================
# Context
# ==============================================================================

from .context import (
    ERPContext,
    CacheManager,
    generate_tx_id,
    generate_transaction_id
)



# ==============================================================================
# Database Core
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
# Repository Layer
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
# RPC Engine
# ==============================================================================

from .rpc_engine import (
    RPCEngine
)



# ==============================================================================
# VERSION
# ==============================================================================

ERP_CORE_VERSION = "30.9 CLEAN ARCHITECTURE"



__all__ = [

    # Database
    "db",
    "get_supabase",
    "get_connection",

    # Money
    "money",
    "money_float",

    # Security
    "validate_uuid",

    # Context
    "ERPContext",
    "CacheManager",

    # RPC
    "RPCEngine",

    # Config
    "Tables"

]
