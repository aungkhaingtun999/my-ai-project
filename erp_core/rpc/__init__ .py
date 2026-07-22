# ==============================================================================
# erp_core/rpc/__init__.py
# ERP ENTERPRISE RPC PACKAGE v30.11
# ==============================================================================


try:

    from .checkout_rpc import checkout_sale_rpc

except Exception as e:

    checkout_sale_rpc = None



try:

    from .purchase_rpc import purchase_receive_rpc

except Exception:

    purchase_receive_rpc = None



try:

    from .refund_rpc import refund_sale_rpc

except Exception:

    refund_sale_rpc = None



try:

    from .stock_rpc import stock_adjustment_rpc

except Exception:

    stock_adjustment_rpc = None



__all__ = [

    "checkout_sale_rpc",

    "purchase_receive_rpc",

    "refund_sale_rpc",

    "stock_adjustment_rpc",

]
