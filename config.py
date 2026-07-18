# ==========================================
# config.py
# Production Ready Configuration
# ==========================================

from pathlib import Path
import streamlit as st

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

    "company": COMPANY_NAME
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

    "Refund"

]

MANAGER_MENU = [

    "Dashboard",

    "POS",

    "Inventory",

    "Reports"

]

CASHIER_MENU = [

    "POS",

    "Receipt",

    "Refund"

]

# ==========================================
# DEBUG
# ==========================================

DEBUG = True
