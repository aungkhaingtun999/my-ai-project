"""
==============================================================================
database.py
ERP ENTERPRISE DATABASE GATEWAY v34
Legacy Compatibility Bridge + Multi-Tenant Extension

Legacy pages:
    from database import ...

New architecture:
    erp_core/

This module re-exports ERP Core APIs and adds Multi-Tenant helpers.
==============================================================================
"""


# ==============================================================================
# ERP CORE IMPORT
# ==============================================================================

from erp_core import (
    # ------------------------------------------------------------------
    # DATABASE
    # ------------------------------------------------------------------
    db,
    get_supabase,
    get_connection,
    DatabaseHealth,
    database_health_check,

    # ------------------------------------------------------------------
    # LOADERS
    # ------------------------------------------------------------------
    get_setting,
    get_products,
    get_inventory_view,
    get_warehouses,
    get_default_warehouse_id,
    get_categories,
    get_suppliers,
    get_customers,

    # ------------------------------------------------------------------
    # RECEIPT
    # ------------------------------------------------------------------
    get_receipt,
    get_sale_items,
    search_receipts,

    # ------------------------------------------------------------------
    # RPC
    # ------------------------------------------------------------------
    checkout_sale_rpc,
    purchase_receive_rpc,
    refund_sale_rpc,
    stock_adjustment_rpc,
    update_product_rpc,
    request_product_create_rpc,
    request_product_bulk_create_rpc,
    approve_product_create_rpc,

    # ------------------------------------------------------------------
    # SERVICES
    # ------------------------------------------------------------------
    SalesService,
    PurchaseService,
    InventoryService,
    RefundService,
    ReceiptService,
    PaymentService,
    PaymentQRService,

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------
    get_fifo_cogs,
    create_audit_log,

    # ------------------------------------------------------------------
    # UTILITIES
    # ------------------------------------------------------------------
    money,
    money_float,
    validate_uuid,
    serialize_json,
    safe_execute,
)


ERP_DATABASE_VERSION = "34.0 Legacy Gateway + Multi-Tenant"


# ==============================================================================
# MULTI-TENANT DATABASE HELPERS
# ==============================================================================

def get_tenant_scoped_query(table_name, tenant_id_field="shop_id"):
    """
    Return a query builder scoped to current tenant.
    Must be used inside Streamlit context.
    
    Example:
        query = get_tenant_scoped_query("products")
        result = query.execute()
    """
    import streamlit as st
    
    supabase_client = db()
    query = supabase_client.table(table_name)
    
    # Apply tenant scope only if multi-tenant enabled
    try:
        from config import MULTI_TENANT_ENABLED, get_tenant_context
        tenant_context = get_tenant_context()
        
        if MULTI_TENANT_ENABLED and tenant_context:
            shop_id = tenant_context.get("shop_id")
            if shop_id:
                query = query.eq(tenant_id_field, shop_id)
    except Exception:
        pass
    
    return query


def get_current_tenant_id():
    """
    Get current tenant shop_id from session.
    Returns None if not set.
    """
    import streamlit as st
    
    return st.session_state.get("shop_id")


def get_current_branch_id():
    """
    Get current branch_id from session.
    Returns None if not set.
    """
    import streamlit as st
    
    return st.session_state.get("branch_id")


def get_current_tenant_role():
    """
    Get current tenant_role from session.
    Returns 'staff' if not set.
    """
    import streamlit as st
    
    return st.session_state.get("tenant_role", "staff")


def tenant_aware_select(table_name, tenant_id_field="shop_id"):
    """
    Perform tenant-aware select query.
    Returns list of records.
    
    Example:
        products = tenant_aware_select("products")
    """
    import streamlit as st
    
    supabase_client = db()
    
    try:
        from config import MULTI_TENANT_ENABLED, get_tenant_context
        tenant_context = get_tenant_context()
        
        query = supabase_client.table(table_name).select("*")
        
        if MULTI_TENANT_ENABLED and tenant_context:
            shop_id = tenant_context.get("shop_id")
            if shop_id:
                query = query.eq(tenant_id_field, shop_id)
        
        result = query.execute()
        return result.data or []
    
    except Exception as e:
        print(f"Tenant-aware select error: {e}")
        return []


def tenant_aware_insert(table_name, data, tenant_id_field="shop_id"):
    """
    Perform tenant-aware insert query.
    Automatically adds tenant_id to the data.
    
    Example:
        result = tenant_aware_insert("products", {"name": "Item 1"})
    """
    import streamlit as st
    
    supabase_client = db()
    
    try:
        from config import MULTI_TENANT_ENABLED
        tenant_id = get_current_tenant_id()
        
        if MULTI_TENANT_ENABLED and tenant_id:
            data[tenant_id_field] = tenant_id
        
        result = supabase_client.table(table_name).insert(data).execute()
        return result.data or []
    
    except Exception as e:
        print(f"Tenant-aware insert error: {e}")
        return []


def tenant_aware_update(table_name, data, match_field, match_value, tenant_id_field="shop_id"):
    """
    Perform tenant-aware update query.
    Scoped to current tenant.
    
    Example:
        result = tenant_aware_update(
            "products",
            {"price": 100},
            "id",
            product_id
        )
    """
    import streamlit as st
    
    supabase_client = db()
    
    try:
        from config import MULTI_TENANT_ENABLED
        tenant_id = get_current_tenant_id()
        
        query = supabase_client.table(table_name).update(data).eq(match_field, match_value)
        
        if MULTI_TENANT_ENABLED and tenant_id:
            query = query.eq(tenant_id_field, tenant_id)
        
        result = query.execute()
        return result.data or []
    
    except Exception as e:
        print(f"Tenant-aware update error: {e}")
        return []


def tenant_aware_delete(table_name, match_field, match_value, tenant_id_field="shop_id"):
    """
    Perform tenant-aware delete query.
    Scoped to current tenant.
    
    Example:
        result = tenant_aware_delete(
            "products",
            "id",
            product_id
        )
    """
    import streamlit as st
    
    supabase_client = db()
    
    try:
        from config import MULTI_TENANT_ENABLED
        tenant_id = get_current_tenant_id()
        
        query = supabase_client.table(table_name).delete().eq(match_field, match_value)
        
        if MULTI_TENANT_ENABLED and tenant_id:
            query = query.eq(tenant_id_field, tenant_id)
        
        result = query.execute()
        return result.data or []
    
    except Exception as e:
        print(f"Tenant-aware delete error: {e}")
        return []


# ==============================================================================
# SERVICE FACTORIES
# ==============================================================================

def get_sales_service():
    return SalesService(
        db()
    )


def get_purchase_service():
    return PurchaseService(
        db()
    )


def get_inventory_service():
    return InventoryService(
        db()
    )


def get_refund_service():
    return RefundService(
        db()
    )


# ==============================================================================
# PAYMENT HELPERS
# ==============================================================================

def create_mobile_payment(
    sale_id,
    provider,
    transaction_id,
    amount,
    cashier_id=None
):
    return PaymentService.create_mobile_payment(
        sale_id=sale_id,
        provider=provider,
        transaction_id=transaction_id,
        amount=amount,
        cashier_id=cashier_id
    )


def verify_payment(
    payment_id,
    verified_by
):
    return PaymentService.verify_payment(
        payment_id,
        verified_by
    )


def reject_payment(
    payment_id,
    verified_by,
    reason
):
    return PaymentService.reject_payment(
        payment_id,
        verified_by,
        reason
    )


def get_pending_payments():
    return PaymentService.pending_payments()


def generate_payment_qr(
    provider="",
    account_name="",
    account_no="",
    amount=0,
    sale_id="",
    raw_payload=None
):
    return PaymentQRService.generate_qr(
        provider=provider,
        account_name=account_name,
        account_no=account_no,
        amount=amount,
        sale_id=sale_id,
        raw_payload=raw_payload
    )


# ==============================================================================
# PUBLIC EXPORTS
# ==============================================================================

__all__ = [
    # DATABASE
    "db",
    "get_supabase",
    "get_connection",
    "DatabaseHealth",
    "database_health_check",

    # LOADERS
    "get_setting",
    "get_products",
    "get_inventory_view",
    "get_warehouses",
    "get_default_warehouse_id",
    "get_categories",
    "get_suppliers",
    "get_customers",

    # RECEIPT
    "get_receipt",
    "get_sale_items",
    "search_receipts",

    # RPC
    "checkout_sale_rpc",
    "purchase_receive_rpc",
    "refund_sale_rpc",
    "stock_adjustment_rpc",
    "update_product_rpc",
    "request_product_create_rpc",
    "request_product_bulk_create_rpc",
    "approve_product_create_rpc",

    # SERVICES
    "SalesService",
    "PurchaseService",
    "InventoryService",
    "RefundService",
    "ReceiptService",
    "PaymentService",
    "PaymentQRService",

    # PAYMENT
    "create_mobile_payment",
    "verify_payment",
    "reject_payment",
    "get_pending_payments",
    "generate_payment_qr",

    # SERVICE FACTORIES
    "get_sales_service",
    "get_purchase_service",
    "get_inventory_service",
    "get_refund_service",

    # HELPERS
    "get_fifo_cogs",
    "create_audit_log",

    # MULTI-TENANT
    "get_tenant_scoped_query",
    "get_current_tenant_id",
    "get_current_branch_id",
    "get_current_tenant_role",
    "tenant_aware_select",
    "tenant_aware_insert",
    "tenant_aware_update",
    "tenant_aware_delete",

    # UTILITIES
    "money",
    "money_float",
    "validate_uuid",
    "serialize_json",
    "safe_execute",
]


print(
    "ERP DATABASE GATEWAY v34 + MULTI-TENANT LOADED"
)
