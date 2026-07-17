# ==============================================================================
# utils/receipt_pdf.py
# ERP ENTERPRISE PDF RECEIPT ENGINE v4.1
# ==============================================================================

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
import json
import os
import streamlit as st

# ==============================================================================
# SHOP CONFIG
# ==============================================================================
def get_shop_info():
    config_path = os.path.join(os.path.dirname(__file__), "..", "pages", "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "shop_name": "MY POS SYSTEM",
            "address": "Tachileik, Shan State, Myanmar",
            "phone": "09-XXXXXXXXXX",
            "footer_msg": "Thank you for shopping with us!"
        }

# ==============================================================================
# PDF GENERATOR
# ==============================================================================
def generate_pdf(data):
    try:
        shop = get_shop_info()
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Receipt Data
        receipt = data or {}
        items = receipt.get("items") or []

        # Financial Data
        subtotal = float(receipt.get("subtotal", 0))
        discount = float(receipt.get("discount", 0))
        tax_rate = float(receipt.get("tax_rate", 0))
        tax = float(receipt.get("tax", 0))
        total = float(receipt.get("total", 0))
        paid = float(receipt.get("paid", 0))
        change = float(receipt.get("change", 0))

        # ==================================
        # HEADER
        # ==================================
        y = height - 50
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawCentredString(width / 2, y, shop.get("shop_name", "MY POS SYSTEM"))
        
        y -= 22
        pdf.setFont("Helvetica", 10)
        pdf.drawCentredString(width / 2, y, shop.get("address", ""))
        
        y -= 15
        pdf.drawCentredString(width / 2, y, "Tel : " + shop.get("phone", ""))
        
        y -= 30
        pdf.drawString(50, y, f"Receipt : {receipt.get('receipt_no', 'N/A')}")
        y -= 15
        pdf.drawString(50, y, f"Date : {receipt.get('timestamp', 'N/A')}")
        y -= 15
        pdf.drawString(50, y, f"Cashier : {receipt.get('cashier_name', 'Admin')}")
        
        y -= 25
        pdf.line(50, y, 550, y)

        # ==================================
        # ITEM TABLE
        # ==================================
        y -= 20
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(50, y, "Item")
        pdf.drawString(280, y, "Qty")
        pdf.drawString(350, y, "Price")
        pdf.drawString(460, y, "Amount")
        
        y -= 20
        pdf.setFont("Helvetica", 10)

        for item in items:
            name = str(item.get("name", "Item"))
            qty = int(item.get("qty", 0))
            price = float(item.get("selling_price", 0))
            amount = qty * price

            if y < 120:
                pdf.showPage()
                y = height - 50
                pdf.setFont("Helvetica", 10)

            pdf.drawString(50, y, name[:30])
            pdf.drawRightString(315, y, str(qty))
            pdf.drawRightString(420, y, f"{price:,.0f}")
            pdf.drawRightString(550, y, f"{amount:,.0f}")
            y -= 18

        # ==================================
        # TOTAL SECTION
        # ==================================
        y -= 10
        pdf.line(50, y, 550, y)
        y -= 22
        pdf.setFont("Helvetica", 11)
        
        pdf.drawRightString(550, y, f"Subtotal : {subtotal:,.0f} MMK")
        y -= 18
        pdf.drawRightString(550, y, f"Discount : {discount:,.0f} MMK")
        y -= 18
        pdf.drawRightString(550, y, f"Tax Rate : {tax_rate:.2f}%")
        y -= 18
        pdf.drawRightString(550, y, f"Tax Amount : {tax:,.0f} MMK")
        y -= 18
        pdf.drawRightString(550, y, f"Paid : {paid:,.0f} MMK")
        y -= 18
        pdf.drawRightString(550, y, f"Change : {change:,.0f} MMK")
        
        y -= 25
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawRightString(550, y, f"GRAND TOTAL : {total:,.0f} MMK")

        # ==================================
        # FOOTER
        # ==================================
        pdf.setFont("Helvetica-Oblique", 10)
        pdf.drawCentredString(width / 2, 60, shop.get("footer_msg", "Thank you!"))

        pdf.save()
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        st.download_button(
            label="⬇️ Download Receipt PDF",
            data=pdf_bytes,
            file_name=f"{receipt.get('receipt_no', 'receipt')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        return pdf_bytes

    except Exception as e:
        st.error(f"PDF Generation Error: {e}")
        return None
