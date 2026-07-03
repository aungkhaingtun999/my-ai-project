from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

def generate_pdf_receipt(receipt, items, filename):

    os.makedirs("receipts", exist_ok=True)

    file_path = f"receipts/{filename}.pdf"

    c = canvas.Canvas(file_path, pagesize=A4)

    width, height = A4

    # =========================
    # HEADER
    # =========================
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 800, "MY POS SYSTEM")

    c.setFont("Helvetica", 10)
    c.drawString(50, 770, f"Receipt No: {receipt['receipt_no']}")
    c.drawString(50, 755, f"Date: {receipt['created_at']}")

    # =========================
    # ITEMS HEADER
    # =========================
    y = 720
    c.drawString(50, y, "Item")
    c.drawString(250, y, "Qty")
    c.drawString(300, y, "Price")
    c.drawString(400, y, "Total")

    y -= 20

    # =========================
    # ITEMS LIST
    # =========================
    for item in items:
        c.drawString(50, y, str(item["name"]))
        c.drawString(250, y, str(item["quantity"]))
        c.drawString(300, y, str(item["unit_price"]))
        c.drawString(400, y, str(item["total"]))
        y -= 20

    # =========================
    # TOTAL
    # =========================
    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(300, y, f"TOTAL: {receipt['total']}")

    y -= 20
    c.drawString(300, y, f"PAID: {receipt['paid_amount']}")

    y -= 20
    c.drawString(300, y, f"CHANGE: {receipt['change_amount']}")

    c.save()

    return file_path