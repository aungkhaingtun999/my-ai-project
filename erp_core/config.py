# erp_core/config.py
import logging

ERP_VERSION = "30.0"
DEBUG = False
DEFAULT_PAGE_SIZE = 100
CURRENCY = "MMK"
SENSITIVE_KEYS = ("password", "token", "secret", "authorization", "api_key", "jwt")

class Tables:
    PRODUCTS = "products"
    PRODUCT_VIEW = "pos_products_view"
    WAREHOUSES = "warehouses"
    WAREHOUSE_STOCK = "warehouse_stock"
    SALES = "sales"
    SALE_ITEMS = "sale_items"
    PURCHASES = "purchases"
    PURCHASE_ITEMS = "purchase_items"
    REFUNDS = "refunds"
    REFUND_ITEMS = "refund_items"
    CUSTOMERS = "customers"
    SUPPLIERS = "suppliers"
    USERS = "users"
    ROLES = "roles"
    PERMISSIONS = "permissions"
    ROLE_PERMISSIONS = "role_permissions"
    SETTINGS = "erp_settings"
    INVENTORY_LEDGER = "inventory_ledgers"
    COST_TRANSACTIONS = "inventory_cost_transactions"
    ACCOUNT_JOURNALS = "accounting_journals"
    ACCOUNT_ENTRIES = "accounting_entries"
    CHART_OF_ACCOUNTS = "chart_of_accounts"
    AUDIT_LOGS = "audit_logs"
    TRANSACTIONS = "erp_transactions"
    SYNC_QUEUE = "sync_queue"

TABLE_USERS = Tables.USERS
TABLE_ROLE_PERMISSIONS = Tables.ROLE_PERMISSIONS
TABLE_PRODUCT_VIEW = Tables.PRODUCT_VIEW
TABLE_WAREHOUSES = Tables.WAREHOUSES
TABLE_CUSTOMERS = Tables.CUSTOMERS
TABLE_SUPPLIERS = Tables.SUPPLIERS
TABLE_SALES = Tables.SALES

logging.basicConfig(
    filename="erp_database.log",
    level=logging.ERROR,
    format="%(asctime)s | %(levelname)s | %(message)s",
    force=True
)

def sanitize_payload(payload):
    if not isinstance(payload, dict): return {}
    return {k: ("***" if any(s in k.lower() for s in SENSITIVE_KEYS) else v) for k, v in payload.items()}

def log_error(message=None, exception=None, payload=None, rpc=None, msg=None, rpc_name=None):
    actual_message = message or msg or "Unknown error"
    actual_rpc = rpc or rpc_name
    logging.error(f"MESSAGE={actual_message} | RPC={actual_rpc} | PAYLOAD={sanitize_payload(payload)} | ERROR={exception}")
