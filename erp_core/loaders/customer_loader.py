# ==============================================================================
# erp_core/loaders/customer_loader.py
# ERP ENTERPRISE CUSTOMER LOADER v30
# ==============================================================================


import streamlit as st


from ..base_repo import (
    db,
    log_error
)


from ..context import (
    CacheManager
)


from ..repositories import (
    RepositoryCoordinator
)





@st.cache_data(ttl=300)
def _get_customers_cached(
    version: int
):

    try:

        with RepositoryCoordinator(
            db()
        ) as coord:

            return coord.customers.get_active_customers()


    except Exception as e:

        log_error(
            f"customer loader error: {e}"
        )

        return []





def get_customers():

    return _get_customers_cached(

        CacheManager.get_version(
            "inventory_version"
        )

    )
