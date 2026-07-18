# ==============================================================================
# utils/receipt_pdf.py
# ERP ENTERPRISE v4.7.5 COMPATIBLE
# FINAL PRODUCTION RECEIPT PDF ENGINE
# ==============================================================================

from utils.timezone import format_datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

import io
import json
import os
import re
import streamlit as st

# ==============================================================================
# SHOP CONFIG
# ==============================================================================

def get_shop_info():

    config_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "pages",
        "config.json"
    )

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:

        return {
            "shop_name": "MY POS SYSTEM",
            "address": "Tachileik, Shan State, Myanmar",
            "phone": "09-267772367",
            "footer_msg": "Thank you for shopping with us!"
        }



# ==============================================================================
# SAFE NUMBER
# ==============================================================================

def num(value):

    try:
        return float(value or 0)

    except Exception:
        return 0.0



# ==============================================================================
# SAFE FILE NAME
# ==============================================================================

def safe_filename(name):

    name = str(name)

    return re.sub(
        r"[^A-Za-z0-9_\-]",
        "_",
        name
    )



# ==============================================================================
# PDF GENERATOR
# ==============================================================================

def generate_pdf(data):

    try:

        receipt = data or {}

        shop = get_shop_info()


        # ==================================================
        # DATA COMPATIBILITY MAP
        # ==================================================

        items = (
            receipt.get("items")
            or receipt.get("cart")
            or []
        )


        invoice_no = (
            receipt.get("invoice_no")
            or receipt.get("receipt_no")
            or receipt.get("invoice")
            or "INV-PENDING"
        )


        date_str = (
            receipt.get("date")
            or receipt.get("timestamp")
            or receipt.get("sale_date")
            or "N/A"
        )


        cashier = (
            receipt.get("cashier")
            or receipt.get("cashier_name")
            or "Admin"
        )


        subtotal = num(
            receipt.get("subtotal")
            or receipt.get("sub_total")
        )


        discount = num(
            receipt.get("discount")
        )


        tax_rate = num(
            receipt.get("tax_rate")
        )


        tax_amount = num(
            receipt.get("tax_amount")
            or receipt.get("tax")
        )


        grand_total = num(
            receipt.get("grand_total")
            or receipt.get("total")
        )


        paid = num(
            receipt.get("paid")
            or receipt.get("paid_amount")
        )


        change = num(
            receipt.get("change")
            or receipt.get("change_amount")
        )


        # ==================================================
        # CREATE PDF
        # ==================================================

        buffer = io.BytesIO()

        pdf = canvas.Canvas(
            buffer,
            pagesize=A4
        )


        width, height = A4


        y = height - 50



        # ==================================================
        # HEADER
        # ==================================================

        pdf.setFont(
            "Helvetica-Bold",
            18
        )

        pdf.drawCentredString(
            width / 2,
            y,
            shop.get(
                "shop_name",
                "MY POS SYSTEM"
            )
        )


        y -= 22


        pdf.setFont(
            "Helvetica",
            10
        )


        pdf.drawCentredString(
            width / 2,
            y,
            shop.get("address","")
        )


        y -= 15


        pdf.drawCentredString(
            width / 2,
            y,
            "Tel : " + shop.get("phone","")
        )



        # ==================================================
        # RECEIPT INFO
        # ==================================================

        y -= 35

        pdf.drawString(
            50,
            y,
            f"Receipt : {invoice_no}"
        )


        y -= 15

        pdf.drawString(
            50,
            y,
            f"Date : {date_str}"
        )


        y -= 15

        pdf.drawString(
            50,
            y,
            f"Cashier : {cashier}"
        )



        y -= 25


        pdf.line(
            50,
            y,
            550,
            y
        )



        # ==================================================
        # ITEM HEADER
        # ==================================================

        y -= 20


        pdf.setFont(
            "Helvetica-Bold",
            10
        )


        pdf.drawString(50,y,"Item")
        pdf.drawString(280,y,"Qty")
        pdf.drawString(350,y,"Price")
        pdf.drawString(460,y,"Amount")



        y -= 20


        pdf.setFont(
            "Helvetica",
            10
        )



        # ==================================================
        # ITEMS
        # ==================================================

        for item in items:


            name = str(
                item.get(
                    "name",
                    "Item"
                )
            )


            qty = int(
                item.get(
                    "qty",
                    0
                )
            )


            price = num(
                item.get("selling_price")
                or item.get("price")
            )


            amount = qty * price



            if y < 120:

                pdf.showPage()

                y = height - 50



            pdf.drawString(
                50,
                y,
                name[:30]
            )


            pdf.drawRightString(
                315,
                y,
                str(qty)
            )


            pdf.drawRightString(
                420,
                y,
                f"{price:,.0f}"
            )


            pdf.drawRightString(
                550,
                y,
                f"{amount:,.0f}"
            )


            y -= 18




        # ==================================================
        # TOTAL SECTION
        # ==================================================

        y -= 10


        pdf.line(
            50,
            y,
            550,
            y
        )


        y -= 25


        pdf.setFont(
            "Helvetica",
            11
        )


        lines = [

            f"Subtotal : {subtotal:,.0f} MMK",

            f"Discount : {discount:,.0f} MMK",

            f"Tax Rate : {tax_rate:.2f}%",

            f"Tax Amount : {tax_amount:,.0f} MMK",

            f"Paid : {paid:,.0f} MMK",

            f"Change : {change:,.0f} MMK"

        ]


        for line in lines:

            pdf.drawRightString(
                550,
                y,
                line
            )

            y -= 18



        pdf.setFont(
            "Helvetica-Bold",
            14
        )


        pdf.drawRightString(
            550,
            y-10,
            f"GRAND TOTAL : {grand_total:,.0f} MMK"
        )



        # ==================================================
        # FOOTER
        # ==================================================

        pdf.setFont(
            "Helvetica-Oblique",
            10
        )


        pdf.drawCentredString(
            width/2,
            60,
            shop.get(
                "footer_msg",
                "Thank you!"
            )
        )



        pdf.save()


        buffer.seek(0)


        pdf_bytes = buffer.getvalue()


        buffer.close()



        filename = safe_filename(invoice_no)


        st.download_button(

            label="⬇️ Download Receipt PDF",

            data=pdf_bytes,

            file_name=f"{filename}.pdf",

            mime="application/pdf",

            use_container_width=True

        )


        return pdf_bytes



    except Exception as e:

        st.error(
            f"PDF Generation Error: {e}"
        )

        return None
