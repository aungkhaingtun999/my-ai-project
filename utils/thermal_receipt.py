# utils/thermal_receipt.py
from datetime import datetime
from escpos.printer import Usb

class DummyPrinter:
    def set(self, **kwargs): pass
    def text(self, msg): print(msg, end="")
    def cut(self): print("\n--- CUT ---\n")

def get_printer():
    try:
        # သင်၏ ပရင်တာ ID များမှန်ကန်ကြောင်း စစ်ဆေးပါ
        return Usb(0x0000, 0x0000)
    except:
        return DummyPrinter()

def line(left="", right="", width=32):
    left, right = str(left), str(right)
    space = width - len(left) - len(right)
    return left + (" " * max(1, space)) + right + "\n"

# POS.py မှ print_thermal(data) ဟု ခေါ်သောကြောင့် ဤနာမည်အတိအကျဖြစ်ရမည်
def print_thermal(data):
    p = get_printer()
    receipt = data
    items = data.get("cart", [])
    
    try:
        p.set(align="center", bold=True)
        p.text("MY POS SHOP\n========================\n")
        p.set(align="left", bold=False)
        p.text(line("Receipt:", receipt.get("receipt_no", "")))
        p.text(line("Date:", datetime.now().strftime("%Y-%m-%d %H:%M")))
        p.text("------------------------\n")
        
        for item in items:
            name = item.get("name", "Item")
            qty = item.get("qty", 0)
            price = float(item.get("selling_price", 0))
            p.text(line(f"{name} x{qty}", f"{qty*price:.0f}"))
            
        p.text("------------------------\n")
        p.set(bold=True)
        p.text(line("TOTAL", f"{receipt.get('total', 0):.0f}"))
        p.text("========================\n")
        p.set(align="center", bold=False)
        p.text("THANK YOU\n\n")
        p.cut()
    except Exception as e:
        print("Printer Error:", e)

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
