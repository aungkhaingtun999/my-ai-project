# ==============================================================================
# erp_core/rpc/checkout_rpc.py
# ERP ENTERPRISE CHECKOUT RPC
# ==============================================================================

print("CHECKOUT RPC START")
from typing import (
    Optional,
    Dict,
    Any
)


from ..base_repo import (
    db,
    log_error
)


from ..services.sales_service import (
    SalesService
)





def checkout_sale_rpc(
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


    try:

        service = SalesService(
            db()
        )


        result = service.checkout(

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


        return result



    except Exception as e:


        log_error(
            f"checkout_sale_rpc error: {e}"
        )


        return {

            "success": False,

            "message": str(e)

        }
