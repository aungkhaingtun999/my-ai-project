# ==============================================================================
# erp_core/services.py
# ERP ENTERPRISE SERVICE LAYER V30 STABLE
# PART 1/3
# ==============================================================================


import streamlit as st

from decimal import Decimal

from typing import (
    List,
    Dict,
    Any,
    Optional
)


from .config import (
    Tables,
    TABLE_PRODUCT_VIEW,
    DEFAULT_PAGE_SIZE
)


from .base_repo import (
    db,
    money,
    validate_uuid,
    serialize_json
)


from .context import (
    ERPContext,
    CacheManager
)


from .rpc_engine import RPCEngine


from .exceptions import (
    AccountingError,
    CreditLimitExceededError,
    ValidationError
)


from .repositories import (
    RepositoryCoordinator
)



# ==============================================================================
# SETTINGS
# ==============================================================================


def get_setting(
    key: str,
    default=None
):

    """
    ERP Settings Reader
    """

    try:

        result = (
            db()
            .table(
                Tables.SETTINGS
            )
            .select("*")
            .eq(
                "key",
                key
            )
            .maybe_single()
            .execute()
        )


        if result.data:

            return result.data.get(
                "value",
                default
            )


    except Exception:

        pass


    return default





# ==============================================================================
# ACCOUNTING SERVICE
# ==============================================================================


class AccountingLedgerService:


    def __init__(
        self,
        client: Any
    ):

        self.client = client



    def post_journal_entry(
        self,
        tx_id: str,
        description: str,
        entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:


        debit = sum(
            money(
                item.get(
                    "debit",
                    0
                )
            )
            for item in entries
        )


        credit = sum(
            money(
                item.get(
                    "credit",
                    0
                )
            )
            for item in entries
        )


        if debit != credit:

            raise AccountingError(
                f"Debit {debit} != Credit {credit}"
            )



        return RPCEngine.execute(
            self.client,
            "post_journal_entry_rpc",
            {

                "p_transaction_id":
                    tx_id,


                "p_description":
                    description,


                "p_entries":
                    serialize_json(
                        entries
                    )

            }
        )





# ==============================================================================
# CUSTOMER SERVICE
# ==============================================================================


class CustomerService:


    def __init__(
        self,
        client: Any
    ):

        self.client = client



    def check_credit_limit(
        self,
        customer_id: str,
        sale_amount: Decimal
    ) -> bool:


        if not customer_id:

            return True


        try:

            result = (

                self.client
                .table(
                    Tables.CUSTOMERS
                )
                .select(
                    "credit_limit,current_balance"
                )
                .eq(
                    "id",
                    customer_id
                )
                .maybe_single()
                .execute()

            )


            if not result.data:

                return True



            limit = money(
                result.data.get(
                    "credit_limit",
                    0
                )
            )


            balance = money(
                result.data.get(
                    "current_balance",
                    0
                )
            )



            if (

                limit > Decimal("0.00")

                and

                balance + sale_amount > limit

            ):

                raise CreditLimitExceededError(
                    "Customer credit limit exceeded"
                )


            return True



        except CreditLimitExceededError:

            raise


        except Exception:

            return True





# ==============================================================================
# SALES SERVICE
# ==============================================================================


class SalesService:


    def __init__(
        self,
        client: Any
    ):

        self.client = client

        self.customer_service = (
            CustomerService(
                client
            )
        )



    def checkout(
        self,
        cart: list,
        paid_amount: Any,
        warehouse_id: Optional[int] = None,
        customer_id: Optional[str] = None,
        cashier_id: Optional[str] = None,
        counter_id: int = 1,
        payment_method: str = "cash",
        tax_rate: Any = 0,
        discount: Any = 0

    ) -> Dict[str, Any]:


        if not cart:

            raise ValidationError(
                "Cart cannot be empty"
            )


        context = ERPContext.get_current()


        context.rotate_transaction()


        tx_id = (
            context.current_transaction_id
        )


        success = False



        try:


            current_warehouse = (

                warehouse_id

                if warehouse_id is not None

                else

                context.current_warehouse_id

            )



            total_sale = sum(

                money(
                    item.get(
                        "selling_price",
                        0
                    )
                )

                *

                money(
                    item.get(
                        "qty",
                        1
                    )
                )

                for item in cart

            )



            if str(payment_method).lower() == "credit":

                self.customer_service.check_credit_limit(
                    customer_id,
                    total_sale
                )



            payload = {

                "p_cart":
                    serialize_json(cart),


                "p_paid_amount":
                    float(
                        money(
                            paid_amount
                        )
                    ),


                "p_warehouse_id":
                    int(
                        current_warehouse
                    ),


                "p_customer_id":
                    validate_uuid(
                        customer_id
                    ),


                "p_cashier_id":
                    validate_uuid(
                        cashier_id
                    ),


                "p_counter_id":
                    int(
                        counter_id
                    ),


                "p_payment_method":
                    str(
                        payment_method
                    ).lower(),


                "p_tax_rate":
                    float(
                        money(
                            tax_rate
                        )
                    ),


                "p_discount":
                    float(
                        money(
                            discount
                        )
                    ),


                "p_transaction_id":
                    tx_id

            }


            result = RPCEngine.execute(
                self.client,
                "complete_sale_transaction_rpc",
                payload
            )


            if result.get("success"):

                success = True

                CacheManager.bump_version(
                    "inventory_version"
                )


            return result



        finally:


            if success:

                pass





# ==============================================================================
# INVENTORY SERVICE
# ==============================================================================


class InventoryService:


    def __init__(
        self,
        client: Any
    ):

        self.client = client



    def adjust_stock(
        self,
        product_id: int,
        warehouse_id: int,
        quantity: int,
        reason: str,
        user_id: Optional[str] = None

    ) -> Dict[str, Any]:


        context = ERPContext.get_current()

        context.rotate_transaction()

        tx_id = context.current_transaction_id



        result = RPCEngine.execute(

            self.client,

            "stock_adjustment_rpc",

            {

                "p_product_id":
                    int(product_id),


                "p_warehouse_id":
                    int(warehouse_id),


                "p_quantity":
                    int(quantity),


                "p_reason":
                    str(reason),


                "p_created_by":
                    validate_uuid(user_id),


                "p_transaction_id":
                    tx_id

            }

        )


        if result.get("success"):

            CacheManager.bump_version(
                "inventory_version"
            )


        return result





# ==============================================================================
# PURCHASE SERVICE
# ==============================================================================


class PurchaseService:


    def __init__(
        self,
        client: Any
    ):

        self.client = client



    def receive_stock(
        self,
        product_id: int,
        supplier_id: int,
        warehouse_id: int,
        qty: int,
        cost: Any,
        payment_method: str = "credit",
        remarks: str = "",
        user_id: Optional[str] = None

    ) -> Dict[str, Any]:


        context = ERPContext.get_current()

        context.rotate_transaction()

        tx_id = context.current_transaction_id



        result = RPCEngine.execute(

            self.client,

            "purchase_receive_rpc",

            {

                "p_product_id":
                    int(product_id),


                "p_supplier_id":
                    int(supplier_id),


                "p_warehouse_id":
                    int(warehouse_id),


                "p_qty":
                    int(qty),


                "p_price":
                    float(
                        money(cost)
                    ),


                "p_payment_method":
                    str(payment_method).lower(),


                "p_notes":
                    str(remarks),


                "p_created_by":
                    validate_uuid(user_id),


                "p_transaction_id":
                    tx_id

            }

        )


        if result.get("success"):

            CacheManager.bump_version(
                "inventory_version"
            )


        return result





# ==============================================================================
# REFUND SERVICE
# ==============================================================================


class RefundService:


    def __init__(
        self,
        client: Any
    ):

        self.client = client



    def process_refund(
        self,
        invoice_no: str,
        refund_items: list,
        reason: str = "",
        cashier_id: Optional[str] = None

    ) -> Dict[str, Any]:


        context = ERPContext.get_current()

        context.rotate_transaction()

        tx_id = context.current_transaction_id



        result = RPCEngine.execute(

            self.client,

            "refund_sale_rpc",

            {

                "p_invoice_no":
                    str(invoice_no),


                "p_refund_items":
                    serialize_json(
                        refund_items
                    ),


                "p_reason":
                    str(reason),


                "p_cashier_id":
                    validate_uuid(
                        cashier_id
                    ),


                "p_transaction_id":
                    tx_id

            }

        )


        if result.get("success"):

            CacheManager.bump_version(
                "inventory_version"
            )


        return result





# ==============================================================================
# DASHBOARD SERVICE
# ==============================================================================


class DashboardService:


    def __init__(
        self,
        client: Any
    ):

        self.client = client



    def get_low_stock_items(
        self,
        warehouse_id: Optional[int] = None

    ) -> List[Dict[str, Any]]:


        try:

            query = (

                self.client
                .table(
                    TABLE_PRODUCT_VIEW
                )
                .select(
                    "id,name,sku,stock,minimum_stock,warehouse_id"
                )

            )


            if warehouse_id:

                query = query.eq(
                    "warehouse_id",
                    int(warehouse_id)
                )



            rows = (
                query
                .execute()
                .data
                or []
            )


            return [

                row

                for row in rows

                if row.get(
                    "stock",
                    0
                )

                <=

                row.get(
                    "minimum_stock",
                    5
                )

            ]


        except Exception:

            return []



    def get_fifo_cogs(
        self,
        product_id: int,
        qty: int,
        warehouse_id: int

    ) -> Decimal:


        try:


            result = RPCEngine.execute(

                self.client,

                "get_fifo_cogs_rpc",

                {

                    "p_product_id":
                        int(product_id),


                    "p_qty":
                        int(qty),


                    "p_warehouse_id":
                        int(warehouse_id)

                }

            )


            if result.get("success"):

                return money(
                    result.get(
                        "data",
                        0
                    )
                )


            return Decimal("0.00")


        except Exception:

            return Decimal("0.00")





# ==============================================================================
# AUDIT SERVICE
# ==============================================================================


class AuditService:


    def __init__(
        self,
        client: Any
    ):

        self.client = client



    def create_audit_log(
        self,
        action: str,
        details: str,
        user_id: Optional[str] = None

    ) -> bool:


        try:


            result = (

                self.client
                .table(
                    Tables.AUDIT_LOGS
                )
                .insert(

                    {

                        "action":
                            str(action),


                        "details":
                            str(details),


                        "user_id":
                            validate_uuid(
                                user_id
                            )

                    }

                )
                .execute()

            )


            return bool(
                result.data
            )


        except Exception:

            return False





# ==============================================================================
# CACHE DATA LOADERS
# ==============================================================================


@st.cache_data(ttl=300)
def _get_warehouses_cached(version: int):

    with RepositoryCoordinator(db()) as coord:

        return coord.warehouses.get_active_warehouses()



def get_warehouses():

    return _get_warehouses_cached(
        CacheManager.get_version(
            "inventory_version"
        )
    )





@st.cache_data(ttl=300)
def _get_suppliers_cached(version: int):

    with RepositoryCoordinator(db()) as coord:

        return coord.suppliers.get_active_suppliers()



def get_suppliers():

    return _get_suppliers_cached(
        CacheManager.get_version(
            "inventory_version"
        )
    )





@st.cache_data(ttl=300)
def _get_customers_cached(version: int):

    with RepositoryCoordinator(db()) as coord:

        return coord.customers.get_active_customers()



def get_customers():

    return _get_customers_cached(
        CacheManager.get_version(
            "inventory_version"
        )
    )





@st.cache_data(ttl=300)
def _get_products_cached(
    warehouse_id,
    offset,
    limit,
    version
):

    with RepositoryCoordinator(db()) as coord:

        return coord.products.get_products(
            warehouse_id,
            offset,
            limit
        )




def get_products(
    warehouse_id=None,
    offset=0,
    limit=DEFAULT_PAGE_SIZE
):

    return _get_products_cached(

        warehouse_id,

        offset,

        limit,

        CacheManager.get_version(
            "inventory_version"
        )

    )





# ==============================================================================
# RPC COMPATIBILITY WRAPPERS
# ==============================================================================


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

    service = SalesService(
        db()
    )


    return service.checkout(

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

    service = PurchaseService(
        db()
    )


    return service.receive_stock(

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

    service = RefundService(
        db()
    )


    return service.process_refund(

        invoice_no,

        refund_items,

        reason,

        cashier_id

    )





# ==============================================================================
# FIFO COGS
# ==============================================================================


def get_fifo_cogs(
    product_id: int,
    qty: int,
    warehouse_id: int

):

    service = DashboardService(
        db()
    )


    return service.get_fifo_cogs(

        product_id,

        qty,

        warehouse_id

    )





# ==============================================================================
# AUDIT LOG
# ==============================================================================


def create_audit_log(
    action: str,
    details: str,
    user_id: Optional[str] = None

):

    service = AuditService(
        db()
    )


    return service.create_audit_log(

        action,

        details,

        user_id

    )





# ==============================================================================
# AUTH CHECK
# ==============================================================================


def require_login():

    if not st.session_state.get("authenticated", False):
        st.warning("Please log in to continue.")
        st.stop()

  
