# ==============================================================================
# erp_core/repositories.py
# ERP ENTERPRISE REPOSITORY LAYER v30
# Database Access Layer
# ==============================================================================


from typing import (
    Dict,
    List,
    Any,
    Optional
)


from .config import (
    Tables,
    TABLE_PRODUCT_VIEW
)


from .base_repo import (
    safe_execute,
    log_error
)



# ==============================================================================
# BASE REPOSITORY
# ==============================================================================


class BaseRepository:


    def __init__(
        self,
        client,
        table_name: str
    ):

        self.db = client
        self.table_name = table_name



    # --------------------------------------------------

    def find_by_id(
        self,
        record_id
    ) -> Optional[Dict[str,Any]]:


        try:

            result = (

                self.db
                .table(
                    self.table_name
                )
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
                message=
                f"Find failed {self.table_name}",

                exception=e
            )


            return None



    # --------------------------------------------------


    def insert(
        self,
        data:Dict[str,Any]
    ):


        result = (

            self.db
            .table(
                self.table_name
            )
            .insert(
                data
            )
            .execute()

        )


        if result.data:

            return result.data[0]


        return {}



    # --------------------------------------------------


    def update(
        self,
        record_id,
        data:Dict[str,Any]
    ):


        result = (

            self.db
            .table(
                self.table_name
            )
            .update(
                data
            )
            .eq(
                "id",
                record_id
            )
            .execute()

        )


        if result.data:

            return result.data[0]


        return {}



    # --------------------------------------------------


    def delete(
        self,
        record_id
    ):


        result = (

            self.db
            .table(
                self.table_name
            )
            .delete()
            .eq(
                "id",
                record_id
            )
            .execute()

        )


        return result.data





# ==============================================================================
# PRODUCT REPOSITORY
# ==============================================================================


class ProductRepository(
    BaseRepository
):


    def __init__(
        self,
        client
    ):

        super().__init__(
            client,
            Tables.PRODUCTS
        )



    # --------------------------------------------------


    def get_products(
        self,
        warehouse_id=None,
        offset=0,
        limit=100
    ) -> List[dict]:


        def query():


            q=(

                self.db
                .table(
                    TABLE_PRODUCT_VIEW
                )
                .select("*")
                .order(
                    "name"
                )

            )


            if warehouse_id:


                q=q.eq(
                    "warehouse_id",
                    int(warehouse_id)
                )


            return (

                q
                .range(
                    offset,
                    offset+limit-1
                )
                .execute()

            )


        return safe_execute(
            query,
            "Loading products failed"
        ) or []



    # --------------------------------------------------


    def search(
        self,
        keyword,
        warehouse_id=None
    ):


        def query():


            q=(

                self.db
                .table(
                    TABLE_PRODUCT_VIEW
                )
                .select("*")

            )


            if warehouse_id:

                q=q.eq(
                    "warehouse_id",
                    warehouse_id
                )


            if keyword:


                q=q.or_(

                    f"name.ilike.%{keyword}%,"
                    f"sku.ilike.%{keyword}%,"
                    f"barcode.ilike.%{keyword}%"

                )


            return q.execute()



        return safe_execute(
            query,
            "Product search failed"
        ) or []





# ==============================================================================
# WAREHOUSE REPOSITORY
# ==============================================================================


class WarehouseRepository(
    BaseRepository
):


    def __init__(
        self,
        client
    ):

        super().__init__(
            client,
            Tables.WAREHOUSES
        )



    def get_active(
        self
    ):


        def query():

            return (

                self.db
                .table(
                    self.table_name
                )
                .select("*")
                .eq(
                    "is_active",
                    True
                )
                .order(
                    "id"
                )
                .execute()

            )


        return safe_execute(
            query,
            "Warehouse loading failed"
        ) or []



    def get_active_warehouses(
        self
    ):

        return self.get_active()





# ==============================================================================
# CUSTOMER REPOSITORY
# ==============================================================================


class CustomerRepository(
    BaseRepository
):


    def __init__(
        self,
        client
    ):

        super().__init__(
            client,
            Tables.CUSTOMERS
        )



    def get_active(self):


        def query():

            return (

                self.db
                .table(
                    self.table_name
                )
                .select("*")
                .eq(
                    "is_active",
                    True
                )
                .order(
                    "name"
                )
                .execute()

            )


        return safe_execute(
            query,
            "Customer loading failed"
        ) or []



    def get_active_customers(
        self
    ):

        return self.get_active()





# ==============================================================================
# SUPPLIER REPOSITORY
# ==============================================================================


class SupplierRepository(
    BaseRepository
):


    def __init__(
        self,
        client
    ):

        super().__init__(
            client,
            Tables.SUPPLIERS
        )



    def get_active(self):


        def query():

            return (

                self.db
                .table(
                    self.table_name
                )
                .select("*")
                .eq(
                    "is_active",
                    True
                )
                .order(
                    "name"
                )
                .execute()

            )


        return safe_execute(
            query,
            "Supplier loading failed"
        ) or []



    def get_active_suppliers(
        self
    ):

        return self.get_active()





# ==============================================================================
# SALES REPOSITORY
# ==============================================================================


class SalesRepository(
    BaseRepository
):


    def __init__(
        self,
        client
    ):

        super().__init__(
            client,
            Tables.SALES
        )



    def search_receipts(
        self,
        keyword,
        limit=10
    ):


        def query():

            return (

                self.db
                .table(
                    self.table_name
                )
                .select(
                    "id,invoice_no,total,created_at"
                )
                .ilike(
                    "invoice_no",
                    f"%{keyword}%"
                )
                .order(
                    "created_at",
                    desc=True
                )
                .limit(
                    limit
                )
                .execute()

            )


        return safe_execute(
            query,
            "Receipt search failed"
        ) or []





# ==============================================================================
# REPOSITORY COORDINATOR
# ==============================================================================


class RepositoryCoordinator:


    def __init__(
        self,
        client
    ):

        self.client = client


        self.products = ProductRepository(
            client
        )


        self.warehouses = WarehouseRepository(
            client
        )


        self.customers = CustomerRepository(
            client
        )


        self.suppliers = SupplierRepository(
            client
        )


        self.sales = SalesRepository(
            client
        )



    def __enter__(
        self
    ):

        return self



    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb
    ):

        pass
