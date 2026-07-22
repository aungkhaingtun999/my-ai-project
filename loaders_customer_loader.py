import streamlit as st

from ..base_repo import db
from ..context import CacheManager
from ..repositories import RepositoryCoordinator


@st.cache_data(ttl=300)
def _get_customers_cached(version: int):

    with RepositoryCoordinator(db()) as coord:

        return coord.customers.get_active_customers()



def get_customers():

    return _get_customers_cached(
        CacheManager.get_version(
            "inventory_version"
        )
    )
