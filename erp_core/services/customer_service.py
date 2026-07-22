# ==============================================================================
# erp_core/services/customer_service.py
# ERP ENTERPRISE CUSTOMER SERVICE
# ==============================================================================


from decimal import Decimal

from typing import (
    Any
)


from ..config import (
    Tables
)


from ..base_repo import (
    money
)


from ..exceptions import (
    CreditLimitExceededError
)





class CustomerService:


    def __init__(
        self,
        client: Any
    ):

        self.client = client





    def check_credit_limit(
        self,
        customer_id: str,
        sale_amount: Decimal
    ) -> bool:


        if not customer_id:

            return True



        try:

            result = (

                self.client
                .table(
                    Tables.CUSTOMERS
                )
                .select(
                    "credit_limit,current_balance"
                )
                .eq(
                    "id",
                    customer_id
                )
                .maybe_single()
                .execute()

            )


            if not result.data:

                return True



            limit = money(
                result.data.get(
                    "credit_limit",
                    0
                )
            )


            balance = money(
                result.data.get(
                    "current_balance",
                    0
                )
            )



            if (

                limit > Decimal("0.00")

                and

                balance + sale_amount > limit

            ):

                raise CreditLimitExceededError(
                    "Customer credit limit exceeded"
                )



            return True



        except CreditLimitExceededError:

            raise



        except Exception:

            return True
