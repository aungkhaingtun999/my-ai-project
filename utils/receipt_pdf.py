# ==========================================
# receipt_pdf.py
# Production POS PDF Generator (A4)
# ==========================================

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from datetime import datetime


# ==========================
# MAIN FUNCTION
# ==========================

def generate_pdf_receipt(receipt, items, filename):

    os.makedirs("receipts", exist_ok=True)

    file_path = f"receipts/{filename}.pdf"

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # ==========================
    # HEADER
    # ==========================
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, 800, "MY POS SYSTEM")

    c.setFont("Helvetica", 10)

    c.drawString(50, 770,
                 f"Receipt No: {receipt.get('receipt_no', '')}")

    c.drawString(50, 755,
                 f"Date: {receipt.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M'))}")

    c.drawString(50, 740, "-" * 90)

    # ==========================
    # TABLE HEADER
    # ==========================
    y = 720

    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Item")
    c.drawString(250, y, "Qty")
    c.drawString(320, y, "Price")
    c.drawString(420, y, "Total")

    y -= 20

    c.setFont("Helvetica", 10)

    # ==========================
    # ITEMS LIST
    # ==========================
    for item in items:

        name = item.get("name", "Item")
        qty = item.get("qty") or item.get("quantity", 0)
        price = item.get("selling_price") or item.get("unit_price", 0)

        total = qty * price

        # page break protection
        if y < 100:
            c.showPage()
            y = 800

        c.drawString(50, y, str(name)[:25])   # truncate long name
        c.drawString(250, y, str(qty))
        c.drawString(320, y, f"{price:,.0f}")
        c.drawString(420, y, f"{total:,.0f}")

        y -= 20

    # ==========================
    # TOTAL SECTION
    # ==========================
    y -= 20
    c.drawString(50, y, "-" * 90)

    y -= 30

    c.setFont("Helvetica-Bold", 12)

    c.drawString(320, y,
                 f"TOTAL: {receipt.get('total', 0):,.0f}")

    y -= 20
    c.drawString(320, y,
                 f"PAID: {receipt.get('paid_amount', 0):,.0f}")

    y -= 20
    c.drawString(320, y,
                 f"CHANGE: {receipt.get('change_amount', 0):,.0f}")

    # ==========================
    # FOOTER
    # ==========================
    y -= 50
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, y, "Thank you for shopping with us!")

    c.save()

    return file_path