import json
import os

try:
    from escpos.printer import Usb
except ImportError:
    Usb = None

# ==========================================
# SHOP CONFIG
# ==========================================

def get_shop_info():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'pages', 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {
            "shop_name": "MY POS SYSTEM",
            "address": "Tachileik, Shan State, Myanmar",
            "phone": "09-267772367",
            "footer_msg": "THANK YOU\nVISIT AGAIN",
            "printer_vendor_id": "0x0000",
            "printer_product_id": "0x0000"
        }

# ==========================================
# DUMMY PRINTER
# ==========================================

class DummyPrinter:
    def set(self, **kwargs): pass
    def text(self, msg): print(msg, end="")
    def feed(self, n=1): print("\n" * n)
    def cut(self): print("\n--- CUT ---\n")

def get_printer():
    if Usb is None: return DummyPrinter()
    shop = get_shop_info()
    try:
        vendor = int(shop.get("printer_vendor_id", "0x0000"), 16)
        product = int(shop.get("printer_product_id", "0x0000"), 16)
        if vendor == 0 and product == 0: return DummyPrinter()
        return Usb(vendor, product)
    except Exception:
        return DummyPrinter()

def line(left="", right="", width=32):
    left = str(left)
    right = str(right)
    space = width - len(left) - len(right)
    return left + (" " * max(space, 1)) + right + "\n"

# ==========================================
# THERMAL PRINT ENGINE (COMPATIBLE v4.5)
# ==========================================

def print_thermal(data):
    shop = get_shop_info()
    p = get_printer()
    receipt = data or {}
    
    # Compatibility Mapping (Old keys + New keys)
    items = receipt.get("items") or receipt.get("cart") or []
    invoice = receipt.get("invoice_no") or receipt.get("invoice") or "N/A"
    date_str = receipt.get("date") or receipt.get("sale_date") or "N/A"
    cashier = receipt.get("cashier") or "Admin"
    
    # Financial Data
    subtotal = float(receipt.get("subtotal", 0))
    discount = float(receipt.get("discount", 0))
    tax_rate = float(receipt.get("tax_rate", 0))
    tax_amt = float(receipt.get("tax_amount") or receipt.get("tax", 0))
    total = float(receipt.get("total") or receipt.get("grand_total", 0))
    paid = float(receipt.get("paid", 0))
    change = float(receipt.get("change", 0))

    try:
        p.set(align="center", bold=True)
        p.text(f"{shop.get('shop_name', 'MY POS SYSTEM')}\n")
        
        if shop.get("address"): p.text(f"{shop['address']}\n")
        if shop.get("phone"): p.text(f"Tel: {shop['phone']}\n")
        
        p.text("================================\n")
        p.set(align="left", bold=False)
        p.text(f"Receipt: {invoice}\n")
        p.text(f"Date: {date_str}\n")
        p.text(f"Cashier: {cashier}\n")
        p.text("--------------------------------\n")

        # Items
        for item in items:
            name = item.get("name", "Item")
            qty = int(item.get("qty", 0))
            price = float(item.get("selling_price") or item.get("price", 0))
            amount = qty * price
            p.text(line(f"{name[:18]} x{qty}", f"{amount:,.0f}"))

        p.text("--------------------------------\n")

        # Total Section
        p.text(line("Subtotal:", f"{subtotal:,.0f}"))
        p.text(line("Discount:", f"{discount:,.0f}"))
        p.text(line(f"Tax ({tax_rate:.2f}%):", f"{tax_amt:,.0f}"))
        p.text(line("Paid:", f"{paid:,.0f}"))
        p.text(line("Change:", f"{change:,.0f}"))
        
        p.text("--------------------------------\n")
        p.set(bold=True, width=2, height=2)
        p.text(line("TOTAL", f"{total:,.0f}"))
        p.set(bold=False, width=1, height=1)
        p.text("================================\n")

        # Footer
        p.set(align="center")
        p.text(f"{shop.get('footer_msg', 'THANK YOU')}\n\n")
        
        p.feed(3)
        p.cut()

    except Exception as e:
        print("Printer Error:", e)
