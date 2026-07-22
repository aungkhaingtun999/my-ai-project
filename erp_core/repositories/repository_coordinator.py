# ==============================================================================
# erp_core/repositories/repository_coordinator.py
# ERP ENTERPRISE REPOSITORY COORDINATOR v30
# Repository Dependency Manager
# ==============================================================================


from typing import Any


from .product_repository import (
    ProductRepository
)


from .warehouse_repository import (
    WarehouseRepository
)


from .customer_repository import (
    CustomerRepository
)


from .supplier_repository import (
    SupplierRepository
)


from .sales_repository import (
    SalesRepository
)





class RepositoryCoordinator:
    """
    Central repository manager.

    Usage:

        with RepositoryCoordinator(db()) as coord:

            products = coord.products.get_products()

    """



    def __init__(
        self,
        client: Any
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





    # --------------------------------------------------------------------------
    # CONTEXT MANAGER
    # --------------------------------------------------------------------------

    def __enter__(
        self
    ):

        return self





    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):

        return False
