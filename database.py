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

from erp_core.repositories import *
from erp_core.services import *
from erp_core.rpc_engine import RPCEngine
from erp_core.context import ERPContext, CacheManager
from erp_core.config import *
from erp_core.exceptions import *


def get_db_client():
    return db()
