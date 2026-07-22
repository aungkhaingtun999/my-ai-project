# ==============================================================================
# erp_core/rpc/purchase_rpc.py
# ERP ENTERPRISE PURCHASE RPC WRAPPER
# ==============================================================================


from typing import Optional, Dict, Any


from ..base_repo import db


from ..services import PurchaseService




def purchase_receive_rpc(
    product_id: int,
    supplier_id: int,
    warehouse_id: int,
    qty: int,
    cost: Any,
    payment_method: str = "credit",
    remarks: str = "",
    user_id: Optional[str] = None

) -> Dict[str, Any]:


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
