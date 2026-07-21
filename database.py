# database.py
# Clean Root Wrapper for Enterprise ERP System

from erp_core import *

def get_db_client():
    """Convenience alias for database client connection."""
    try:
        return db()
    except Exception:
        return None
        
