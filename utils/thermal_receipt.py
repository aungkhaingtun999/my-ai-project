# ==============================================================================
# utils/thermal_receipt.py
# ERP ENTERPRISE THERMAL RECEIPT ENGINE v5.0
# PART 1/2
# DATA FORMAT + PRINTER CORE
# ==============================================================================


import json
import os
import streamlit as st


# ==============================================================================
# OPTIONAL IMPORTS
# ==============================================================================

try:
    import win32print
    import win32api

except ImportError:

    win32print = None
    win32api = None



try:
    from escpos.printer import Usb, Network

except ImportError:

    Usb = None
    Network = None



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


    default = {

        "shop_name":
            "MY POS SYSTEM",

        "address":
            "Tachileik, Shan State, Myanmar",

        "phone":
            "09-267772367",


        "footer_msg":
            "THANK YOU\nVISIT AGAIN",


        "printer_mode":
            "windows",


        "printer_name":
            "",


        "printer_vendor_id":
            "",


        "printer_product_id":
            "",


        "printer_ip":
            "",


        "printer_port":
            9100
    }



    try:

        if os.path.exists(config_path):

            with open(
                config_path,
                "r",
                encoding="utf-8"
            ) as f:

                user = json.load(f)

                return {
                    **default,
                    **user
                }


    except Exception:

        pass



    return default





# ==============================================================================
# NUMBER SAFE
# ==============================================================================


def num(value):

    try:

        if value is None:

            return 0


        return float(value)


    except Exception:

        return 0





# ==============================================================================
# TEXT FORMAT
# ==============================================================================


def line(
    left="",
    right="",
    width=32
):

    left = str(left)

    right = str(right)


    space = (
        width
        -
        len(left)
        -
        len(right)
    )


    return (
        left
        +
        (" " * max(space,1))
        +
        right
    )





# ==============================================================================
# ITEM NORMALIZER
# ==============================================================================


def normalize_items(items):

    """
    Convert database sale_items
    into thermal printer format

    Input:

    {
      quantity,
      unit_price,
      total,
      product_id
    }


    Output:

    {
      name,
      qty,
      price,
      amount
    }

    """


    result = []


    for item in items or []:


        if not item:

            continue



        product = item.get(
            "products"
        )



        if isinstance(
            product,
            dict
        ):


            name = (
                product.get("name")
                or
                f"Product #{item.get('product_id')}"
            )


        else:


            name = (
                f"Product #{item.get('product_id','')}"
            )



        qty = item.get(
            "quantity",
            item.get(
                "qty",
                0
            )
        )



        price = item.get(
            "unit_price",
            item.get(
                "price",
                0
            )
        )



        amount = item.get(
            "total",
            item.get(
                "amount",
                0
            )
        )



        qty = num(qty)

        price = num(price)

        amount = num(amount)



        if amount == 0:

            amount = qty * price



        result.append(

            {

                "name":
                    name,


                "qty":
                    int(qty),


                "price":
                    price,


                "amount":
                    amount

            }

        )



    return result





# ==============================================================================
# RECEIPT DATA FORMATTER
# ==============================================================================


def prepare_receipt(data):

    """

    Convert POS receipt data
    into printer format

    """


    if not data:

        return {}



    return {


        "shop":

            get_shop_info(),
# ==============================================================================
# THERMAL PRINT ENGINE
# ==============================================================================

def print_thermal(data):

    try:

        if not data:
            st.error("No receipt data")
            return False


        shop = get_shop_info()

        mode = shop.get(
            "printer_mode",
            "windows"
        )


        # =====================================================
        # BUILD RECEIPT TEXT
        # =====================================================

        receipt_text = ""

        receipt_text += (
            shop.get(
                "shop_name",
                "MY POS SYSTEM"
            )
            + "\n"
        )

        receipt_text += (
            shop.get(
                "address",
                ""
            )
            + "\n"
        )

        receipt_text += (
            "Tel : "
            +
            shop.get(
                "phone",
                ""
            )
            +
            "\n"
        )


        receipt_text += "-" * 32 + "\n"


        receipt_text += (
            "Receipt : "
            +
            str(
                data.get(
                    "invoice_no",
                    "-"
                )
            )
            +
            "\n"
        )


        receipt_text += (
            "Date : "
            +
            str(
                data.get(
                    "date",
                    "-"
                )
            )
            +
            "\n"
        )


        receipt_text += (
            "Cashier : "
            +
            str(
                data.get(
                    "cashier",
                    "Admin"
                )
            )
            +
            "\n"
        )


        receipt_text += "-" * 32 + "\n"


        receipt_text += (
            line(
                "Item",
                "Amount",
                32
            )
        )


        items = data.get(
            "items",
            []
        )


        for item in items:

            name = (
                item.get("name")
                or
                f"Product #{item.get('product_id','')}"
            )


            qty = item.get(
                "quantity",
                item.get(
                    "qty",
                    0
                )
            )


            price = num(
                item.get(
                    "unit_price",
                    item.get(
                        "price",
                        0
                    )
                )
            )


            amount = num(
                item.get(
                    "total",
                    qty * price
                )
            )


            receipt_text += (
                f"{name[:16]}\n"
            )

            receipt_text += line(
                f"{qty} x {price:,.0f}",
                f"{amount:,.0f}",
                32
            )


        receipt_text += "-" * 32 + "\n"


        receipt_text += line(
            "Subtotal",
            f"{num(data.get('subtotal')):,.0f}",
            32
        )


        receipt_text += line(
            "Tax",
            f"{num(data.get('tax_amount')):,.0f}",
            32
        )


        receipt_text += line(
            "TOTAL",
            f"{num(data.get('grand_total')):,.0f}",
            32
        )


        receipt_text += line(
            "Paid",
            f"{num(data.get('paid')):,.0f}",
            32
        )


        receipt_text += line(
            "Change",
            f"{num(data.get('change')):,.0f}",
            32
        )


        receipt_text += "-" * 32 + "\n"


        receipt_text += (
            shop.get(
                "footer_msg",
                "THANK YOU"
            )
            +
            "\n"
        )


        # =====================================================
        # WINDOWS PRINTER
        # =====================================================

        if mode == "windows":

            printer_name = shop.get(
                "printer_name"
            )


            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".txt",
                mode="w",
                encoding="utf-8"
            )


            temp_file.write(
                receipt_text
            )

            temp_file.close()


            if win32api:

                win32api.ShellExecute(
                    0,
                    "print",
                    temp_file.name,
                    None,
                    ".",
                    0
                )


            else:

                st.warning(
                    "pywin32 not installed"
                )


            return True



        # =====================================================
        # ESC/POS USB / NETWORK
        # =====================================================

        printer = get_printer()


        if printer:

            printer.text(
                receipt_text
            )


            try:
                printer.cut()
            except Exception:
                pass


            return True



        return False



    except Exception as e:

        st.error(
            f"THERMAL PRINT ERROR: {e}"
        )

        return False
# ==============================================================================
# THERMAL PRINT ENGINE
# ==============================================================================

def print_thermal(data):

    try:

        if not data:
            st.error("No receipt data")
            return False


        shop = get_shop_info()

        mode = shop.get(
            "printer_mode",
            "windows"
        )


        # =====================================================
        # BUILD RECEIPT TEXT
        # =====================================================

        receipt_text = ""

        receipt_text += (
            shop.get(
                "shop_name",
                "MY POS SYSTEM"
            )
            + "\n"
        )

        receipt_text += (
            shop.get(
                "address",
                ""
            )
            + "\n"
        )

        receipt_text += (
            "Tel : "
            +
            shop.get(
                "phone",
                ""
            )
            +
            "\n"
        )


        receipt_text += "-" * 32 + "\n"


        receipt_text += (
            "Receipt : "
            +
            str(
                data.get(
                    "invoice_no",
                    "-"
                )
            )
            +
            "\n"
        )


        receipt_text += (
            "Date : "
            +
            str(
                data.get(
                    "date",
                    "-"
                )
            )
            +
            "\n"
        )


        receipt_text += (
            "Cashier : "
            +
            str(
                data.get(
                    "cashier",
                    "Admin"
                )
            )
            +
            "\n"
        )


        receipt_text += "-" * 32 + "\n"


        receipt_text += (
            line(
                "Item",
                "Amount",
                32
            )
        )


        items = data.get(
            "items",
            []
        )


        for item in items:

            name = (
                item.get("name")
                or
                f"Product #{item.get('product_id','')}"
            )


            qty = item.get(
                "quantity",
                item.get(
                    "qty",
                    0
                )
            )


            price = num(
                item.get(
                    "unit_price",
                    item.get(
                        "price",
                        0
                    )
                )
            )


            amount = num(
                item.get(
                    "total",
                    qty * price
                )
            )


            receipt_text += (
                f"{name[:16]}\n"
            )

            receipt_text += line(
                f"{qty} x {price:,.0f}",
                f"{amount:,.0f}",
                32
            )


        receipt_text += "-" * 32 + "\n"


        receipt_text += line(
            "Subtotal",
            f"{num(data.get('subtotal')):,.0f}",
            32
        )


        receipt_text += line(
            "Tax",
            f"{num(data.get('tax_amount')):,.0f}",
            32
        )


        receipt_text += line(
            "TOTAL",
            f"{num(data.get('grand_total')):,.0f}",
            32
        )


        receipt_text += line(
            "Paid",
            f"{num(data.get('paid')):,.0f}",
            32
        )


        receipt_text += line(
            "Change",
            f"{num(data.get('change')):,.0f}",
            32
        )


        receipt_text += "-" * 32 + "\n"


        receipt_text += (
            shop.get(
                "footer_msg",
                "THANK YOU"
            )
            +
            "\n"
        )


        # =====================================================
        # WINDOWS PRINTER
        # =====================================================

        if mode == "windows":

            printer_name = shop.get(
                "printer_name"
            )


            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".txt",
                mode="w",
                encoding="utf-8"
            )


            temp_file.write(
                receipt_text
            )

            temp_file.close()


            if win32api:

                win32api.ShellExecute(
                    0,
                    "print",
                    temp_file.name,
                    None,
                    ".",
                    0
                )


            else:

                st.warning(
                    "pywin32 not installed"
                )


            return True



        # =====================================================
        # ESC/POS USB / NETWORK
        # =====================================================

        printer = get_printer()


        if printer:

            printer.text(
                receipt_text
            )


            try:
                printer.cut()
            except Exception:
                pass


            return True



        return False



    except Exception as e:

        st.error(
            f"THERMAL PRINT ERROR: {e}"
        )

        return False
        # ==============================================================================
# RECEIPT DATA BUILDER
# ERP ENTERPRISE RECEIPT DATA STANDARD
# ==============================================================================


def build_receipt_data(
    sale,
    items
):
    """
    Convert database sale + sale_items
    into common receipt format

    Used by:
        - receipt_pdf.py
        - thermal_receipt.py
        - printer.py
    """

    try:

        sale = sale or {}
        items = items or []


        clean_items = []


        for item in items:


            if not item:
                continue


            qty = item.get(
                "quantity",
                0
            )


            price = item.get(
                "unit_price",
                0
            )


            total = item.get(
                "total"
            )


            # fallback calculation
            if total is None:

                total = (
                    num(qty)
                    *
                    num(price)
                )


            clean_items.append(

                {

                    "name":
                        (
                            item.get(
                                "name"
                            )
                            or
                            item.get(
                                "product_name"
                            )
                            or
                            f"Product #{item.get('product_id','')}"
                        ),


                    "product_id":
                        item.get(
                            "product_id"
                        ),


                    "quantity":
                        qty,


                    "unit_price":
                        price,


                    "total":
                        total

                }

            )



        return {


            "invoice_no":
                sale.get(
                    "invoice_no",
                    "-"
                ),


            "date":
                sale.get(
                    "created_at",
                    "-"
                ),


            "cashier":
                sale.get(
                    "cashier",
                    "Admin"
                ),


            "items":
                clean_items,


            "subtotal":
                sale.get(
                    "subtotal",
                    0
                ),


            "discount":
                sale.get(
                    "discount",
                    0
                ),


            "tax_amount":
                sale.get(
                    "tax",
                    sale.get(
                        "tax_amount",
                        0
                    )
                ),


            "grand_total":
                sale.get(
                    "total",
                    0
                ),


            "paid":
                sale.get(
                    "paid_amount",
                    0
                ),


            "change":
                sale.get(
                    "change_amount",
                    0
                )

        }


    except Exception as e:

        print(
            "BUILD RECEIPT DATA ERROR:",
            e
        )

        return {}
