# ==============================================================================
# utils/receipt_pdf.py
# ERP ENTERPRISE RECEIPT PDF ENGINE v4.8
# SALE_ITEMS COMPATIBLE VERSION
# ==============================================================================


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
                "09-267772367",

            "footer_msg":
                "Thank you for shopping with us!"

        }



# ==============================================================================
# SAFE NUMBER
# ==============================================================================


def num(value):

    try:

        return float(
            value or 0
        )

    except Exception:

        return 0



# ==============================================================================
# SAFE FILE NAME
# ==============================================================================


def safe_filename(name):

    return re.sub(
        r"[^A-Za-z0-9_\-]",
        "_",
        str(name)
    )



# ==============================================================================
# ITEM NORMALIZER
# ==============================================================================


def normalize_item(item):
def normalize_item(item):

    """
    Support:

    Database format:
    quantity
    unit_price
    total


    Receipt page format:
    name
    qty
    price
    amount

    """

    return {

        "name":
            item.get(
                "name",
                f"Product #{item.get('product_id','')}"
            ),


        "qty":
            int(
                item.get(
                    "qty",
                    item.get(
                        "quantity",
                        0
                    )
                )
            ),


        "price":
            num(
                item.get(
                    "price",
                    item.get(
                        "unit_price",
                        0
                    )
                )
            ),


        "amount":
            num(

                item.get(
                    "amount",

                    item.get(
                        "total",
                        0
                    )

                )

            )

    }




# ==============================================================================
# PDF GENERATOR
# ==============================================================================


def generate_pdf(data):

    try:


        receipt = data or {}

        shop = get_shop_info()



        raw_items = (

            receipt.get("items")

            or

            receipt.get("cart")

            or

            []

        )



        items = [

            normalize_item(i)

            for i in raw_items

        ]



        invoice_no = (

            receipt.get("invoice_no")

            or

            "INV-PENDING"

        )



        date_str = (

            receipt.get("date")

            or

            "N/A"

        )



        cashier = (

            receipt.get("cashier")

            or

            "Admin"

        )



        subtotal = num(
            receipt.get(
                "subtotal"
            )
        )


        discount = num(
            receipt.get(
                "discount"
            )
        )


        tax_amount = num(
            receipt.get(
                "tax_amount",
                receipt.get(
                    "tax"
                )
            )
        )


        grand_total = num(
            receipt.get(
                "grand_total",
                receipt.get(
                    "total"
                )
            )
        )


        paid = num(
            receipt.get(
                "paid"
            )
        )


        change = num(
            receipt.get(
                "change"
            )
        )



        buffer = io.BytesIO()


        pdf = canvas.Canvas(
            buffer,
            pagesize=A4
        )


        width,height = A4


        y = height - 50



        # --------------------------------------------------
        # HEADER
        # --------------------------------------------------


        pdf.setFont(
            "Helvetica-Bold",
            18
        )


        pdf.drawCentredString(
            width/2,
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
            width/2,
            y,
            shop.get(
                "address",
                ""
            )
        )


        y -= 15


        pdf.drawCentredString(
            width/2,
            y,
            "Tel : "
            +
            shop.get(
                "phone",
                ""
            )
        )



        # --------------------------------------------------
        # RECEIPT INFO
        # --------------------------------------------------


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



        # --------------------------------------------------
        # ITEM HEADER
        # --------------------------------------------------


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
            350,
            y,
            "Price"
        )


        pdf.drawString(
            460,
            y,
            "Amount"
        )


        y -= 20


        pdf.setFont(
            "Helvetica",
            10
        )



        # --------------------------------------------------
        # ITEMS
        # --------------------------------------------------


        for item in items:


            if y < 120:

                pdf.showPage()

                y = height - 50



            pdf.drawString(
                50,
                y,
                item["name"][:30]
            )


            pdf.drawRightString(
                315,
                y,
                str(
                    item["qty"]
                )
            )


            pdf.drawRightString(
                420,
                y,
                f"{item['price']:,.0f}"
            )


            pdf.drawRightString(
                550,
                y,
                f"{item['amount']:,.0f}"
            )


            y -= 18




        # --------------------------------------------------
        # TOTAL
        # --------------------------------------------------


        y -= 10


        pdf.line(
            50,
            y,
            550,
            y
        )


        y -= 25


        for line in [

            f"Subtotal : {subtotal:,.0f} MMK",

            f"Discount : {discount:,.0f} MMK",

            f"Tax Amount : {tax_amount:,.0f} MMK",

            f"Paid : {paid:,.0f} MMK",

            f"Change : {change:,.0f} MMK"

        ]:


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


        result = buffer.getvalue()


        buffer.close()



        return (
            result,
            safe_filename(invoice_no)
        )



    except Exception as e:


        st.error(
            f"PDF Generation Error : {e}"
        )


        return None, None
