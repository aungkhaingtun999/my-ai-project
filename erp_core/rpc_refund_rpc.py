# ==============================================================================
# erp_core/rpc/refund_rpc.py
# ERP ENTERPRISE REFUND RPC WRAPPER
# ==============================================================================


from typing import Optional, Dict, Any


from ..base_repo import db


from ..services import RefundService




def refund_sale_rpc(
    invoice_no: str,
    refund_items: list,
    reason: str = "",
    cashier_id: Optional[str] = None

) -> Dict[str, Any]:


    service = RefundService(
        db()
    )


    return service.process_refund(

        invoice_no,

        refund_items,

        reason,

        cashier_id

    )