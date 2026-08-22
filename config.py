# ==========================================
# config.py
# Production Ready Configuration
# Multi-Tenant Extended
# ==========================================

from pathlib import Path
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==========================================
# APP INFORMATION
# ==========================================

APP_NAME = "AI POS System"
APP_VERSION = "1.0.0"

COMPANY_NAME = "My Store"

CURRENCY = "MMK"

TIMEZONE = "Asia/Yangon"

DATE_FORMAT = "%d-%m-%Y"

DATETIME_FORMAT = "%d-%m-%Y %H:%M:%S"

# ==========================================
# SUPABASE CONFIGURATION
# ==========================================

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-supabase-anon-key-here")

# ==========================================
# TIMEZONE MANAGEMENT
# ==========================================

TIMEZONE_OPTIONS = {
    "Myanmar 🇲🇲": "Asia/Yangon",
    "Thailand 🇹🇭": "Asia/Bangkok",
    "Mongolia 🇲🇳": "Asia/Ulaanbaatar",
    "Japan 🇯🇵": "Asia/Tokyo",
    "Singapore 🇸🇬": "Asia/Singapore",
    "China 🇨🇳": "Asia/Shanghai",
    "UTC 🌐": "UTC"
}

DEFAULT_TIMEZONE = "Asia/Yangon"

# Auto browser/device timezone
AUTO_TIMEZONE = True

# ==========================================
# ROOT PATH
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

PAGES_DIR = BASE_DIR / "pages"

UTILS_DIR = BASE_DIR / "utils"

SQL_DIR = BASE_DIR / "sql"

LOCALE_DIR = BASE_DIR / "locale"

RECEIPT_DIR = BASE_DIR / "receipts"

LOG_DIR = BASE_DIR / "logs"

EXPORT_DIR = BASE_DIR / "exports"

# Auto Create Folder
for folder in [
    RECEIPT_DIR,
    LOG_DIR,
    EXPORT_DIR
]:
    folder.mkdir(exist_ok=True)

# ==========================================
# USER ROLES
# ==========================================

ROLE_ADMIN = "Admin"
ROLE_MANAGER = "Manager"
ROLE_CASHIER = "Cashier"

ROLES = [
    ROLE_ADMIN,
    ROLE_MANAGER,
    ROLE_CASHIER
]

# ==========================================
# MULTI-TENANT SETTINGS
# ==========================================

MULTI_TENANT_ENABLED = True

TENANT_ROLES = [
    "staff",
    "manager",
    "admin",
    "owner"
]

DEFAULT_TENANT_ROLE = "staff"

TENANT_SESSION_KEYS = [
    "shop_id",
    "branch_id",
    "tenant_role",
    "shop_name",
    "branch_name"
]

# ==========================================
# LANGUAGES
# ==========================================

LANG_MY = "မြန်မာ"
LANG_EN = "English"

LANGUAGES = [
    LANG_MY,
    LANG_EN
]

DEFAULT_LANGUAGE = LANG_EN

# ==========================================
# RECEIPT
# ==========================================

RECEIPT_PREFIX = "RCP"

STORE_FOOTER = "Thank you. Please come again."

# ==========================================
# INVENTORY
# ==========================================

DEFAULT_MINIMUM_STOCK = 5

LOW_STOCK_COLOR = "red"

# ==========================================
# SALES
# ==========================================

DEFAULT_TAX = 0.0

ALLOW_NEGATIVE_STOCK = False

DEFAULT_PAYMENT_METHOD = "CASH"

PAYMENT_METHODS = [
    "CASH",
    "KBZPay",
    "WavePay",
    "AYA Pay",
    "CB Pay",
    "Bank Transfer"
]

# ==========================================
# REPORTS
# ==========================================

TOP_PRODUCT_LIMIT = 10

RECENT_SALES_LIMIT = 20

# ==========================================
# DASHBOARD
# ==========================================

CHART_HEIGHT = 350

# ==========================================
# SESSION STATE
# ==========================================

SESSION_DEFAULTS = {
    "user": None,
    "role": ROLE_CASHIER,
    "language": DEFAULT_LANGUAGE,
    "cart": [],
    "receipt": None,
    "receipt_items": [],
    "sale_id": None,
    "logged_in": False,
    "theme": "light",
    "company": COMPANY_NAME,
    
    # Integrity Check Session States
    "integrity_results": None,
    "last_integrity_run": None,
    "active_page": "1_POS",
    
    # Multi-Tenant Session States
    "tenant_context": None,
    "shop_id": None,
    "branch_id": None,
    "tenant_role": DEFAULT_TENANT_ROLE,
    "shop_name": None,
    "branch_name": None
}

# ==========================================
# INIT SESSION
# ==========================================

def init_session():
    for key, value in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            if isinstance(value, list):
                st.session_state[key] = value.copy()
            elif isinstance(value, dict):
                st.session_state[key] = value.copy()
            else:
                st.session_state[key] = value

# ==========================================
# RESET SESSION
# ==========================================

def reset_session():
    keep_language = st.session_state.get(
        "language",
        DEFAULT_LANGUAGE
    )
    
    st.session_state.clear()
    
    init_session()
    
    st.session_state.language = keep_language

# ==========================================
# PAGE CONFIG
# ==========================================

PAGE_CONFIG = {
    "page_title": APP_NAME,
    "page_icon": "🛒",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# ==========================================
# MENU
# ==========================================

ADMIN_MENU = [
    "Dashboard",
    "POS",
    "Inventory",
    "Receipt",
    "Reports",
    "Users",
    "Refund",
    "Integrity Check"
]

MANAGER_MENU = [
    "Dashboard",
    "POS",
    "Inventory",
    "Reports",
    "Integrity Check"
]

CASHIER_MENU = [
    "POS",
    "Receipt",
    "Refund",
    "Integrity Check"
]

# ==========================================
# INTEGRITY CHECK CONFIGURATION
# ==========================================

# FIFO Cost Alert Threshold
FIFO_DEFAULT_COST_ALERT = 1.00

# Max days to check for FIFO data quality
FIFO_CHECK_DAYS = 30

# Enable/Disable specific checks
ENABLE_DOUBLE_ENTRY_CHECK = True
ENABLE_SALES_PAYMENTS_CHECK = True
ENABLE_STOCK_LEDGER_CHECK = True
ENABLE_FIFO_STOCK_CHECK = True
ENABLE_SALES_ITEMS_CHECK = True
ENABLE_FIFO_DATA_QUALITY_CHECK = True

# ==========================================
# DEBUG
# ==========================================

DEBUG = True

# ==========================================
# GET SUPABASE CONFIG
# ==========================================

def get_supabase_config():
    """Return Supabase configuration"""
    return {
        "url": SUPABASE_URL,
        "key": SUPABASE_KEY
    }

# ==========================================
# VALIDATE CONFIG
# ==========================================

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    if not SUPABASE_URL or SUPABASE_URL == "https://your-project.supabase.co":
        errors.append("SUPABASE_URL is not configured")
    
    if not SUPABASE_KEY or SUPABASE_KEY == "your-supabase-anon-key-here":
        errors.append("SUPABASE_KEY is not configured")
    
    return errors

# ==========================================
# MULTI-TENANT HELPERS
# ==========================================

def get_tenant_context():
    """Get current tenant context from session"""
    if not MULTI_TENANT_ENABLED:
        return None
    
    return {
        "shop_id": st.session_state.get("shop_id"),
        "branch_id": st.session_state.get("branch_id"),
        "tenant_role": st.session_state.get("tenant_role", DEFAULT_TENANT_ROLE),
        "shop_name": st.session_state.get("shop_name"),
        "branch_name": st.session_state.get("branch_name")
    }

def set_tenant_context(shop_id, branch_id, tenant_role, shop_name=None, branch_name=None):
    """Set current tenant context in session"""
    st.session_state.shop_id = shop_id
    st.session_state.branch_id = branch_id
    st.session_state.tenant_role = tenant_role
    st.session_state.shop_name = shop_name
    st.session_state.branch_name = branch_name
    
    st.session_state.tenant_context = {
        "shop_id": shop_id,
        "branch_id": branch_id,
        "tenant_role": tenant_role,
        "shop_name": shop_name,
        "branch_name": branch_name
    }

def clear_tenant_context():
    """Clear tenant context from session"""
    for key in TENANT_SESSION_KEYS:
        st.session_state.pop(key, None)
    
    st.session_state.tenant_context = None

# ==========================================
# PRINT CONFIG (Debug only)
# ==========================================

if DEBUG:
    print("=" * 50)
    print("📋 ERP CONFIGURATION")
    print("=" * 50)
    print(f"✅ APP_NAME: {APP_NAME}")
    print(f"✅ SUPABASE_URL: {SUPABASE_URL[:30]}..." if SUPABASE_URL else "❌ SUPABASE_URL: Not Set")
    print(f"✅ SUPABASE_KEY: {SUPABASE_KEY[:15]}..." if SUPABASE_KEY else "❌ SUPABASE_KEY: Not Set")
    print(f"✅ MULTI_TENANT_ENABLED: {MULTI_TENANT_ENABLED}")
    print(f"✅ DEBUG: {DEBUG}")
    print("=" * 50)
