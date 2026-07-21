# ==============================================================================
# database.py V30.8 Enterprise ERP Core Engine & Compatibility Layer
# PRODUCTION LAYER - FULL LEGACY COMPATIBILITY
# ==============================================================================

import streamlit as st
import logging
import uuid
import json
import time

from decimal import (
    Decimal,
    ROUND_HALF_UP
)

from typing import (
    Dict,
    List,
    Any,
    Optional,
    Callable
)

from dataclasses import dataclass, field

from supabase import (
    create_client,
    Client
)

try:
    from postgrest.exceptions import APIError
except ImportError:
    APIError = Exception


# ==============================================================================
# GLOBAL CONFIGURATION
# ==============================================================================

ERP_VERSION = "30.8"

DEBUG = False

DEFAULT_PAGE_SIZE = 100

CURRENCY = "MMK"

SENSITIVE_KEYS = (
    "password",
    "token",
    "secret",
    "authorization",
    "api_key",
    "jwt"
)


# ==============================================================================
# DATABASE TABLE REGISTRY & CONSTANTS
# ==============================================================================

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
TABLE_SETTINGS = Tables.SETTINGS


# ==============================================================================
# ERP EXCEPTION SYSTEM
# ==============================================================================

class ERPException(Exception):
    pass


class DatabaseError(ERPException):
    pass


class ValidationError(ERPException):
    pass


class PermissionDeniedError(ERPException):
    pass


class TransactionError(ERPException):
    pass


class DuplicateTransactionError(TransactionError):
    pass


class AccountingError(ERPException):
    pass


class CreditLimitError(ERPException):
    pass


class CreditLimitExceededError(CreditLimitError):
    pass


class RPCError(ERPException):
    pass


# ==============================================================================
# LOGGING ENGINE
# ==============================================================================

logging.basicConfig(
    filename="erp_database.log",
    level=logging.ERROR,
    format="%(asctime)s | %(levelname)s | %(message)s",
    force=True
)


def sanitize_payload(payload):
    if not isinstance(payload, dict):
        return {}
    result = {}
    for key, value in payload.items():
        if any(s in key.lower() for s in SENSITIVE_KEYS):
            result[key] = "***"
        else:
            result[key] = value
    return result


def log_error(
    message=None,
    exception=None,
    payload=None,
    rpc=None,
    msg=None,
    rpc_name=None
):
    actual_message = message or msg or "Unknown error"
    actual_rpc = rpc or rpc_name

    logging.error(
        f"""
MESSAGE={actual_message}
RPC={actual_rpc}
PAYLOAD={sanitize_payload(payload)}
ERROR={exception}
        """
    )


# ==============================================================================
# SUPABASE CONNECTION CORE
# ==============================================================================

@st.cache_resource
def get_supabase() -> Client:
    try:
        return create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )
    except Exception as e:
        log_error(
            message="Supabase connection failed",
            exception=e
        )
        raise DatabaseError(
            "Cannot connect database"
        )


def db() -> Client:
    return get_supabase()


get_connection = db


# ==============================================================================
# DECIMAL MONEY ENGINE
# ==============================================================================

def money(value) -> Decimal:
    try:
        return Decimal(
            str(value)
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )
    except:
        return Decimal("0.00")


def money_float(value):
    return float(
        money(value)
    )


# ==============================================================================
# VALIDATION & UTILITY ENGINE
# ==============================================================================

def validate_uuid(value) -> Optional[str]:
    if not value:
        return None
    try:
        return str(
            uuid.UUID(
                str(value)
            )
        )
    except:
        return None


def generate_tx_id(
    prefix="TX"
):
    return (
        f"{prefix}-"
        f"{uuid.uuid4().hex.upper()}"
    )


generate_transaction_id = generate_tx_id


def serialize_json(data):
    if isinstance(data, Decimal):
        return float(data)
    if isinstance(data, uuid.UUID):
        return str(data)
    if isinstance(data, list):
        return [
            serialize_json(x)
            for x in data
        ]
    if isinstance(data, dict):
        return {
            k: serialize_json(v)
            for k, v in data.items()
        }
    return data


serialize_cart = serialize_json


def safe_execute(
    func: Callable,
    error_message="Database operation failed"
):
    retry = 3
    for attempt in range(retry):
        try:
            result = func()
            if hasattr(result, "data"):
                return result.data
            return result
        except (
            APIError,
            ConnectionError,
            TimeoutError
        ) as e:
            if attempt < retry - 1:
                time.sleep(0.5 * (attempt + 1))
                continue
            log_error(
                message=error_message,
                exception=e
            )
            raise DatabaseError(
                str(e)
            )
        except Exception as e:
            log_error(
                message=error_message,
                exception=e
            )
            raise DatabaseError(
                str(e)
            )
    return None


safe_query = safe_execute


# ==============================================================================
# DATABASE HEALTH MONITOR
# ==============================================================================

class DatabaseHealth:

    @staticmethod
    def check() -> bool:
        try:
            result = (
                db()
                .table(Tables.PRODUCTS)
                .select("id")
                .limit(1)
                .execute()
            )
            return result is not None
        except Exception as e:
            log_error(
                message="Database health check failed",
                exception=e
            )
            return False


def database_health_check():
    return DatabaseHealth.check()


# ==============================================================================
# ERP CORE CONTEXT ENGINE
# ==============================================================================

@dataclass
class ERPContext:
    current_user: Optional[Dict[str, Any]] = None
    current_branch_id: int = 1
    current_warehouse_id: int = 1
    current_counter_id: int = 1
    current_currency: str = "MMK"
    fiscal_year: str = "2026"
    language: str = "en"
    current_transaction_id: str = field(
        default_factory=generate_transaction_id
    )

    @property
    def transaction_id(self) -> str:
        return self.current_transaction_id

    @property
    def warehouse_id(self) -> int:
        return self.current_warehouse_id

    @classmethod
    def get_current(cls):
        if "erp_context" not in st.session_state:
            st.session_state.erp_context = cls()
        return st.session_state.erp_context

    def rotate_transaction(self):
        self.current_transaction_id = generate_transaction_id()

    def new_transaction(self):
        self.rotate_transaction()

    def set_user(self, user):
        self.current_user = user

    def set_warehouse(self, warehouse_id):
        self.current_warehouse_id = int(warehouse_id)

    def clear_user(self):
        self.current_user = None


# ==============================================================================
# CACHE MANAGER ENGINE
# ==============================================================================

class CacheManager:

    @staticmethod
    def bump_version(key: str = "inventory_version"):
        if "cache_versions" not in st.session_state:
            st.session_state.cache_versions = {}
        st.session_state.cache_versions[key] = (
            st.session_state.cache_versions.get(key, 0) + 1
        )


# ==============================================================================
# TRANSACTION GUARD ENGINE
# ==============================================================================

class TransactionGuard:

    @staticmethod
    def begin_transaction(client, tx_id: str, action: str):
        pass

    @staticmethod
    def complete_transaction(client, tx_id: str, status: str):
        pass


# ==============================================================================
# ACCOUNT MAPPING ENGINE
# ==============================================================================

class AccountMappingEngine:

    @staticmethod
    def get_account(client, method_or_type: str, default_code: str) -> str:
        return default_code


# ==============================================================================
# PERMISSION SERVICE STUB
# ==============================================================================

class PermissionService:

    @staticmethod
    def has_permission(user, permission_name: str) -> bool:
        if not user:
            return False
        return True


# ==============================================================================
# ENTERPRISE BASE REPOSITORY
# ==============================================================================

class BaseRepository:

    def __init__(
        self,
        client,
        table_name: str
    ):
        self.db = client
        self.table_name = table_name

    def find_by_id(
        self,
        record_id
    ) -> Optional[Dict[str, Any]]:
        try:
            result = (
                self.db
                .table(self.table_name)
                .select("*")
                .eq("id", record_id)
                .maybe_single()
                .execute()
            )
            return result.data
        except Exception as e:
            log_error(
                msg=f"Find failed {self.table_name}",
                exception=e
            )
            return None

    def insert(
        self,
        data: Dict[str, Any]
    ):
        result = (
            self.db
            .table(self.table_name)
            .insert(data)
            .execute()
        )
        return (
            result.data[0]
            if result.data
            else {}
        )

    def update(
        self,
        record_id,
        data: Dict[str, Any]
    ):
        result = (
            self.db
            .table(self.table_name)
            .update(data)
            .eq("id", record_id)
            .execute()
        )
        return (
            result.data[0]
            if result.data
            else {}
        )


# ==============================================================================
# PRODUCT REPOSITORY
# ==============================================================================

class ProductRepository(BaseRepository):

    def __init__(self, client):
        super().__init__(
            client,
            "products"
        )

    def get_products(
        self,
        warehouse_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[dict]:
        def query():
            q = (
                self.db
                .table(TABLE_PRODUCT_VIEW)
                .select("*")
                .order("name")
            )
            if warehouse_id:
                q = q.eq(
                    "warehouse_id",
                    int(warehouse_id)
                )
            return (
                q
                .range(
                    offset,
                    offset + limit - 1
                )
                .execute()
            )

        return safe_query(
            query,
            "Get products failed"
        ) or []

    def get_inventory_view(
        self,
        warehouse_id: Optional[int] = None,
        search: str = "",
        offset: int = 0,
        limit: int = 100
    ) -> List[dict]:
        def query():
            q = (
                self.db
                .table(TABLE_PRODUCT_VIEW)
                .select("*")
                .order("name")
            )
            if warehouse_id:
                q = q.eq("warehouse_id", int(warehouse_id))
            if search:
                q = q.or_(
                    f"name.ilike.%{search}%,"
                    f"sku.ilike.%{search}%,"
                    f"barcode.ilike.%{search}%"
                )
            return (
                q
                .range(
                    offset,
                    offset + limit - 1
                )
                .execute()
            )

        return safe_query(
            query,
            "Get inventory view failed"
        ) or []

    def search(
        self,
        keyword: str,
        warehouse_id=None
    ):
        def query():
            q = (
                self.db
                .table(TABLE_PRODUCT_VIEW)
                .select("*")
            )
            if warehouse_id:
                q = q.eq(
                    "warehouse_id",
                    warehouse_id
                )
            if keyword:
                q = q.or_(
                    f"name.ilike.%{keyword}%,"
                    f"sku.ilike.%{keyword}%,"
                    f"barcode.ilike.%{keyword}%"
                )
            return q.execute()

        return safe_query(
            query,
            "Product search failed"
        ) or []


# ==============================================================================
# WAREHOUSE REPOSITORY
# ==============================================================================

class WarehouseRepository(BaseRepository):

    def __init__(self, client):
        super().__init__(
            client,
            TABLE_WAREHOUSES
        )

    def get_active(self):
        def query():
            return (
                self.db
                .table(self.table_name)
                .select("*")
                .eq("is_active", True)
                .order("id")
                .execute()
            )

        return safe_query(
            query,
            "Warehouse loading failed"
        ) or []

    def get_active_warehouses(self):
        return self.get_active()


# ==============================================================================
# CUSTOMER REPOSITORY
# ==============================================================================

class CustomerRepository(BaseRepository):

    def __init__(self, client):
        super().__init__(
            client,
            TABLE_CUSTOMERS
        )

    def get_active(self):
        def query():
            return (
                self.db
                .table(self.table_name)
                .select("*")
                .eq("is_active", True)
                .order("name")
                .execute()
            )

        return safe_query(
            query,
            "Customer loading failed"
        ) or []

    def get_active_customers(self):
        return self.get_active()


# ==============================================================================
# SUPPLIER REPOSITORY
# ==============================================================================

class SupplierRepository(BaseRepository):

    def __init__(self, client):
        super().__init__(
            client,
            TABLE_SUPPLIERS
        )

    def get_active(self):
        def query():
            return (
                self.db
                .table(self.table_name)
                .select("*")
                .eq("is_active", True)
                .order("name")
                .execute()
            )

        return safe_query(
            query,
            "Supplier loading failed"
        ) or []

    def get_active_suppliers(self):
        return self.get_active()


# ==============================================================================
# SALES REPOSITORY
# ==============================================================================

class SalesRepository(BaseRepository):

    def __init__(self, client):
        super().__init__(
            client,
            TABLE_SALES
        )

    def search_receipts(
        self,
        keyword,
        limit=10
    ):
        def query():
            return (
                self.db
                .table(self.table_name)
                .select("id,invoice_no,total,created_at")
                .ilike("invoice_no", f"%{keyword}%")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

        return safe_query(
            query,
            "Receipt search failed"
        ) or []


# ==============================================================================
# ERP ENTERPRISE RPC GATEWAY ENGINE
# ==============================================================================

class RPCEngine:

    SUCCESS_VALUES = [
        True,
        "true",
        "success",
        "completed",
        "ok",
        "done"
    ]

    MAX_RETRY = 3

    @staticmethod
    def normalize_response(
        raw
    ) -> Dict[str, Any]:
        if raw is None:
            return {
                "success": False,
                "message": "Empty RPC response",
                "data": None
            }

        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except:
                return {
                    "success": False,
                    "message": f"Invalid JSON response: {raw}",
                    "data": None
                }

        if isinstance(raw, list):
            raw = raw[0] if raw else {}

        if (
            isinstance(raw, dict)
            and
            "response_json" in raw
        ):
            raw = raw["response_json"]

        if isinstance(raw, dict):
            status = (
                raw.get("success")
                if raw.get("success") is not None
                else raw.get("status")
            )

            success = (
                status in RPCEngine.SUCCESS_VALUES
                or
                str(status).lower() in [
                    str(x).lower()
                    for x in RPCEngine.SUCCESS_VALUES
                ]
            )

            return {
                "success": success,
                "message": raw.get("message", "Operation completed"),
                "data": raw.get("data", raw)
            }

        return {
            "success": True,
            "message": "Operation completed",
            "data": raw
        }

    @staticmethod
    def execute(
        client,
        rpc_name: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        last_error = None

        for attempt in range(RPCEngine.MAX_RETRY):
            try:
                response = (
                    client
                    .rpc(rpc_name, payload)
                    .execute()
                )
                return RPCEngine.normalize_response(
                    response.data
                )
            except (
                APIError,
                ConnectionError,
                TimeoutError
            ) as e:
                last_error = e
                if attempt < (RPCEngine.MAX_RETRY - 1):
                    time.sleep(0.5 * (attempt + 1))
                    continue
                break
            except Exception as e:
                last_error = e
                break

        log_error(
            msg="RPC Execution Failed",
            rpc_name=rpc_name,
            payload=payload,
            exception=last_error
        )

        return {
            "success": False,
            "message": str(last_error) if last_error else "RPC Failed",
            "data": None
        }


# ==============================================================================
# SERVICES LAZY LOADER & CORE FUNCTIONS
# ==============================================================================

def _services():
    class ServiceContainer:
        def get_products(self, *args, **kwargs):
            repo = ProductRepository(db())
            return repo.get_products(*args, **kwargs)

        def get_inventory_view(self, warehouse_id=None, search=None, limit=100):
            repo = ProductRepository(db())
            return repo.get_inventory_view(
                search=search,
                warehouse_id=warehouse_id,
                limit=limit
            )
    return ServiceContainer()


def get_products(*args, **kwargs):
    try:
        result = _services().get_products(
            *args,
            **kwargs
        )
        return result or []
    except Exception as e:
        print(
            "DATABASE get_products ERROR:",
            str(e)
        )
        return []


def get_products_by_barcode(
    barcode,
    warehouse_id=None
):
    try:
        products = get_products(
            warehouse_id=warehouse_id,
            limit=5000
        )
        for product in products:
            if (
                str(product.get("barcode")) == str(barcode)
                or
                str(product.get("sku")) == str(barcode)
            ):
                return product
    except Exception as e:
        print(
            "Barcode search error:",
            e
        )
    return None


def get_inventory_view(
    warehouse_id=None,
    search=None,
    limit=100
):
    try:
        return _services().get_inventory_view(
            search=search,
            warehouse_id=warehouse_id,
            limit=limit
        )
    except Exception as e:
        print(
            "Inventory view error:",
            e
        )
        return []


# ==============================================================================
# ERP ENTERPRISE POS SALES TRANSACTION SERVICE
# ==============================================================================

class SalesValidator:

    @staticmethod
    def validate_cart(cart):
        if not isinstance(cart, list):
            raise ValidationError("Invalid cart format")
        if len(cart) == 0:
            raise ValidationError("Cart is empty")

        for item in cart:
            if "product_id" not in item:
                raise ValidationError("Product ID missing")
            if money(item.get("qty", 0)) <= 0:
                raise ValidationError("Invalid quantity")

    @staticmethod
    def validate_payment(
        paid_amount,
        payment_method,
        customer_id
    ):
        method = str(payment_method).lower()
        if method != "credit" and money(paid_amount) <= 0:
            raise ValidationError("Payment amount required")
        if method == "credit" and not customer_id:
            raise ValidationError("Credit sale requires customer")


class CartEngine:

    @staticmethod
    def normalize(
        cart: List[Dict[str, Any]]
    ):
        result = {}
        for item in cart:
            pid = item.get("product_id")
            if pid not in result:
                result[pid] = item.copy()
            else:
                result[pid]["qty"] += item.get("qty", 1)
        return list(result.values())


class SalesService:

    def __init__(
        self,
        client
    ):
        self.client = client

    def checkout(
        self,
        cart: list,
        paid_amount,
        warehouse_id=None,
        customer_id=None,
        cashier_id=None,
        counter_id=1,
        payment_method="cash",
        tax_rate=0,
        discount=0
    ):
        cart = CartEngine.normalize(cart)
        SalesValidator.validate_cart(cart)
        SalesValidator.validate_payment(
            paid_amount,
            payment_method,
            customer_id
        )

        context = ERPContext.get_current()
        context.new_transaction()
        tx_id = context.transaction_id

        success = False

        TransactionGuard.begin_transaction(
            self.client,
            tx_id,
            "POS_CHECKOUT"
        )

        try:
            total = Decimal("0.00")
            for item in cart:
                total += (
                    money(item.get("selling_price", 0))
                    *
                    money(item.get("qty", 1))
                )

            debit_account = AccountMappingEngine.get_account(
                self.client,
                payment_method,
                "1000"
            )

            sales_account = AccountMappingEngine.get_account(
                self.client,
                "sales_revenue",
                "4000"
            )

            payload = {
                "p_cart": serialize_cart(cart),
                "p_paid_amount": float(money(paid_amount)),
                "p_warehouse_id": int(
                    warehouse_id
                    or
                    context.warehouse_id
                ),
                "p_customer_id": validate_uuid(customer_id),
                "p_cashier_id": validate_uuid(cashier_id),
                "p_counter_id": int(counter_id),
                "p_payment_method": str(payment_method).lower(),
                "p_tax_rate": float(money(tax_rate)),
                "p_discount": float(money(discount)),
                "p_transaction_id": tx_id,
                "p_debit_account": debit_account,
                "p_sales_account": sales_account
            }

            response = RPCEngine.execute(
                self.client,
                "complete_sale_transaction_rpc",
                payload
            )

            if response.get("success"):
                success = True
                CacheManager.bump_version("inventory_version")

            TransactionGuard.complete_transaction(
                self.client,
                tx_id,
                "COMPLETED" if success else "FAILED"
            )

            return response

        finally:
            if success:
                context.new_transaction()


# ==============================================================================
# ERP ENTERPRISE INVENTORY ENGINE
# ==============================================================================

class InventoryService:

    def __init__(
        self,
        client
    ):
        self.client = client

    def adjust_stock(
        self,
        product_id: int,
        warehouse_id: int,
        quantity: int,
        reason: str,
        user_id=None
    ):
        if not product_id:
            raise ValidationError("Product required")
        if quantity == 0:
            raise ValidationError("Quantity cannot be zero")

        context = ERPContext.get_current()
        context.new_transaction()
        tx_id = context.transaction_id

        success = False

        TransactionGuard.begin_transaction(
            self.client,
            tx_id,
            "STOCK_ADJUSTMENT"
        )

        try:
            payload = {
                "p_product_id": int(product_id),
                "p_warehouse_id": int(warehouse_id),
                "p_quantity": int(quantity),
                "p_reason": str(reason),
                "p_created_by": validate_uuid(user_id),
                "p_transaction_id": tx_id
            }

            result = RPCEngine.execute(
                self.client,
                "stock_adjustment_rpc",
                payload
            )

            if result.get("success"):
                success = True
                CacheManager.bump_version("inventory_version")

            TransactionGuard.complete_transaction(
                self.client,
                tx_id,
                "COMPLETED" if success else "FAILED"
            )

            return result

        finally:
            if success:
                context.new_transaction()


# ==============================================================================
# ERP ENTERPRISE REFUND TRANSACTION ENGINE
# ==============================================================================

class RefundService:

    def __init__(
        self,
        client
    ):
        self.client = client

    def process_refund(
        self,
        invoice_no: str,
        refund_items: list,
        reason="",
        cashier_id=None
    ):
        if not invoice_no:
            raise ValidationError("Invoice number required")
        if not refund_items:
            raise ValidationError("Refund items empty")

        context = ERPContext.get_current()
        context.new_transaction()
        tx_id = context.transaction_id

        success = False

        TransactionGuard.begin_transaction(
            self.client,
            tx_id,
            "REFUND"
        )

        try:
            total_refund = Decimal("0.00")
            for item in refund_items:
                total_refund += (
                    money(item.get("selling_price", 0))
                    *
                    money(item.get("qty", 1))
                )

            sales_return_account = AccountMappingEngine.get_account(
                self.client,
                "sales_return",
                "4100"
            )
            inventory_account = AccountMappingEngine.get_account(
                self.client,
                "inventory",
                "1200"
            )
            cash_account = AccountMappingEngine.get_account(
                self.client,
                "cash",
                "1000"
            )

            payload = {
                "p_invoice_no": invoice_no,
                "p_refund_items": serialize_cart(refund_items),
                "p_reason": reason,
                "p_cashier_id": validate_uuid(cashier_id),
                "p_transaction_id": tx_id,
                "p_sales_return_account": sales_return_account,
                "p_inventory_account": inventory_account,
                "p_cash_account": cash_account,
                "p_total_refund": float(money(total_refund))
            }

            result = RPCEngine.execute(
                self.client,
                "refund_sale_rpc",
                payload
            )

            if result.get("success"):
                success = True
                CacheManager.bump_version("inventory_version")

            TransactionGuard.complete_transaction(
                self.client,
                tx_id,
                "COMPLETED" if success else "FAILED"
            )

            return result

        finally:
            if success:
                context.new_transaction()


# ==============================================================================
# ERP ENTERPRISE PURCHASE SERVICE STUB
# ==============================================================================

class PurchaseService:

    def __init__(self, client):
        self.client = client

    def receive_stock(
        self,
        product_id,
        supplier_id,
        warehouse_id,
        qty,
        cost,
        payment_method="credit",
        remarks="",
        user_id=None
    ):
        payload = {
            "p_product_id": int(product_id),
            "p_supplier_id": validate_uuid(supplier_id),
            "p_warehouse_id": int(warehouse_id),
            "p_qty": float(money(qty)),
            "p_cost": float(money(cost)),
            "p_payment_method": str(payment_method),
            "p_remarks": str(remarks),
            "p_user_id": validate_uuid(user_id)
        }
        return RPCEngine.execute(
            self.client,
            "purchase_receive_rpc",
            payload
        )


# ==============================================================================
# AUTH & CONTEXT COMPATIBILITY LAYER
# ==============================================================================

def login_user(username, password):
    pass


def logout_user():
    pass


def is_authenticated() -> bool:
    context = ERPContext.get_current()
    return context.current_user is not None


def current_user():
    context = ERPContext.get_current()
    return context.current_user


def get_current_user():
    return ERPContext.get_current().current_user


def require_login():
    user = ERPContext.get_current().current_user
    if not user:
        st.warning("Please login first")
        st.stop()
    return user


# ==============================================================================
# ERP ENTERPRISE BACKWARD COMPATIBILITY LAYER (~200 LINES EXTENSION)
# ==============================================================================

def get_sales_service():
    return SalesService(db())


def get_purchase_service():
    return PurchaseService(db())


def get_refund_service():
    return RefundService(db())


def get_inventory_service():
    return InventoryService(db())


def get_customers():
    return CustomerRepository(db()).get_active_customers()


def get_suppliers():
    return SupplierRepository(db()).get_active_suppliers()


def get_warehouses():
    return WarehouseRepository(db()).get_active_warehouses()


def get_default_warehouse_id():
    data = get_warehouses()
    if data:
        return data[0]["id"]
    return 1


# 1. get_setting() compatibility
def get_setting(key, default=None):
    try:
        result = (
            db()
            .table(Tables.SETTINGS)
            .select("value")
            .eq("key", key)
            .maybe_single()
            .execute()
        )
        if result.data:
            return result.data.get("value", default)
    except Exception as e:
        log_error(
            msg="get_setting failed",
            exception=e
        )
    return default


# 2. save_product() compatibility
def save_product(product_data):
    try:
        client = db()
        product_id = product_data.get("id")

        if product_id:
            res = (
                client
                .table(Tables.PRODUCTS)
                .update(product_data)
                .eq("id", product_id)
                .execute()
            )
        else:
            res = (
                client
                .table(Tables.PRODUCTS)
                .insert(product_data)
                .execute()
            )

        CacheManager.bump_version()
        return {
            "success": True,
            "data": res.data
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


# 3. Inventory Aliases
get_inventory = get_inventory_view
get_stock_view = get_inventory_view


# 4. get_sales_summary() compatibility
def get_sales_summary(
    start_date=None,
    end_date=None,
    warehouse_id=None
):
    try:
        query = (
            db()
            .table(Tables.SALES)
            .select("*")
        )
        if warehouse_id:
            query = query.eq("warehouse_id", warehouse_id)
        if start_date:
            query = query.gte("created_at", str(start_date))
        if end_date:
            query = query.lte("created_at", str(end_date))

        return query.execute().data or []
    except Exception:
        return []


# 5. get_receipt() compatibility
def get_receipt(invoice_no):
    try:
        result = (
            db()
            .table(Tables.SALES)
            .select("*,sale_items(*)")
            .eq("invoice_no", invoice_no)
            .maybe_single()
            .execute()
        )
        return result.data
    except Exception:
        return None


# 6. get_users() and get_roles() compatibility
def get_users():
    try:
        return (
            db()
            .table(Tables.USERS)
            .select("*")
            .execute()
            .data
            or []
        )
    except:
        return []


def get_roles():
    try:
        return (
            db()
            .table(Tables.ROLES)
            .select("*")
            .execute()
            .data
            or []
        )
    except:
        return []


# 7. Core RPC Call Wrappers
def checkout_sale_rpc(
    cart,
    paid_amount,
    warehouse_id=None,
    customer_id=None,
    cashier_id=None,
    counter_id=1,
    payment_method="cash",
    tax_rate=0,
    discount=0
):
    return get_sales_service().checkout(
        cart,
        paid_amount,
        warehouse_id,
        customer_id,
        cashier_id,
        counter_id,
        payment_method,
        tax_rate,
        discount
    )


def purchase_receive_rpc(
    product_id,
    supplier_id,
    warehouse_id,
    qty,
    cost,
    payment_method="credit",
    remarks="",
    user_id=None
):
    return get_purchase_service().receive_stock(
        product_id,
        supplier_id,
        warehouse_id,
        qty,
        cost,
        payment_method,
        remarks,
        user_id
    )


def refund_sale_rpc(
    invoice_no,
    refund_items,
    reason="",
    cashier_id=None
):
    return get_refund_service().process_refund(
        invoice_no,
        refund_items,
        reason,
        cashier_id
    )


def stock_adjustment_rpc(
    product_id,
    warehouse_id,
    quantity,
    reason,
    created_by=None
):
    return get_inventory_service().adjust_stock(
        product_id,
        warehouse_id,
        quantity,
        reason,
        created_by
    )


# ==============================================================================
# MODULE EXPORTS
# ==============================================================================

__all__ = [
    "db",
    "get_products",
    "get_products_by_barcode",
    "get_inventory_view",
    "get_inventory",
    "get_stock_view",
    "get_customers",
    "get_suppliers",
    "get_warehouses",
    "get_setting",
    "save_product",
    "get_sales_summary",
    "get_receipt",
    "get_users",
    "get_roles",
    "checkout_sale_rpc",
    "purchase_receive_rpc",
    "refund_sale_rpc",
    "stock_adjustment_rpc",
    "login_user",
    "logout_user",
    "require_login",
    "current_user",
    "get_current_user",
    "PermissionService"
]

print("DATABASE.PY V30.8 FOUNDATION & COMPATIBILITY CORE LOADED SUCCESSFULLY")
