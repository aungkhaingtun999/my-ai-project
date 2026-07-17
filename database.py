# ==========================================
# database.py v14.9
# ERP ENTERPRISE - PERFORMANCE & CONTEXT OPTIMIZED
# ==========================================

# ... (Previous imports & setup remain the same) ...

# ==========================================
# PRODUCTS (Performance Optimized)
# ==========================================

def get_products(active_only=True, warehouse_id=None):
    """
    Optimized: Stock calculation logic improved.
    """
    try:
        query = (
            db()
            .table("products")
            .select("""
                id, barcode, sku, name, purchase_price, selling_price, is_active,
                warehouse_stock(warehouse_id, qty)
            """)
        )
        if active_only:
            query = query.eq("is_active", True)
        
        data = query.execute().data or []
        
        for p in data:
            stock_qty = 0
            # Logic: If warehouse_id is specified, take that specific stock
            # If not, aggregate all stocks (Current logic for global view)
            for s in p.get("warehouse_stock", []):
                if warehouse_id is None:
                    stock_qty += s.get("qty", 0)
                elif s["warehouse_id"] == warehouse_id:
                    stock_qty = s.get("qty", 0) # Exact warehouse match
            
            p["stock"] = stock_qty
            p.pop("warehouse_stock", None)
            
        return data
    except Exception as e:
        log_error(e)
        return []

# ==========================================
# WAREHOUSE CONTEXT (Enterprise Setup)
# ==========================================

def get_default_warehouse():
    """ Enterprise POS default warehouse picker """
    try:
        res = db().table("warehouses").select("id,name").eq("is_active", True).order("id").limit(1).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        log_error(e)
        return None

# ==========================================
# CHECKOUT CONTEXT (Adding Warehouse/Counter)
# ==========================================

def checkout_sale_rpc(cart, paid_amount, warehouse_id, cashier_id=None, counter_id=1):
    """
    Enterprise Checkout: Including Warehouse and Counter contexts
    """
    try:
        payload = {
            "p_cart": cart,
            "p_paid_amount": money(paid_amount),
            "p_warehouse_id": warehouse_id, # Added context
            "p_counter_id": counter_id,     # Added context
            "p_cashier_id": validate_uuid(cashier_id)
        }
        res = db().rpc("checkout_sale_rpc", payload).execute()
        return res.data if res.data else {"success": False, "message": "No response from RPC"}
    except Exception as e:
        log_error(e)
        return {"success": False, "message": str(e)}

# ... (Other functions remain consistent) ...
