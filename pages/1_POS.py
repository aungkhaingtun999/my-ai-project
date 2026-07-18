# ==============================================================================
# 1_POS.py
# ERP ENTERPRISE POS v10.0
# PART 1/3 - CORE + SEARCH + CART ENGINE
# ==============================================================================

import sys
import os
import pandas as pd
from utils.timezone import format_datetime

# Root path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

import streamlit as st

from database import (
    get_products,
    get_setting,
    get_default_warehouse_id,
    checkout_sale_rpc
)

from auth import is_authenticated
from language import t, language_selector


# ------------------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------------------

st.set_page_config(
    page_title="Enterprise POS",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ------------------------------------------------------------------------------
# LANGUAGE
# ------------------------------------------------------------------------------

language_selector()


# ------------------------------------------------------------------------------
# SECURITY CHECK
# ------------------------------------------------------------------------------

if not is_authenticated():
    st.warning("Please login first")
    st.stop()



# ------------------------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------------------------

DEFAULT_STATE = {

    "cart": [],
    "sale_data": None,
    "show_receipt": False,
    "processing": False,

}


for key, value in DEFAULT_STATE.items():

    if key not in st.session_state:
        st.session_state[key] = value



# ------------------------------------------------------------------------------
# TAX SETTINGS
# ------------------------------------------------------------------------------

if "tax_rate" not in st.session_state:

    try:

        st.session_state.tax_rate = float(
            get_setting(
                "default_tax_rate",
                0
            )
        )

    except:

        st.session_state.tax_rate = 0



# ------------------------------------------------------------------------------
# WAREHOUSE
# ------------------------------------------------------------------------------

warehouse_id = get_default_warehouse_id()


if not warehouse_id:

    st.error(
        "Default warehouse not configured"
    )

    st.stop()



# ------------------------------------------------------------------------------
# PRODUCT LOAD
# ------------------------------------------------------------------------------

try:

    products = get_products(
        warehouse_id=warehouse_id
    )

except Exception as e:

    st.error(
        f"Product loading failed: {e}"
    )

    st.stop()



if not products:

    st.warning(
        "No products available"
    )

    st.stop()



# ------------------------------------------------------------------------------
# TITLE
# ------------------------------------------------------------------------------

st.title(
    f"🛒 {t('app.pos_system')}"
)



# ------------------------------------------------------------------------------
# SEARCH ENGINE
# ------------------------------------------------------------------------------

if not st.session_state.show_receipt:


    col1, col2 = st.columns(2)


    with col1:

        name_search = st.text_input(
            "🔎 Product Name"
        )


    with col2:

        barcode_search = st.text_input(
            "📦 SKU / Barcode"
        )



    matches = []


    for product in products:


        name = str(
            product.get(
                "name",
                ""
            )
        )


        sku = str(
            product.get(
                "sku",
                ""
            )
        )


        barcode = str(
            product.get(
                "barcode",
                ""
            )
        )


        name_ok = True
        code_ok = True



        if name_search:

            name_ok = (
                name_search.lower()
                in
                name.lower()
            )



        if barcode_search:


            search = barcode_search.lower()


            code_ok = (

                search in sku.lower()

                or

                search in barcode.lower()

            )



        if name_ok and code_ok:

            matches.append(product)



    # --------------------------------------------------------------------------
    # PRODUCT SELECT
    # --------------------------------------------------------------------------

    if matches:


        selected = st.selectbox(

            "Select Product",

            matches,

            format_func=lambda x:

                f"{x.get('sku','')} | {x.get('name')} | Stock:{x.get('available_qty',x.get('stock',0))}"

        )


        qty = st.number_input(

            "Quantity",

            min_value=1,

            value=1,

            step=1

        )



        if st.button(
            "➕ Add To Cart"
        ):


            available = int(

                selected.get(
                    "available_qty",
                    selected.get(
                        "stock",
                        0
                    )
                )

            )



            existing_qty = sum(

                item["qty"]

                for item in st.session_state.cart

                if item["id"] == selected["id"]

            )



            if existing_qty + qty > available:


                st.error(

                    f"Insufficient stock. Available {available}"

                )


            else:


                found = False



                for item in st.session_state.cart:


                    if item["id"] == selected["id"]:


                        item["qty"] += int(qty)

                        found = True

                        break



                if not found:


                    price = float(

                        selected.get(
                            "selling_price",
                            0
                        )

                    )


                    st.session_state.cart.append(

                        {

                            "id":
                            selected["id"],


                            "name":
                            selected["name"],


                            "sku":
                            selected.get(
                                "sku",
                                ""
                            ),


                            "selling_price":
                            price,


                            "qty":
                            int(qty)

                        }

                    )



                st.success(
                    "Added to cart"
                )

                st.rerun()




# ------------------------------------------------------------------------------
# END PART 1
# ------------------------------------------------------------------------------
# ==============================================================================
# PART 2/3
# CART DISPLAY + CHECKOUT ENGINE
# ==============================================================================


# ------------------------------------------------------------------------------
# CART SECTION
# ------------------------------------------------------------------------------

if (
    not st.session_state.show_receipt
    and st.session_state.cart
):


    st.divider()

    st.subheader(
        "🛒 Shopping Cart"
    )


    cart_rows = []


    for item in st.session_state.cart:


        amount = (
            item["selling_price"]
            *
            item["qty"]
        )


        cart_rows.append(

            {

                "Product":
                item["name"],


                "SKU":
                item.get(
                    "sku",
                    ""
                ),


                "Qty":
                item["qty"],


                "Price":
                f"{item['selling_price']:,.0f} MMK",


                "Amount":
                f"{amount:,.0f} MMK"

            }

        )



    df = pd.DataFrame(
        cart_rows
    )


    st.dataframe(

        df,

        use_container_width=True,

        hide_index=True

    )



    # --------------------------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------------------------


    subtotal = sum(

        item["selling_price"]
        *
        item["qty"]

        for item in st.session_state.cart

    )



    total_qty = sum(

        item["qty"]

        for item in st.session_state.cart

    )



    st.info(

        f"""
        Product Lines : {len(st.session_state.cart)}

        Total Quantity : {total_qty}

        Subtotal : {subtotal:,.0f} MMK
        """

    )



    # --------------------------------------------------------------------------
    # REMOVE ITEM
    # --------------------------------------------------------------------------


    st.subheader(
        "❌ Remove Product"
    )



    for index, item in enumerate(

        st.session_state.cart

    ):


        c1, c2 = st.columns(

            [5,1]

        )


        with c1:

            st.write(

                f"{item['name']} × {item['qty']}"

            )



        with c2:


            if st.button(

                "❌",

                key=f"remove_{index}"

            ):


                st.session_state.cart.pop(

                    index

                )

                st.rerun()



    # --------------------------------------------------------------------------
    # PAYMENT CALCULATION
    # --------------------------------------------------------------------------


    st.divider()


    st.subheader(
        "💰 Payment"
    )



    st.session_state.tax_rate = st.number_input(

        "Tax Rate (%)",

        min_value=0.0,

        value=float(
            st.session_state.tax_rate
        ),

        step=0.5

    )



    discount = st.number_input(

        "Discount",

        min_value=0.0,

        value=0.0,

        step=100.0

    )



    tax_amount = round(

        subtotal
        *
        st.session_state.tax_rate
        /
        100,

        2

    )



    grand_total = (

        subtotal

        +

        tax_amount

        -

        discount

    )



    if grand_total < 0:

        grand_total = 0



    st.success(

        f"""
        Subtotal : {subtotal:,.0f} MMK

        Tax : {tax_amount:,.0f} MMK

        Discount : {discount:,.0f} MMK


        GRAND TOTAL :

        {grand_total:,.0f} MMK
        """

    )



    # --------------------------------------------------------------------------
    # PAYMENT METHOD
    # --------------------------------------------------------------------------


    payment_method = st.selectbox(

        "Payment Method",

        [

            "Cash",

            "Card",

            "Mobile"

        ]

    )



    if payment_method == "Cash":


        received = st.number_input(

            "Received Amount",

            min_value=float(grand_total),

            value=float(grand_total),

            step=100.0

        )


    else:


        received = grand_total



    change = max(

        0,

        received - grand_total

    )



    st.write(

        f"Change : {change:,.0f} MMK"

    )



    # --------------------------------------------------------------------------
    # CHECKOUT
    # --------------------------------------------------------------------------


    if st.button(

        "✅ Confirm Sale",

        disabled=st.session_state.processing,

        use_container_width=True

    ):


        st.session_state.processing = True



        try:



            cart_payload = [

                {

                    "id":
                    item["id"],


                    "qty":
                    int(item["qty"]),


                    "selling_price":
                    float(item["selling_price"])

                }


                for item in st.session_state.cart

            ]



            result = checkout_sale_rpc(

                cart=cart_payload,

                paid_amount=received,

                cashier_id=st.session_state.get(

                    "user_id"

                )

            )



            if result.get(

                "success",

                False

            ):



                data = result.get(

                    "data",

                    {}

                )



                if isinstance(

                    data,

                    list

                ):


                    data = data[0] if data else {}



                invoice_no = (

                    data.get(
                        "invoice_no"
                    )

                    or

                    data.get(
                        "sale_no"
                    )

                    or

                    "INV-"

                    +

                    datetime.now().strftime(

                        "%Y%m%d%H%M%S"

                    )

                )



                st.session_state.sale_data = {


                    "invoice_no":
                    invoice_no,


                    "date": format_datetime(),


                    "cashier":
                    st.session_state.get(

                        "username",

                        "Unknown"

                    ),


                    "items":
                    list(

                        st.session_state.cart

                    ),


                    "subtotal":
                    subtotal,


                    "tax_rate":
                    st.session_state.tax_rate,


                    "tax_amount":
                    tax_amount,


                    "discount":
                    discount,


                    "grand_total":
                    grand_total,


                    "paid":
                    received,


                    "change":
                    change

                }



                st.session_state.show_receipt = True



                st.session_state.processing = False



                st.rerun()



            else:


                st.error(

                    result.get(

                        "message",

                        "Sale failed"

                    )

                )


                st.session_state.processing = False




        except Exception as e:


            st.session_state.processing = False


            st.error(

                f"Checkout Error : {e}"

            )



# ------------------------------------------------------------------------------
# END PART 2
# ------------------------------------------------------------------------------
# ==============================================================================
# PART 3/3
# RECEIPT + PRINT + RESET ENGINE
# ==============================================================================


# ------------------------------------------------------------------------------
# RECEIPT MODULE IMPORT
# ------------------------------------------------------------------------------

try:

    from utils.thermal_receipt import print_thermal

except Exception:

    print_thermal = None



try:

    from utils.receipt_pdf import generate_pdf

except Exception:

    generate_pdf = None




# ------------------------------------------------------------------------------
# RECEIPT PREVIEW
# ------------------------------------------------------------------------------

if st.session_state.show_receipt:


    data = st.session_state.sale_data


    if not data:

        st.error(
            "Receipt data missing"
        )

        st.stop()



    st.divider()


    st.title(
        "🧾 Sales Receipt"
    )



    st.info(

        f"""
        Invoice No : {data['invoice_no']}

        Date : {data['date']}

        Cashier : {data['cashier']}

        """

    )



    st.subheader(
        "Items"
    )



    receipt_rows = []



    for item in data["items"]:


        amount = (

            item["selling_price"]

            *

            item["qty"]

        )



        receipt_rows.append(

            {

                "Product":
                item["name"],


                "Qty":
                item["qty"],


                "Price":
                f"{item['selling_price']:,.0f}",


                "Amount":
                f"{amount:,.0f} MMK"

            }

        )



    receipt_df = pd.DataFrame(

        receipt_rows

    )


    st.dataframe(

        receipt_df,

        use_container_width=True,

        hide_index=True

    )



    st.divider()



    st.write(

        f"""
### Payment Summary


Subtotal :

**{data['subtotal']:,.0f} MMK**


Tax ({data['tax_rate']}%) :

**{data['tax_amount']:,.0f} MMK**


Discount :

**{data['discount']:,.0f} MMK**



# GRAND TOTAL

## {data['grand_total']:,.0f} MMK



Paid :

{data['paid']:,.0f} MMK



Change :

{data['change']:,.0f} MMK

"""

    )



    st.divider()



    # --------------------------------------------------------------------------
    # ACTION BUTTONS
    # --------------------------------------------------------------------------


    c1, c2, c3 = st.columns(3)



    # --------------------------------------------------------------------------
    # THERMAL PRINT
    # --------------------------------------------------------------------------


    with c1:


        if st.button(

            "🖨 Print Receipt",

            use_container_width=True

        ):


            if print_thermal:


                try:


                    print_thermal(

                        data

                    )


                    st.success(

                        "Printed successfully"

                    )


                except Exception as e:


                    st.error(

                        f"Printer Error : {e}"

                    )


            else:


                st.warning(

                    "Thermal printer module not installed"

                )



    # --------------------------------------------------------------------------
    # PDF RECEIPT
    # --------------------------------------------------------------------------


    with c2:


        if st.button(

            "📄 Generate PDF",

            use_container_width=True

        ):


            if generate_pdf:


                try:


                    file = generate_pdf(

                        data

                    )


                    st.success(

                        "PDF Generated"

                    )


                except Exception as e:


                    st.error(

                        f"PDF Error : {e}"

                    )


            else:


                st.warning(

                    "PDF module missing"

                )



    # --------------------------------------------------------------------------
    # NEW SALE
    # --------------------------------------------------------------------------


    with c3:


        if st.button(

            "🆕 New Sale",

            use_container_width=True

        ):



            st.session_state.cart = []


            st.session_state.sale_data = None


            st.session_state.show_receipt = False


            st.session_state.processing = False



            try:


                st.session_state.tax_rate = float(

                    get_setting(

                        "default_tax_rate",

                        0

                    )

                )


            except:


                st.session_state.tax_rate = 0



            st.rerun()



# ==============================================================================
# END ERP ENTERPRISE POS v10.0
# ==============================================================================
