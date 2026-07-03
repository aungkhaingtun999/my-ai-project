# ==========================================
# printer.py
# Production Thermal Printer Engine
# ==========================================

from datetime import datetime

# ==========================
# GET PRINTER (SAFE)
# ==========================

def get_printer():
    """
    Safe printer initialization
    Replace with real ESC/POS printer later
    """

    try:
        from escpos.printer import Usb

        # 🔧 CHANGE THIS FOR YOUR PRINTER
        # Vendor ID / Product ID
        p = Usb(0x0000, 0x0000)

        return p

    except Exception:
        return DummyPrinter()


# ==========================
# DUMMY PRINTER (FALLBACK)
# ==========================

class DummyPrinter:
    def set(self, **kwargs):
        pass

    def text(self, msg):
        print(msg, end="")

    def cut(self):
        print("\n--- CUT ---\n")


# ==========================
# FORMAT HELPERS
# ==========================

def line(left="", right="", width=32):
    """
    Align text like receipt layout
    """
    left = str(left)
    right = str(right)

    space = width - len(left) - len(right)
    if space < 0:
        space = 1

    return left + (" " * space) + right + "\n"


# ==========================
# MAIN PRINT FUNCTION
# ==========================

def print_receipt(receipt, items):

    p = get_printer()

    # ==========================
    # HEADER
    # ==========================
    try:
        p.set(align="center", bold=True)
        p.text("MY POS SHOP\n")
        p.text("========================\n")

        # ==========================
        # META INFO
        # ==========================
        p.set(align="left", bold=False)

        p.text(line("Receipt:", receipt.get("receipt_no", "")))
        p.text(line("Date:", receipt.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M"))))
        p.text("------------------------\n")

        # ==========================
        # ITEMS
        # ==========================
        for item in items:

            name = item.get("name", "Item")
            qty = item.get("qty", 0)
            price = item.get("selling_price", 0)
            total = qty * price

            p.text(line(f"{name} x{qty}", f"{total:.0f}"))

        p.text("------------------------\n")

        # ==========================
        # TOTAL SECTION
        # ==========================
        p.set(bold=True)

        p.text(line("TOTAL", f"{receipt.get('total', 0):.0f}"))
        p.text(line("PAID", f"{receipt.get('paid_amount', 0):.0f}"))
        p.text(line("CHANGE", f"{receipt.get('change_amount', 0):.0f}"))

        p.text("========================\n")

        # ==========================
        # FOOTER
        # ==========================
        p.set(align="center", bold=False)
        p.text("THANK YOU\nVISIT AGAIN\n")

        p.cut()

    except Exception as e:
        print("Printer Error:", e)