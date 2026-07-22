# ==============================================================================
# erp_core/services/sales_service.py
# ERP ENTERPRISE SALES SERVICE
# ==============================================================================


from typing import (
    Optional,
    Dict,
    Any
)


from ..base_repo import (
    money,
    validate_uuid,
    serialize_json
)


from ..context import (
    ERPContext,
    CacheManager
)


from ..rpc_engine import (
    RPCEngine
)


from ..exceptions import (
    ValidationError
)


from .customer_service import (
    CustomerService
)





class SalesService:


    def __init__(
        self,
        client: Any
    ):

        self.client = client


        self.customer_service = CustomerService(
            client
        )





    def checkout(
        self,
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


        if not cart:

            raise ValidationError(
                "Cart cannot be empty"
            )



        context = ERPContext.get_current()


        context.rotate_transaction()



        success = False



        try:


            current_warehouse = (

                warehouse_id

                if warehouse_id is not None

                else

                context.current_warehouse_id

            )



            total_sale = sum(

                money(
                    item.get(
                        "selling_price",
                        0
                    )
                )

                *

                money(
                    item.get(
                        "qty",
                        1
                    )
                )

                for item in cart

            )



            if str(payment_method).lower() == "credit":

                self.customer_service.check_credit_limit(
                    customer_id,
                    total_sale
                )



            payload = {


                "p_cart":

                    serialize_json(
                        cart
                    ),



                "p_paid_amount":

                    float(
                        money(
                            paid_amount
                        )
                    ),



                "p_warehouse_id":

                    int(
                        current_warehouse
                    ),



                "p_cashier_id":

                    validate_uuid(
                        cashier_id
                    ),



                "p_counter_id":

                    int(
                        counter_id
                    ),



                "p_payment_method":

                    str(
                        payment_method
                    ).lower(),



                "p_tax_rate":

                    float(
                        money(
                            tax_rate
                        )
                    ),



                "p_discount":

                    float(
                        money(
                            discount
                        )
                    )

            }



            result = RPCEngine.execute(

                self.client,

                "checkout_sale_rpc",

                payload

            )



            if result.get(
                "success"
            ):

                success = True


                CacheManager.bump_version(
                    "inventory_version"
                )



            return result



        finally:


            if success:

                pass
