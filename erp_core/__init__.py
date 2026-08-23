# ==============================================================================
# erp_core/__init__.py
# ERP ENTERPRISE CORE
# LIGHTWEIGHT PACKAGE INITIALIZER
#
# IMPORTANT
# ------------------------------------------------------------------------------
# DO NOT eagerly import loaders / RPC / services here.
#
# Why:
#   from erp_core.base_repo import db
#
# first executes this __init__.py.
#
# If this file eagerly imports a service/loader/RPC which imports auth,
# it creates:
#
#     auth
#       ↓
#     erp_core
#       ↓
#     service/loader/RPC
#       ↓
#     auth
#
# resulting in:
#
#     cannot import name 'change_password' from 'auth'
#
# Therefore erp_core package initialization must remain lightweight.
# ==============================================================================

print("ERP CORE PACKAGE START")


# ==============================================================================
# VERSION
# ==============================================================================

ERP_CORE_EXPORT_VERSION = "38.0"


# ==============================================================================
# BASIC PUBLIC METADATA ONLY
# ==============================================================================
#
# Do NOT import:
#
#   base_repo
#   loaders
#   rpc
#   services
#   auth
#
# from this package initializer.
#
# Modules should import the exact dependency they need.
#
# Example:
#
#     from erp_core.base_repo import db
#
#     from erp_core.services.inventory_service import InventoryService
#
# ==============================================================================


__all__ = [
    "ERP_CORE_EXPORT_VERSION",
]


print(
    f"ERP CORE PACKAGE READY v{ERP_CORE_EXPORT_VERSION}"
)
