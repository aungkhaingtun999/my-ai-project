# ==============================================================================
# erp_core/services.py
# ERP ENTERPRISE SERVICE COMPATIBILITY BRIDGE
# ==============================================================================


"""
Legacy compatibility module.

Old imports:

    from erp_core.services import SalesService

will continue working.

Real implementations are now inside:

    erp_core/services/

"""



from .services import (

    AccountingLedgerService,

    CustomerService,

    InventoryService,

    PurchaseService,

    RefundService,

    SalesService,

    DashboardService,

    AuditService

)



__all__ = [

    "AccountingLedgerService",

    "CustomerService",

    "InventoryService",

    "PurchaseService",

    "RefundService",

    "SalesService",

    "DashboardService",

    "AuditService",

]
