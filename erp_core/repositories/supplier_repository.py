# ==============================================================================
# erp_core/repositories/supplier_repository.py
# ERP ENTERPRISE SUPPLIER REPOSITORY v30
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





class SupplierRepository(BaseRepository):
    """
    Supplier database operations
    """



    # --------------------------------------------------------------------------
    # GET ACTIVE SUPPLIERS
    # --------------------------------------------------------------------------

    def get_active_suppliers(
        self
    ) -> List[Dict[str, Any]]:


        try:

            result = (

                self.client
                .table(
                    Tables.SUPPLIERS
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
                f"get_active_suppliers error: {e}"
            )

            return []





    # --------------------------------------------------------------------------
    # GET SUPPLIER BY ID
    # --------------------------------------------------------------------------

    def get_by_id(
        self,
        supplier_id: int
    ) -> Optional[Dict[str, Any]]:


        try:

            result = (

                self.client
                .table(
                    Tables.SUPPLIERS
                )
                .select("*")
                .eq(
                    "id",
                    int(supplier_id)
                )
                .maybe_single()
                .execute()

            )


            return result.data


        except Exception as e:

            log_error(
                f"get_supplier error: {e}"
            )

            return None





    # --------------------------------------------------------------------------
    # SEARCH SUPPLIER
    # --------------------------------------------------------------------------

    def search(
        self,
        keyword: str
    ) -> List[Dict[str, Any]]:


        try:

            result = (

                self.client
                .table(
                    Tables.SUPPLIERS
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
                f"supplier search error: {e}"
            )

            return []
