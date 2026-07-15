# utils/thermal_receipt.py
import json
import os
try:
    from escpos.printer import Usb
except ImportError:
    Usb = None

def get_shop_info():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            "shop_name": "MY POS SHOP",
            "address": "Tachileik, Myanmar",
            "footer_msg": "THANK YOU\nVISIT AGAIN"
        }

class DummyPrinter:
    def set(self, **kwargs): pass
    def text(self, msg): print(msg, end="")
    def cut(self): print("\n--- CUT ---\n")

def get_printer():
    if Usb is None:
        return DummyPrinter()
    try:
        # သင်၏ ပရင်တာ ID များမှန်ကန်ကြောင်း စစ်ဆေးပါ
        return Usb(0x0000, 0x0000)
    except:
        return DummyPrinter()

def line(left="", right="", width=32):
    left, right = str(left), str(right)
    space = width - len(left) - len(right)
    return left + (" " * max(1, space)) + right + "\n"

def print_thermal(data):
    shop = get_shop_info()
    p = get_printer()
    receipt = data
    items = data.get("cart", [])
    timestamp = receipt.get("timestamp", "N/A")
    
    try:
        p.set(align="center", bold=True)
        p.text(f"{shop['shop_name']}\n")
        p.text("========================\n")
        
        p.set(align="left", bold=False)
        p.text(f"Receipt: {receipt.get('receipt_no', '')}\n")
        p.text(f"Date: {timestamp}\n")
        p.text(f"Cashier: {receipt.get('cashier_name', 'Admin')}\n")
        p.text("------------------------\n")
        
        # Items
        for item in items:
            name = item.get("name", "Item")
            qty = item.get("qty", 0)
            price = float(item.get("selling_price", 0))
            p.text(line(f"{name} x{qty}", f"{qty*price:,.0f}"))
            
        p.text("------------------------\n")
        
        # Financial Details
        p.text(line("Subtotal:", f"{receipt.get('subtotal', 0):,.0f}"))
        p.text(line("Discount:", f"{receipt.get('discount', 0):,.0f}"))
        p.text(line("Tax:", f"{receipt.get('tax', 0):,.0f}"))
        
        p.set(bold=True)
        p.text("------------------------\n")
        p.text(line("GRAND TOTAL:", f"{receipt.get('total', 0):,.0f}"))
        p.text("========================\n")
        
        p.set(align="center", bold=False)
        p.text(f"{shop['footer_msg']}\n\n")
        p.cut()
        
    except Exception as e:
        print("Printer Error:", e)
        
