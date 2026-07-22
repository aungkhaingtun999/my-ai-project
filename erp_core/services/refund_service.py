# ==============================================================================
# erp_core/services/refund_service.py
# ERP ENTERPRISE REFUND SERVICE
# ==============================================================================


from typing import (
    Optional,
    Dict,
    Any
)


from ..base_repo import (
    validate_uuid,
    serialize_json
)


from ..context import (
    ERPContext,
    CacheManager
)


from ..rpc.engine import (
    RPCEngine
)





class RefundService:


    def __init__(
        self,
        client: Any
    ):

        self.client = client





    def process_refund(
        self,
        sale_id: int,
        refund_items: list,
        reason: str = "",
        cashier_id: Optional[str] = None

    ) -> Dict[str, Any]:


        context = ERPContext.get_current()


        context.rotate_transaction()



        result = RPCEngine.execute(

            self.client,

            "refund_sale_rpc",

            {

                "p_sale_id":
                    int(sale_id),


                "p_items":
                    serialize_json(
                        refund_items
                    ),


                "p_reason":
                    str(reason),


                "p_cashier_id":
                    validate_uuid(
                        cashier_id
                    )

            }

        )



        if result.get(
            "success"
        ):

            CacheManager.bump_version(
                "inventory_version"
            )



        return result
