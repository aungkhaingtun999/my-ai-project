# ==============================================================================
# erp_core/services/helpers.py
# ERP ENTERPRISE SERVICE HELPERS v30.12
# ==============================================================================

from datetime import datetime
from decimal import Decimal


def get_fifo_cogs(
    product_id=None,
    qty=0,
    db=None
):
    """
    FIFO Cost Calculation Helper

    TODO:
    Connect with inventory_logs / purchase_batches
    """

    return Decimal("0.00")



def create_audit_log(
    action,
    user_id=None,
    details=None,
    db=None
):
    """
    Central Audit Log Helper
    """

    return {
        "action": action,
        "user_id": user_id,
        "details": details,
        "created_at": datetime.utcnow()
    }