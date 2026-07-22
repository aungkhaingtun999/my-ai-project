# ==============================================================================
# erp_core/repositories/sales_repository.py
# ERP ENTERPRISE SALES REPOSITORY v30
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





class SalesRepository(BaseRepository):
    """
    Sales transaction database operations
    """



    # --------------------------------------------------------------------------
    # GET SALES
    # --------------------------------------------------------------------------

    def get_sales(
        self,
        limit: int = 100
    ) -> List[Dict[str, Any]]:


        try:

            result = (

                self.client
                .table(
                    Tables.SALES
                )
                .select("*")
                .order(
                    "created_at",
                    desc=True
                )
                .limit(
                    limit
                )
                .execute()

            )


            return result.data or []


        except Exception as e:

            log_error(
                f"get_sales error: {e}"
            )

            return []





    # --------------------------------------------------------------------------
    # GET SALE BY ID
    # --------------------------------------------------------------------------

    def get_by_id(
        self,
        sale_id: int
    ) -> Optional[Dict[str, Any]]:


        try:

            result = (

                self.client
                .table(
                    Tables.SALES
                )
                .select("*")
                .eq(
                    "id",
                    int(sale_id)
                )
                .maybe_single()
                .execute()

            )


            return result.data


        except Exception as e:

            log_error(
                f"get_sale error: {e}"
            )

            return None





    # --------------------------------------------------------------------------
    # GET SALE ITEMS
    # --------------------------------------------------------------------------

    def get_sale_items(
        self,
        sale_id: int
    ) -> List[Dict[str, Any]]:


        try:

            result = (

                self.client
                .table(
                    Tables.SALE_ITEMS
                )
                .select("*")
                .eq(
                    "sale_id",
                    int(sale_id)
                )
                .execute()

            )


            return result.data or []


        except Exception as e:

            log_error(
                f"get_sale_items error: {e}"
            )

            return []





    # --------------------------------------------------------------------------
    # SEARCH SALES
    # --------------------------------------------------------------------------

    def search(
        self,
        keyword: str
    ) -> List[Dict[str, Any]]:


        try:

            result = (

                self.client
                .table(
                    Tables.SALES
                )
                .select("*")
                .ilike(
                    "invoice_no",
                    f"%{keyword}%"
                )
                .execute()

            )


            return result.data or []


        except Exception as e:

            log_error(
                f"sales search error: {e}"
            )

            return []
