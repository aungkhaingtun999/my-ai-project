# erp_core/base_repo.py
import time
import streamlit as st
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Callable
from supabase import create_client, Client
try:
    from postgrest.exceptions import APIError
except ImportError:
    APIError = Exception

from .config import log_error, Tables

@st.cache_resource
def get_supabase() -> Client:
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception as e:
        log_error(message="Supabase connection failed", exception=e)
        from .exceptions import DatabaseError
        raise DatabaseError("Cannot connect database")

def db() -> Client: return get_supabase()
get_connection = db

def money(value) -> Decimal:
    try: return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except: return Decimal("0.00")
def safe_float(value):
    try:
        return float(value or 0)
    except:
        return 0.0
def money_float(value): return float(money(value))

def validate_uuid(value) -> Optional[str]:
    if not value: return None
    import uuid
    try: return str(uuid.UUID(str(value)))
    except: return None

def serialize_json(data):
    import uuid
    if isinstance(data, Decimal): return float(data)
    if isinstance(data, uuid.UUID): return str(data)
    if isinstance(data, list): return [serialize_json(x) for x in data]
    if isinstance(data, dict): return {k: serialize_json(v) for k, v in data.items()}
    return data

def safe_execute(func: Callable, error_message="Database operation failed"):
    retry = 3
    for attempt in range(retry):
        try:
            result = func()
            if hasattr(result, "data"): return result.data
            return result
        except (APIError, ConnectionError, TimeoutError) as e:
            if attempt < retry - 1:
                time.sleep(0.5 * (attempt + 1))
                continue
            log_error(message=error_message, exception=e)
            from .exceptions import DatabaseError
            raise DatabaseError(str(e))
        except Exception as e:
            log_error(message=error_message, exception=e)
            from .exceptions import DatabaseError
            raise DatabaseError(str(e))
    return None

class DatabaseHealth:
    @staticmethod
    def check() -> bool:
        try:
            result = db().table(Tables.PRODUCTS).select("id").limit(1).execute()
            return result is not None
        except Exception as e:
            log_error(message="Database health check failed", exception=e)
            return False

def database_health_check(): return DatabaseHealth.check()

__all__ = [
    "get_supabase",
    "db",
    "get_connection",
    "money",
    "money_float",
    "safe_float",
    "validate_uuid",
    "serialize_json",
    "safe_execute",
    "DatabaseHealth",
    "database_health_check",
    "log_error"
]
