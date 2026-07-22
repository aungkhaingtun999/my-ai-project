Skip to content
aungkhaingtun999
my-ai-project
Repository navigation
Code
Issues
Pull requests
Agents
Actions
Projects
Wiki
Security and quality
Insights
Settings
my-ai-project/erp_core
/services.py
Go to file
t
T
aungkhaingtun999
aungkhaingtun999
Update services.py
10c6d38
 · 
12 hours ago
my-ai-project/erp_core
/services.py

Code

Blame
1315 lines (767 loc) · 20.2 KB
def update_product_rpc(
# ==============================================================================
# erp_core/services.py
# ERP ENTERPRISE SERVICE LAYER V30.8 STABLE
# PART 1/3 (FULL UPDATED CODE)
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

from .config import log_error


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
    sale_id,
    refund_items,
    reason="",
    cashier_id=None

):

    service = RefundService(
        db()
    )


    return service.process_refund(

        sale_id,

        refund_items,

        reason,

        cashier_id

    )





def stock_adjustment_rpc(
    product_id,
    warehouse_id,
    quantity,
    reason,
    user_id=None
):

    service = InventoryService(
        db()
    )

    return service.adjust_stock(
        product_id,
        warehouse_id,
        quantity,
        reason,
        user_id
    )





def update_product_rpc(
    product_id,
    data
):

    try:

        result = (
            db()
            .table(
                Tables.PRODUCTS
            )
            .update(
                data
            )
            .eq(
                "id",
                product_id
            )
            .execute()
        )

        return {
            "success": True,
            "data": result.data
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }





# ==============================================================================
# FIFO COGS COMPATIBILITY WRAPPER
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
# INVENTORY VIEW COMPATIBILITY WRAPPER
# ==============================================================================

def get_inventory_view(
    warehouse_id=None,
    search=None,
    limit=100
):
    try:
        with RepositoryCoordinator(db()) as coord:
            return coord.products.search(
                search,
                warehouse_id
            )[:limit]

    except Exception:
        return []


# ==============================================================================
# AUDIT LOG COMPATIBILITY WRAPPER
# ==============================================================================

def create_audit_log(
    action,
    details,
    user_id=None
):
    service = AuditService(
        db()
    )

    return service.create_audit_log(
        action,
        details,
        user_id
    )

