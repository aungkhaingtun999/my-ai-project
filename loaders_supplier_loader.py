import streamlit as st

from ..base_repo import db
from ..context import CacheManager
from ..repositories import RepositoryCoordinator


@st.cache_data(ttl=300)
def _get_suppliers_cached(version: int):

    with RepositoryCoordinator(db()) as coord:

        return coord.suppliers.get_active_suppliers()



def get_suppliers():

    return _get_suppliers_cached(
        CacheManager.get_version(
            "inventory_version"
        )
    )