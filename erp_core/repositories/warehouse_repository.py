# ==============================================================================
# erp_core/repositories/warehouse_repository.py
# ERP ENTERPRISE WAREHOUSE REPOSITORY v30
# ==============================================================================


from typing import (
    List,
    Dict,
    Any,
    Optional
)


from ..config import Tables


from ..base_repo import (
    safe_execute,
    log_error
)


from .base_repository import BaseRepository





class WarehouseRepository(BaseRepository):
    """
    Warehouse database operations
    """



    # --------------------------------------------------------------------------
    # GET ACTIVE WAREHOUSES
    # --------------------------------------------------------------------------

    def get_active_warehouses(
        self
    ) -> List[Dict[str, Any]]:


        try:

            result = (

                self.client
                .table(
                    Tables.WAREHOUSES
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
                f"get_active_warehouses error: {e}"
            )

            return []





    # --------------------------------------------------------------------------
    # GET WAREHOUSE BY ID
    # --------------------------------------------------------------------------

    def get_by_id(
        self,
        warehouse_id: int
    ) -> Optional[Dict[str, Any]]:


        try:

            result = (

                self.client
                .table(
                    Tables.WAREHOUSES
                )
                .select("*")
                .eq(
                    "id",
                    int(warehouse_id)
                )
                .maybe_single()
                .execute()

            )


            return result.data


        except Exception as e:

            log_error(
                f"get warehouse error: {e}"
            )

            return None





    # --------------------------------------------------------------------------
    # DEFAULT WAREHOUSE
    # --------------------------------------------------------------------------

    def get_default_warehouse_id(
        self
    ) -> int:


        warehouses = self.get_active_warehouses()


        if warehouses:

            return warehouses[0].get(
                "id",
                1
            )


        return 1
