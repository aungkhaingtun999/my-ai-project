# ==============================================================================
# erp_core/rpc/purchase_rpc.py
# ERP ENTERPRISE PURCHASE RPC WRAPPER
# ==============================================================================


from typing import (
    Optional,
    Dict,
    Any
)


from ..base_repo import (
    db,
    log_error
)


from ..services import (
    PurchaseService
)





def purchase_receive_rpc(
    product_id: int,
    supplier_id: int,
    warehouse_id: int,
    qty: int,
    cost: Any,
    remarks: str = "",
    user_id: Optional[str] = None

) -> Dict[str, Any]:


    try:

        service = PurchaseService(
            db()
        )


        return service.receive_stock(

            product_id,

            supplier_id,

            warehouse_id,

            qty,

            cost,

            remarks,

            user_id

        )


    except Exception as e:

        log_error(
            f"purchase_receive_rpc error: {e}"
        )


        return {

            "success": False,

            "message": str(e),

            "data": None

        }
