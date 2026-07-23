# ==========================================
# utils/receipt_pdf.py
# ERP ENTERPRISE RECEIPT PDF GENERATOR
# ==========================================

import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors


def num(val):
    try:
        return float(val or 0)
    except (ValueError, TypeError):
        return 0.0


def generate_pdf(receipt_data):
    """
    Generates a professional receipt PDF from receipt data dictionary.
    Returns a tuple of (pdf_bytes, filename) or None on failure.
    """
    try:
        invoice_no = receipt_data.get("invoice_no", "INV-UNKNOWN")
        filename = f"Receipt_{invoice_no}"
        
        # Temporary file path for generation
        pdf_path = f"{filename}.pdf"

        # Setup canvas
        pdf = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter

        # ==========================================
        # HEADER SECTION
        # ==========================================
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, height - 50, "ERP ENTERPRISE")
        
        pdf.setFont("Helvetica", 10)
        pdf.drawRightString(width - 50, height - 50, f"Date: {receipt_data.get('date', '-')}")
        
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, height - 75, "OFFICIAL RECEIPT")
        
        pdf.setFont("Helvetica", 10)
        pdf.drawString(50, height - 95, f"Invoice No: {invoice_no}")
        pdf.drawString(50, height - 110, f"Cashier: {receipt_data.get('cashier', 'Admin')}")

        # ==========================================
        # TABLE HEADERS
        # ==========================================
        y = height - 145
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(50, y, "Item Description")
        pdf.drawRightString(315, y, "Qty")
        pdf.drawRightString(420, y, "Price (MMK)")
        pdf.drawRightString(550, y, "Amount (MMK)")

        y -= 10
        pdf.setStrokeColor(colors.gray)
        pdf.setLineWidth(0.5)
        pdf.line(50, y, width - 50, y)

        # ==========================================
        # ITEMS SECTION
        # ==========================================
        y -= 20
        pdf.setFont("Helvetica", 10)

        items = receipt_data.get("items", [])

        for item in items:
            # Product Name fallback mapping
            name = (
                item.get("name")
                or item.get("product_name")
                or f"Product #{item.get('product_id', '')}"
            )

            # Quantity fallback mapping
            qty = int(
                item.get("quantity")
                or item.get("qty")
                or 0
            )

            # Unit Price fallback mapping
            price = num(
                item.get("unit_price")
                or item.get("selling_price")
                or item.get("price")
            )

            # Total from database or calculated fallback
            amount = num(
                item.get("total")
                or item.get("amount")
            )

            if amount == 0:
                amount = qty * price

            if y < 120:
                pdf.showPage()
                y = height - 50

            pdf.drawString(50, y, str(name)[:30])
            pdf.drawRightString(315, y, str(qty))
            pdf.drawRightString(420, y, f"{price:,.0f}")
            pdf.drawRightString(550, y, f"{amount:,.0f}")

            y -= 18

        # ==========================================
        # FINANCIAL TOTALS SECTION
        # ==========================================
        y -= 10
        pdf.line(300, y, width - 50, y)
        y -= 20

        subtotal = num(receipt_data.get("subtotal"))
        discount = num(receipt_data.get("discount"))
        tax = num(receipt_data.get("tax_amount"))
        grand_total = num(receipt_data.get("grand_total"))
        paid = num(receipt_data.get("paid"))
        change = num(receipt_data.get("change"))

        pdf.setFont("Helvetica", 10)
        
        pdf.drawString(350, y, "Subtotal:")
        pdf.drawRightString(550, y, f"{subtotal:,.0f} MMK")
        y -= 15

        if discount > 0:
            pdf.drawString(350, y, "Discount:")
            pdf.drawRightString(550, y, f"-{discount:,.0f} MMK")
            y -= 15

        if tax > 0:
            pdf.drawString(350, y, "Tax:")
            pdf.drawRightString(550, y, f"{tax:,.0f} MMK")
            y -= 15

        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(350, y, "GRAND TOTAL:")
        pdf.drawRightString(550, y, f"{grand_total:,.0f} MMK")
        y -= 20

        pdf.setFont("Helvetica", 10)
        pdf.drawString(350, y, "Paid:")
        pdf.drawRightString(550, y, f"{paid:,.0f} MMK")
        y -= 15

        pdf.drawString(350, y, "Change:")
        pdf.drawRightString(550, y, f"{change:,.0f} MMK")

        # ==========================================
        # FOOTER
        # ==========================================
        y -= 40
        pdf.setFont("Helvetica-Oblique", 9)
        pdf.drawCentredString(width / 2.0, y, "Thank you for your business!")

        pdf.save()

        # Read bytes and cleanup temp file
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        return pdf_bytes, filename

    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None
