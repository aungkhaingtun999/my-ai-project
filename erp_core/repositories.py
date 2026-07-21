# erp_core/repositories.py
from typing import Dict, List, Any, Optional
from supabase import Client
from .config import Tables, TABLE_PRODUCT_VIEW
from .base_repo import db, safe_execute

class BaseRepository:
    def __init__(self, client: Client, table_name: str):
        self.db = client
        self.table_name = table_name

    def find_by_id(self, record_id) -> Optional[Dict[str, Any]]:
        try:
            result = self.db.table(self.table_name).select("*").eq("id", record_id).maybe_single().execute()
            return result.data
        except Exception as e:
            from .config import log_error
            log_error(msg=f"Find failed {self.table_name}", exception=e)
            return None

    def insert(self, data: Dict[str, Any]):
        result = self.db.table(self.table_name).insert(data).execute()
        return result.data[0] if result.data else {}

    def update(self, record_id, data: Dict[str, Any]):
        result = self.db.table(self.table_name).update(data).eq("id", record_id).execute()
        return result.data[0] if result.data else {}

class ProductRepository(BaseRepository):
    def __init__(self, client: Client): super().__init__(client, Tables.PRODUCTS)

    def get_products(self, warehouse_id: Optional[int] = None, offset: int = 0, limit: int = 100) -> List[dict]:
        def query():
            q = self.db.table(TABLE_PRODUCT_VIEW).select("*").order("name")
            if warehouse_id: q = q.eq("warehouse_id", int(warehouse_id))
            return q.range(offset, offset + limit - 1).execute()
        return safe_execute(query, "Get products failed") or []

    def get_inventory_view(self, warehouse_id: Optional[int] = None, search: str = "", offset: int = 0, limit: int = 100) -> List[dict]:
        def query():
            q = self.db.table(TABLE_PRODUCT_VIEW).select("*").order("name")
            if warehouse_id: q = q.eq("warehouse_id", int(warehouse_id))
            if search: q = q.or_(f"name.ilike.%{search}%,sku.ilike.%{search}%,barcode.ilike.%{search}%")
            return q.range(offset, offset + limit - 1).execute()
        return safe_execute(query, "Get inventory view failed") or []

    def search(self, keyword: str, warehouse_id=None):
        def query():
            q = self.db.table(TABLE_PRODUCT_VIEW).select("*")
            if warehouse_id: q = q.eq("warehouse_id", warehouse_id)
            if keyword: q = q.or_(f"name.ilike.%{keyword}%,sku.ilike.%{keyword}%,barcode.ilike.%{keyword}%")
            return q.execute()
        return safe_execute(query, "Product search failed") or []

class WarehouseRepository(BaseRepository):
    def __init__(self, client: Client): super().__init__(client, Tables.WAREHOUSES)
    def get_active(self):
        def query(): return self.db.table(self.table_name).select("*").eq("is_active", True).order("id").execute()
        return safe_execute(query, "Warehouse loading failed") or []
    def get_active_warehouses(self): return self.get_active()

class CustomerRepository(BaseRepository):
    def __init__(self, client: Client): super().__init__(client, Tables.CUSTOMERS)
    def get_active(self):
        def query(): return self.db.table(self.table_name).select("*").eq("is_active", True).order("name").execute()
        return safe_execute(query, "Customer loading failed") or []
    def get_active_customers(self): return self.get_active()

class SupplierRepository(BaseRepository):
    def __init__(self, client: Client): super().__init__(client, Tables.SUPPLIERS)
    def get_active(self):
        def query(): return self.db.table(self.table_name).select("*").eq("is_active", True).order("name").execute()
        return safe_execute(query, "Supplier loading failed") or []
    def get_active_suppliers(self): return self.get_active()

class SalesRepository(BaseRepository):
    def __init__(self, client: Client): super().__init__(client, Tables.SALES)
    def search_receipts(self, keyword, limit=10):
        def query(): return self.db.table(self.table_name).select("id,invoice_no,total,created_at").ilike("invoice_no", f"%{keyword}%").order("created_at", desc=True).limit(limit).execute()
        return safe_execute(query, "Receipt search failed") or []

class RepositoryCoordinator:
    def __init__(self, client=None):
        self.client = client if client else db()
        self.products = ProductRepository(self.client)
        self.warehouses = WarehouseRepository(self.client)
        self.customers = CustomerRepository(self.client)
        self.suppliers = SupplierRepository(self.client)
        self.sales = SalesRepository(self.client)
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): pass
