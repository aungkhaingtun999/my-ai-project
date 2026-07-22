# ==============================================================================
# erp_core/services/dashboard_service.py
# ERP ENTERPRISE DASHBOARD SERVICE
# ==============================================================================


from decimal import Decimal


from typing import (
    Optional,
    List,
    Dict,
    Any
)


from ..config import (
    TABLE_PRODUCT_VIEW
)


from ..base_repo import (
    money
)


from ..rpc.engine import (
    RPCEngine
)





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

                    int(
                        warehouse_id
                    )

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

                        int(
                            product_id
                        ),



                    "p_qty":

                        int(
                            qty
                        ),



                    "p_warehouse_id":

                        int(
                            warehouse_id
                        )

                }

            )



            if result.get(
                "success"
            ):


                return money(

                    result.get(
                        "data",
                        0
                    )

                )



            return Decimal(
                "0.00"
            )



        except Exception:

            return Decimal(
                "0.00"
            )
