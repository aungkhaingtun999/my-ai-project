# ==============================================================================
# erp_core/loaders/supplier_loader.py
# ERP ENTERPRISE SUPPLIER LOADER v30
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
def _get_suppliers_cached(
    version: int
):

    try:

        with RepositoryCoordinator(
            db()
        ) as coord:

            return coord.suppliers.get_active_suppliers()


    except Exception as e:

        log_error(
            f"supplier loader error: {e}"
        )

        return []





def get_suppliers():

    return _get_suppliers_cached(

        CacheManager.get_version(
            "inventory_version"
        )

    )
