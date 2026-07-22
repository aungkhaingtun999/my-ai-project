# ==============================================================================
# erp_core/loaders/inventory_loader.py
# ERP ENTERPRISE INVENTORY LOADER v30
# ==============================================================================


from ..base_repo import (
    db,
    log_error
)


from ..repositories import (
    RepositoryCoordinator
)





def get_inventory_view(
    warehouse_id=None,
    search=None,
    limit=100
):
    """
    Inventory compatibility loader.

    Provides old database.py compatible function:
        get_inventory_view()
    """


    try:

        with RepositoryCoordinator(
            db()
        ) as coord:

            data = coord.products.search(
                search,
                warehouse_id
            )

            return data[:limit]


    except Exception as e:

        log_error(
            f"get_inventory_view error: {e}"
        )

        return []
