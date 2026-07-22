# ==============================================================================
# erp_core/loaders/product_loader.py
# ERP ENTERPRISE PRODUCT LOADER v30
# ==============================================================================


import streamlit as st


from ..base_repo import (
    db,
    log_error
)


from ..context import (
    CacheManager
)


from ..config import (
    DEFAULT_PAGE_SIZE
)


from ..repositories import (
    RepositoryCoordinator
)





@st.cache_data(ttl=300)
def _get_products_cached(
    warehouse_id,
    offset,
    limit,
    version
):

    try:

        with RepositoryCoordinator(
            db()
        ) as coord:

            return coord.products.get_products(
                warehouse_id,
                offset,
                limit
            )


    except Exception as e:

        log_error(
            f"product loader error: {e}"
        )

        return []





def get_products(
    warehouse_id=None,
    offset=0,
    limit=DEFAULT_PAGE_SIZE
):

    return _get_products_cached(

        warehouse_id,

        offset,

        limit,

        CacheManager.get_version(
            "inventory_version"
        )

    )
