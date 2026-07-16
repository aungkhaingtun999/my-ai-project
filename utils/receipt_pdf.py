# ==========================================
# utils/receipt_pdf.py
# ERP ENTERPRISE PDF RECEIPT ENGINE v2
# ==========================================

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

import io
import json
import os

import streamlit as st



# ==========================================
# SHOP CONFIG
# ==========================================

def get_shop_info():

    config_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "pages",
        "config.json"
    )

    try:

        with open(
            config_path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)


    except Exception:

        return {

            "shop_name":
                "MY POS SYSTEM",

            "address":
                "Tachileik, Shan State, Myanmar",

            "phone":
                "09-XXXXXXXXXX",

            "footer_msg":
                "Thank you for shopping with us!"

        }



# ==========================================
# PDF GENERATOR
# ==========================================

def generate_pdf(data):

    try:

        shop = get_shop_info()


        buffer = io.BytesIO()


        pdf = canvas.Canvas(
            buffer,
            pagesize=A4
        )


        width, height = A4



        # ==========================
        # DATA COMPATIBILITY
        # ==========================

        receipt = data or {}


        items = (
            receipt.get("items")
            or
            receipt.get("cart")
            or []
        )



        # ==========================
        # HEADER
        # ==========================

        y = height - 50


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


        y -= 20


        pdf.setFont(
            "Helvetica",
            10
        )


        pdf.drawCentredString(
            width / 2,
            y,
            shop.get(
                "address",
                ""
            )
        )


        y -= 15


        pdf.drawCentredString(
            width / 2,
            y,
            f"Tel: {shop.get('phone','')}"
        )



        y -= 30


        pdf.drawString(
            50,
            y,
            f"Receipt No: {receipt.get('receipt_no','N/A')}"
        )


        y -= 15


        pdf.drawString(
            50,
            y,
            f"Date: {receipt.get('timestamp','N/A')}"
        )


        y -= 15


        pdf.drawString(
            50,
            y,
            f"Cashier: {receipt.get('cashier_name','Admin')}"
        )


        y -= 25



        pdf.line(
            50,
            y,
            550,
            y
        )



        # ==========================
        # TABLE HEADER
        # ==========================

        y -= 20


        pdf.setFont(
            "Helvetica-Bold",
            10
        )


        pdf.drawString(
            50,
            y,
            "Item"
        )

        pdf.drawString(
            280,
            y,
            "Qty"
        )

        pdf.drawString(
            340,
            y,
            "Price"
        )

        pdf.drawString(
            440,
            y,
            "Total"
        )


        y -= 20


        pdf.setFont(
            "Helvetica",
            10
        )



        # ==========================
        # ITEMS
        # ==========================

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


            price = float(
                item.get(
                    "selling_price",
                    0
                )
            )


            total = qty * price



            if y < 120:

                pdf.showPage()

                y = height - 50



            pdf.drawString(
                50,
                y,
                name[:30]
            )


            pdf.drawString(
                280,
                y,
                str(qty)
            )


            pdf.drawString(
                340,
                y,
                f"{price:,.0f}"
            )


            pdf.drawString(
                440,
                y,
                f"{total:,.0f}"
            )


            y -= 18



        # ==========================
        # TOTAL
        # ==========================

        y -= 20


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


        pdf.drawRightString(
            550,
            y,
            f"Subtotal : {receipt.get('subtotal',0):,.0f}"
        )


        y -= 18


        pdf.drawRightString(
            550,
            y,
            f"Discount : {receipt.get('discount',0):,.0f}"
        )


        y -= 18


        pdf.drawRightString(
            550,
            y,
            f"Tax : {receipt.get('tax',0):,.0f}"
        )


        y -= 25


        pdf.setFont(
            "Helvetica-Bold",
            13
        )


        pdf.drawRightString(
            550,
            y,
            f"TOTAL : {receipt.get('total',0):,.0f} MMK"
        )



        # ==========================
        # FOOTER
        # ==========================

        pdf.setFont(
            "Helvetica-Oblique",
            10
        )


        pdf.drawCentredString(
            width / 2,
            50,
            shop.get(
                "footer_msg",
                "Thank you!"
            )
        )



        pdf.save()



        buffer.seek(0)


        pdf_bytes = buffer.getvalue()


        buffer.close()



        # ==========================
        # STREAMLIT DOWNLOAD
        # ==========================

        st.download_button(

            label="⬇️ Download Receipt PDF",

            data=pdf_bytes,

            file_name=
                f"{receipt.get('receipt_no','receipt')}.pdf",

            mime="application/pdf"

        )


        return pdf_bytes



    except Exception as e:


        st.error(
            f"PDF Generate Error: {e}"
        )

        return None
