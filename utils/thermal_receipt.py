# ==============================================================================
# utils/thermal_receipt.py
# ERP ENTERPRISE v4.7.5
# FINAL PRODUCTION THERMAL RECEIPT ENGINE
# ==============================================================================

import json
import os
import streamlit as st
from utils.timezone import format_datetime

try:
    from escpos.printer import Usb
except ImportError:
    Usb = None

# ==============================================================================
# SHOP CONFIG
# ==============================================================================

def get_shop_info():
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "pages", "config.json"
    )

    default_config = {
        "shop_name": "MY POS SYSTEM",
        "address": "Tachileik, Shan State, Myanmar",
        "phone": "09-267772367",
        "footer_msg": "THANK YOU\nVISIT AGAIN",
        "printer_vendor_id": "0x0000",
        "printer_product_id": "0x0000"
    }

    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return {**default_config, **json.load(f)}
    except Exception:
        pass
    
    return default_config

# ==============================================================================
# DUMMY PRINTER
# ==============================================================================

class DummyPrinter:
    def set(self, **kwargs): pass
    def text(self, msg): print(msg, end="")
    def feed(self, n=1): print("\n" * n)
    def cut(self): print("\n--- CUT ---\n")

# ==============================================================================
# PRINTER CONNECTION
# ==============================================================================

def get_printer():
    if Usb is None:
        st.error("python-escpos not installed")
        return DummyPrinter()

    shop = get_shop_info()

    try:
        vendor = int(shop.get("printer_vendor_id", "0x0000"), 16)
        product = int(shop.get("printer_product_id", "0x0000"), 16)

        st.info(f"Vendor ID : {hex(vendor)}")
        st.info(f"Product ID : {hex(product)}")

        if vendor == 0 or product == 0:
            st.warning("Printer Vendor/Product ID not configured.")
            return DummyPrinter()

        printer = Usb(vendor, product)
        st.success("USB Printer Connected")
        return printer

    except Exception as e:
        st.error(f"USB Printer Error : {e}")
        return DummyPrinter()

# ==============================================================================
# FORMATTING UTILITIES
# ==============================================================================

def line(left="", right="", width=32):
    left = str(left)
    right = str(right)
    space = width - len(left) - len(right)
    return f"{left}{' ' * max(space, 1)}{right}\n"

def num(value):
    try:
        return float(value or 0)
    except (ValueError, TypeError):
        return 0.0

# ==============================================================================
# THERMAL PRINT ENGINE
# ==============================================================================

def print_thermal(data):
    try:
        receipt = data or {}
        shop = get_shop_info()
        printer = get_printer()

        # Data Extraction
        items = receipt.get("items") or receipt.get("cart") or []
        invoice = receipt.get("invoice_no") or receipt.get("receipt_no") or receipt.get("invoice") or "INV-PENDING"
        date_str = receipt.get("date") or receipt.get("timestamp") or receipt.get("sale_date") or format_datetime()
        cashier = receipt.get("cashier") or receipt.get("cashier_name") or "Admin"
        
        subtotal = num(receipt.get("subtotal"))
        discount = num(receipt.get("discount"))
        tax_rate = num(receipt.get("tax_rate"))
        tax_amount = num(receipt.get("tax_amount") or receipt.get("tax"))
        total = num(receipt.get("grand_total") or receipt.get("total"))
        paid = num(receipt.get("paid") or receipt.get("paid_amount"))
        change = num(receipt.get("change") or receipt.get("change_amount"))

        # Print Header
        printer.set(align="center", bold=True)
        printer.text(f"{shop.get('shop_name')}\n")
        printer.text(f"{shop.get('address')}\n")
        printer.text(f"Tel: {shop.get('phone')}\n")
        printer.text("================================\n")

        printer.set(align="left", bold=False)
        printer.text(f"Receipt : {invoice}\n")
        printer.text(f"Date    : {date_str}\n")
        printer.text(f"Cashier : {cashier}\n")
        printer.text("--------------------------------\n")

        # Print Items
        for item in items:
            name = str(item.get("name", "Item"))
            qty = int(item.get("qty", 0))
            price = num(item.get("selling_price") or item.get("price"))
            amount = qty * price
            printer.text(line(f"{name[:18]} x{qty}", f"{amount:,.0f}"))

        printer.text("--------------------------------\n")

        # Print Totals
        printer.text(line("Subtotal:", f"{subtotal:,.0f}"))
        printer.text(line("Discount:", f"{discount:,.0f}"))
        printer.text(line(f"Tax {tax_rate:.2f}%:", f"{tax_amount:,.0f}"))
        printer.text(line("Paid:", f"{paid:,.0f}"))
        printer.text(line("Change:", f"{change:,.0f}"))
        printer.text("================================\n")

        # Final Total (Large Font)
        printer.set(bold=True, width=2, height=2)
        printer.text(line("TOTAL", f"{total:,.0f}"))
        printer.set(bold=False, width=1, height=1)

        printer.text("================================\n")

        # Footer
        printer.set(align="center")
        printer.text(f"{shop.get('footer_msg', 'THANK YOU')}\n")
        printer.feed(3)
        printer.cut()

    except Exception as e:
        st.error(f"THERMAL PRINT ERROR: {e}")
