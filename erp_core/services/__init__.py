# ==============================================================================
# erp_core/services/__init__.py
# ERP ENTERPRISE SERVICE LAYER v30.12
# SAFE SERVICE EXPORT PACKAGE
# ==============================================================================


"""
ERP Service Layer

Structure:

erp_core
 |
 └── services
        |
        ├── sales_service.py
        ├── customer_service.py
        ├── purchase_service.py
        ├── inventory_service.py
        └── dashboard_service.py


This file only exports service classes.

No database initialization.
No heavy imports.
"""



print("SERVICES PACKAGE START")



# ==============================================================================
# CORE DEPENDENCY CHECK
# ==============================================================================


from ..exceptions import *


from ..config import (

    log_error

)



# ==============================================================================
# CUSTOMER SERVICE
# ==============================================================================


try:

    from .customer_service import (

        CustomerService

    )

except Exception as e:

    print(
        "CustomerService import failed:",
        e
    )

    CustomerService = None





# ==============================================================================
# SALES SERVICE
# ==============================================================================


try:

    from .sales_service import (

        SalesService

    )

except Exception as e:

    print(
        "SalesService import failed:",
        e
    )

    SalesService = None





# ==============================================================================
# PURCHASE SERVICE
# ==============================================================================


try:

    from .purchase_service import (

        PurchaseService

    )

except Exception as e:

    print(
        "PurchaseService import failed:",
        e
    )

    PurchaseService = None





# ==============================================================================
# INVENTORY SERVICE
# ==============================================================================


try:

    from .inventory_service import (

        InventoryService

    )

except Exception as e:

    print(
        "InventoryService import failed:",
        e
    )

    InventoryService = None





# ==============================================================================
# REFUND SERVICE
# ==============================================================================


try:

    from .refund_service import (

        RefundService

    )

except Exception as e:

    print(
        "RefundService import failed:",
        e
    )

    RefundService = None





# ==============================================================================
# DASHBOARD SERVICE
# ==============================================================================


try:

    from .dashboard_service import (

        DashboardService

    )

except Exception as e:

    print(
        "DashboardService import failed:",
        e
    )

    DashboardService = None





# ==============================================================================
# ACCOUNTING SERVICE
# ==============================================================================


try:

    from .accounting_service import (

        AccountingLedgerService

    )

except Exception as e:

    print(
        "AccountingLedgerService import failed:",
        e
    )

    AccountingLedgerService = None





# ==============================================================================
# AUDIT SERVICE
# ==============================================================================


try:

    from .audit_service import (

        AuditService

    )

except Exception as e:

    print(
        "AuditService import failed:",
        e
    )

    AuditService = None





# ==============================================================================
# HELPER EXPORTS
# ==============================================================================


try:

    from .helpers import (

        get_fifo_cogs,

        create_audit_log

    )


except Exception as e:


    print(
        "Service helper import failed:",
        e
    )


    get_fifo_cogs = None

    create_audit_log = None





# ==============================================================================
# PUBLIC API
# ==============================================================================


__all__ = [


    "SalesService",

    "CustomerService",

    "PurchaseService",

    "InventoryService",

    "RefundService",

    "DashboardService",

    "AccountingLedgerService",

    "AuditService",

    "get_fifo_cogs",

    "create_audit_log"

]



print(
    "SERVICES PACKAGE READY"
)
