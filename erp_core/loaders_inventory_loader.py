from ..base_repo import db
from ..repositories import RepositoryCoordinator
def get_inventory_view(
    warehouse_id=None,
    search=None,
    limit=100
):
    try:
        with RepositoryCoordinator(db()) as coord:
            return coord.products.search(
                search,
                warehouse_id
            )[:limit]
    except Exception:
        return []