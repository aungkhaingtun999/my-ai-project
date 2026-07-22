# ==============================================================================
# erp_core/rpc/stock_rpc.py
# ERP ENTERPRISE STOCK ADJUSTMENT RPC WRAPPER
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
    InventoryService
)





def stock_adjustment_rpc(
    product_id: int,
    warehouse_id: int,
    quantity: int,
    reason: str,
    user_id: Optional[str] = None

) -> Dict[str, Any]:


    try:

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


    except Exception as e:

        log_error(
            f"stock_adjustment_rpc error: {e}"
        )


        return {

            "success": False,

            "message": str(e),

            "data": None

        }
