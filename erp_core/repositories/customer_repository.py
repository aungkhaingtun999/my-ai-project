# ==============================================================================
# erp_core/repositories/customer_repository.py
# ERP ENTERPRISE CUSTOMER REPOSITORY v30
# ==============================================================================


from typing import (
    List,
    Dict,
    Any,
    Optional
)


from ..config import Tables


from ..base_repo import (
    log_error
)


from .base_repository import BaseRepository





class CustomerRepository(BaseRepository):
    """
    Customer database operations
    """



    # --------------------------------------------------------------------------
    # GET ACTIVE CUSTOMERS
    # --------------------------------------------------------------------------

    def get_active_customers(
        self
    ) -> List[Dict[str, Any]]:


        try:

            result = (

                self.client
                .table(
                    Tables.CUSTOMERS
                )
                .select("*")
                .eq(
                    "is_active",
                    True
                )
                .execute()

            )


            return result.data or []


        except Exception as e:

            log_error(
                f"get_active_customers error: {e}"
            )

            return []





    # --------------------------------------------------------------------------
    # GET CUSTOMER BY ID
    # --------------------------------------------------------------------------

    def get_by_id(
        self,
        customer_id: int
    ) -> Optional[Dict[str, Any]]:


        try:

            result = (

                self.client
                .table(
                    Tables.CUSTOMERS
                )
                .select("*")
                .eq(
                    "id",
                    int(customer_id)
                )
                .maybe_single()
                .execute()

            )


            return result.data


        except Exception as e:

            log_error(
                f"get_customer error: {e}"
            )

            return None





    # --------------------------------------------------------------------------
    # SEARCH CUSTOMER
    # --------------------------------------------------------------------------

    def search(
        self,
        keyword: str
    ) -> List[Dict[str, Any]]:


        try:

            result = (

                self.client
                .table(
                    Tables.CUSTOMERS
                )
                .select("*")
                .ilike(
                    "name",
                    f"%{keyword}%"
                )
                .execute()

            )


            return result.data or []


        except Exception as e:

            log_error(
                f"customer search error: {e}"
            )

            return []
