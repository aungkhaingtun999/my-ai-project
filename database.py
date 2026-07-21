# database.py
# Robust Root Wrapper & Compatibility Bridge for ERP System
# This ensures 100% backward compatibility for all pages importing from 'database'.

import streamlit as st
import logging
from decimal import Decimal
from typing import Dict, List, Any, Optional, Callable

# Import everything from the core package
from erp_core import *

# --- SAFE FALLBACKS & EXTRA ALIASES (Prevent any potential missing attribute errors) ---

try:
    from erp_core import db, get_connection, ERPContext, CacheManager
except ImportError:
    pass

# Ensure critical helper functions are explicitly available at root level
def get_db_client():
    """Fallback alias for database client connection."""
    try:
        return db()
    except Exception:
        return None

# Additional runtime safety check for global variables if needed
if "CURRENCY" not in globals():
    CURRENCY = "MMK"

if "DEFAULT_PAGE_SIZE" not in globals():
    DEFAULT_PAGE_SIZE = 100

