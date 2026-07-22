# ==============================================================================
# erp_core/repositories/base_repository.py
# ERP ENTERPRISE BASE REPOSITORY v30
# Common Database Access Layer
# ==============================================================================


from typing import (
    Any,
    Dict,
    List,
    Optional
)


from ..base_repo import (
    db,
    safe_execute,
    log_error
)





class BaseRepository:
    """
    Base repository class.

    All repositories inherit this class.

    Example:
        ProductRepository(BaseRepository)
        WarehouseRepository(BaseRepository)
    """



    def __init__(
        self,
        client=None
    ):

        self.client = (
            client
            if client
            else db()
        )




    # --------------------------------------------------------------------------
    # TABLE SELECT
    # --------------------------------------------------------------------------

    def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:


        try:

            query = (
                self.client
                .table(table)
                .select(columns)
            )


            if filters:

                for key, value in filters.items():

                    query = query.eq(
                        key,
                        value
                    )


            result = query.execute()


            return result.data or []


        except Exception as e:

            log_error(
                f"Repository select error: {e}"
            )

            return []





    # --------------------------------------------------------------------------
    # SINGLE RECORD
    # --------------------------------------------------------------------------

    def find_one(
        self,
        table: str,
        record_id: Any
    ):


        try:

            result = (

                self.client
                .table(table)
                .select("*")
                .eq(
                    "id",
                    record_id
                )
                .maybe_single()
                .execute()

            )


            return result.data


        except Exception as e:

            log_error(
                f"Repository find_one error: {e}"
            )

            return None





    # --------------------------------------------------------------------------
    # INSERT
    # --------------------------------------------------------------------------

    def insert(
        self,
        table: str,
        data: Dict[str, Any]
    ):


        try:

            result = (

                self.client
                .table(table)
                .insert(data)
                .execute()

            )


            return result.data


        except Exception as e:

            log_error(
                f"Repository insert error: {e}"
            )

            return []





    # --------------------------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------------------------

    def update(
        self,
        table: str,
        record_id: Any,
        data: Dict[str, Any]
    ):


        try:

            result = (

                self.client
                .table(table)
                .update(data)
                .eq(
                    "id",
                    record_id
                )
                .execute()

            )


            return result.data


        except Exception as e:

            log_error(
                f"Repository update error: {e}"
            )

            return []





    # --------------------------------------------------------------------------
    # DELETE
    # --------------------------------------------------------------------------

    def delete(
        self,
        table: str,
        record_id: Any
    ):


        try:

            result = (

                self.client
                .table(table)
                .delete()
                .eq(
                    "id",
                    record_id
                )
                .execute()

            )


            return result.data


        except Exception as e:

            log_error(
                f"Repository delete error: {e}"
            )

            return []
