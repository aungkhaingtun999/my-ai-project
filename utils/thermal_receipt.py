from printer import get_printer

def print_receipt(receipt, items):

    p = get_printer()

    p.set(align="center", bold=True)
    p.text("MY POS SHOP\n")
    p.text("========================\n")

    p.set(align="left", bold=False)
    p.text(f"Receipt: {receipt['receipt_no']}\n")
    p.text(f"Date: {receipt['created_at']}\n")
    p.text("------------------------\n")

    for item in items:
        line = f"{item['name']} x{item['qty']}  {item['selling_price'] * item['qty']}\n"
        p.text(line)

    p.text("------------------------\n")
    p.set(bold=True)
    p.text(f"TOTAL: {receipt['total']}\n")
    p.text(f"PAID: {receipt['paid_amount']}\n")
    p.text(f"CHANGE: {receipt['change_amount']}\n")

    p.text("========================\n")
    p.text("THANK YOU!\n")

    p.cut()