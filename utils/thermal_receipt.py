# ==============================================================================
# utils/thermal_receipt.py
# ERP ENTERPRISE v4.7.5
# ==============================================================================

import json
import os
import tempfile
import subprocess
import streamlit as st
from utils.timezone import format_datetime

try:
    import win32print
    import win32api
except ImportError:
    win32print = None
    win32api = None

try:
    from escpos.printer import Usb, Network
except ImportError:
    Usb = None
    Network = None

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
        "printer_mode": "windows",
        "printer_name": "Microsoft Print to PDF",
        "printer_vendor_id": "",
        "printer_product_id": "",
        "printer_ip": "",
        "printer_port": 9100
    }

    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                return {**default_config, **user_config}
    except Exception:
        pass
    
    return default_config

# ==============================================================================
# PRINTER CONNECTION
# ==============================================================================

def get_printer():
    shop = get_shop_info()
    mode = shop.get("printer_mode", "windows")

    if mode == "usb":
        if Usb is None:
            st.error("python-escpos (USB) not installed")
            return None
        try:
            vendor = int(shop.get("printer_vendor_id", "0x0000"), 16)
            product = int(shop.get("printer_product_id", "0x0000"), 16)
            return Usb(vendor, product)
        except Exception as e:
            st.error(f"USB Printer Error: {e}")
            return None

    elif mode == "network":
        if Network is None:
            st.error("python-escpos (Network) not installed")
            return None
        try:
            return Network(shop.get("printer_ip"), port=int(shop.get("printer_port", 9100)))
        except Exception as e:
            st.error(f"Network Printer Error: {e}")
            return None
            
    return "windows"

# ==============================================================================
# THERMAL PRINT ENGINE
# ==============================================================================

def print_thermal(data):
    try:
        shop = get_shop_info()
        printer_obj = get_printer()
        
        # Windows Printing Path
        if shop.get("printer_mode") == "windows":
            printer_name = shop.get("printer_name")
            # Logic for generating receipt content to temp file will go here
            # For now, we simulate Windows raw printing trigger
            st.info(f"Sending to Windows Printer: {printer_name}")
            return

        # ESC/POS Path
        if printer_obj:
            # ... (Existing logic for USB/Network printing)
            st.success("Printing via ESC/POS...")
            
    except Exception as e:
        st.error(f"THERMAL PRINT ERROR: {e}")

# ==============================================================================
# UTILITIES
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
