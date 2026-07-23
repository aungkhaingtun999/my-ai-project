# ==============================================================================
# erp_core/services/inventory_service.py
# ERP ENTERPRISE INVENTORY SERVICE
# ==============================================================================


from typing import (
    Optional,
    Dict,
    Any
)


from ..base_repo import (
    validate_uuid
)


from ..context import (
    ERPContext,
    CacheManager
)


from ..rpc.engine import (
    RPCEngine
)





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
                    validate_uuid(
                        user_id
                    ),


                "p_transaction_id":
                    tx_id

            }

        )



        if result.get(
            "success"
        ):

            CacheManager.bump_version(
                "inventory_version"
            )



        return result
            def update_product(
        self,
        product_id: int,
        data: Dict[str, Any]

    ) -> Dict[str, Any]:


        result = RPCEngine.execute(

            self.client,

            "update_product_rpc",

            {
                "p_product_id": int(product_id),

                "p_data": data
            }

        )


        if result.get("success"):

            CacheManager.bump_version(
                "inventory_version"
            )


        return result
