# ==========================================
# utils/thermal_receipt.py
# ERP ENTERPRISE THERMAL PRINT ENGINE v4.2
# ==========================================

import json
import os
try:
    from escpos.printer import Usb
except ImportError:
    Usb = None

def get_shop_info():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'pages', 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            "shop_name": "MY POS SYSTEM",
            "address": "Tachileik, Shan State, Myanmar",
            "phone": "09-XXXXXXXXXX",
            "footer_msg": "THANK YOU\nVISIT AGAIN",
            "printer_vendor_id": "0x0000",
            "printer_product_id": "0x0000"
        }

class DummyPrinter:
    def set(self, **kwargs): pass
    def text(self, msg): print(msg, end="")
    def feed(self, n=1): print("\n" * n, end="")
    def cut(self): print("\n--- CUT ---\n")

def get_printer():
    if Usb is None:
        return DummyPrinter()
    
    shop = get_shop_info()
    try:
        # Config မှ IDs များကို integer (hex base) သို့ ပြောင်းလဲခြင်း
        vendor = int(shop.get("printer_vendor_id", "0x0000"), 16)
        product = int(shop.get("printer_product_id", "0x0000"), 16)
        
        # Valid ID ရှိမှသာ Usb object ကို တည်ဆောက်ပါ
        if vendor == 0 and product == 0:
            return DummyPrinter()
            
        return Usb(vendor, product)
    except:
        return DummyPrinter()

def line(left="", right="", width=32):
    left, right = str(left), str(right)
    space = width - len(left) - len(right)
    return left + (" " * max(1, space)) + right + "\n"

def print_thermal(data):
    shop = get_shop_info()
    p = get_printer()
    receipt = data or {}
    items = receipt.get("items") or receipt.get("cart") or []
    
    # Financials
    subtotal = float(receipt.get("subtotal") or 0)
    discount = float(receipt.get("discount") or 0)
    tax_rate = float(receipt.get("tax_rate") or 0)
    total = float(receipt.get("total") or 0)
    paid = float(receipt.get("paid") or 0)
    change = float(receipt.get("change") or 0)

    # --- ENTERPRISE AUTO CALCULATE ---
    if subtotal == 0 and items:
        subtotal = sum(
            float(item.get("selling_price", item.get("unit_price", item.get("price", 0))))
            * int(item.get("qty", item.get("quantity", 0)))
            for item in items
        )
    
    if total == 0:
        total = subtotal - discount + tax
    # ---------------------------------
    
    try:
        p.set(align="center", bold=True)
        p.text(f"{shop.get('shop_name', 'MY POS SYSTEM')}\n")
        if shop.get('address'): p.text(f"{shop['address']}\n")
        if shop.get('phone'): p.text(f"Tel: {shop['phone']}\n")
        p.text("================================\n")
        
        p.set(align="left", bold=False)
        p.text(f"Receipt: {receipt.get('receipt_no', 'N/A')}\n")
        p.text(f"Date: {receipt.get('timestamp', 'N/A')}\n")
        p.text(f"Cashier: {receipt.get('cashier_name', 'Admin')}\n")
        p.text(f"Payment: {receipt.get('method', 'Cash')}\n")
        p.text("--------------------------------\n")
        
        # Items Loop
        for item in items:
            name = item.get("name", "Item")
            qty = int(item.get("qty", item.get("quantity", 0)))
            price = float(item.get("selling_price", item.get("unit_price", item.get("price", 0))))
            amount = qty * price
            p.text(line(f"{name[:18]} x{qty}", f"{amount:,.0f}"))
            
        p.text("--------------------------------\n")
        
        # Financial Details
        p.text(line("Subtotal:", f"{subtotal:,.0f}"))
        p.text(line("Discount:", f"{discount:,.0f}"))
        p.text(
    line(
        f"Tax ({tax_rate:.2f}%):",
        f"{tax:,.0f}"
    )
        )
        p.text(line("Paid:", f"{paid:,.0f}"))
        p.text(line("Change:", f"{change:,.0f}"))
        
        # Enhanced Total Display
        p.text("--------------------------------\n")
        p.set(bold=True, width=2, height=2)
        p.text(line("TOTAL", f"{total:,.0f} MMK"))
        p.set(bold=False, width=1, height=1)
        p.text("================================\n")
        
        p.set(align="center", bold=False)
        p.text(f"{shop.get('footer_msg', 'THANK YOU')}\n\n")
        p.cut()
        
    except Exception as e:
        print("Printer Error:", e)
            
