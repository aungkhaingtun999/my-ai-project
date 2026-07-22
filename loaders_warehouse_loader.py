import streamlit as st

from ..base_repo import db
from ..context import CacheManager
from ..repositories import RepositoryCoordinator
@st.cache_data(ttl=300)
def _get_warehouses_cached(version: int):
    with RepositoryCoordinator(db()) as coord:
        return coord.warehouses.get_active_warehouses()


def get_warehouses():
    return _get_warehouses_cached(
        CacheManager.get_version("inventory_version")
    )