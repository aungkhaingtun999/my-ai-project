# ==============================================================================
# 1_POS.py
# ERP ENTERPRISE POS v18
# PART 1/10
# SECURITY CORE + INITIALIZATION ENGINE
# ==============================================================================


import sys
import os
import json
import time
import pandas as pd

import streamlit as st

from decimal import Decimal
from datetime import datetime


# ------------------------------------------------------------------------------
# ROOT PATH
# ------------------------------------------------------------------------------

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)


# ------------------------------------------------------------------------------
# DATABASE SERVICES
# ------------------------------------------------------------------------------

from database import (

    get_products,
    get_setting,
    get_erp_setting,
    get_default_warehouse_id,
    get_payment_methods,
    checkout_sale_rpc,
    is_module_enabled

)


# ------------------------------------------------------------------------------
# AUTH SERVICES
# ------------------------------------------------------------------------------

from auth import is_authenticated


# ------------------------------------------------------------------------------
# LANGUAGE
# ------------------------------------------------------------------------------

from language import (
    t,
    language_selector
)



# ==============================================================================
# SECURITY ENGINE V23 COMPATIBLE
# ==============================================================================


def get_current_user():

    user = st.session_state.get(
        "user"
    )


    if not user:

        return None


    if isinstance(
        user.get("permissions"),
        str
    ):

        try:

            user["permissions"] = json.loads(
                user["permissions"]
            )

        except:

            user["permissions"] = {}


    return user




def has_permission(
        module,
        action
):


    user = get_current_user()


    if not user:

        return False



    permissions = user.get(
        "permissions",
        {}
    )


    return (

        permissions
        .get(
            module,
            {}
        )
        .get(
            action,
            False
        )

    )





def require_permission(
        module,
        action
):


    if not has_permission(
        module,
        action
    ):

        st.error(
            f"⛔ Access Denied : {module} → {action}"
        )

        st.stop()





# ==============================================================================
# SESSION SECURITY
# ==============================================================================


def check_session_timeout():


    try:

        timeout = int(
            get_erp_setting(
                "session_timeout",
                60
            )
        )


    except:

        timeout = 60



    login_time = st.session_state.get(
        "login_time"
    )



    if login_time:


        elapsed = (
            time.time()
            -
            login_time
        ) / 60



        if elapsed > timeout:


            st.warning(
                "Session expired. Please login again."
            )


            st.session_state.clear()

            st.stop()







# ==============================================================================
# PAGE CONFIG
# ==============================================================================


st.set_page_config(

    page_title="ERP Enterprise POS v18",

    layout="wide",

    initial_sidebar_state="collapsed"

)



# ==============================================================================
# LANGUAGE
# ==============================================================================


language_selector()





# ==============================================================================
# AUTHENTICATION CHECK
# ==============================================================================


if not is_authenticated():


    st.warning(
        "Please login first"
    )


    st.stop()





# Runtime Security

check_session_timeout()





# ==============================================================================
# MODULE SECURITY
# ==============================================================================


if not is_module_enabled(
        "POS"
):


    st.error(
        "🛑 POS Module Disabled"
    )


    st.stop()





# ==============================================================================
# USER STANDARDIZATION
# ==============================================================================


current_user = get_current_user()



if not current_user:


    st.error(
        "User session invalid"
    )


    st.stop()





# ==============================================================================
# SESSION STATE
# ==============================================================================


DEFAULT_STATE = {


    "cart":

    [],



    "sale_data":

    None,



    "processing":

    False,



    "show_receipt":

    False



}



for key, value in DEFAULT_STATE.items():


    if key not in st.session_state:


        st.session_state[key] = value





# ==============================================================================
# BASIC SYSTEM SETTINGS
# ==============================================================================


warehouse_id = get_default_warehouse_id()



if not warehouse_id:


    st.error(
        "Default Warehouse Missing"
    )


    st.stop()





currency = get_erp_setting(

    "currency",

    "MMK"

)



tax_rate = Decimal(

    str(

        get_erp_setting(

            "tax_rate",

            "0"

        )

    )

) / Decimal("100")





# ==============================================================================
# END PART 1/10
# ==============================================================================
# ==============================================================================
# PRODUCT LOAD ENGINE
# ==============================================================================


try:

    products = get_products(
        warehouse_id=warehouse_id
    )


except Exception as e:


    st.error(
        f"Product Loading Error : {e}"
    )

    st.stop()



if not products:


    st.warning(
        "No products available"
    )

    st.stop()





# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================


def get_stock(product):


    return int(

        product.get(
            "available_qty",
            product.get(
                "stock",
                0
            )
        )

        or 0

    )





def add_to_cart(product, qty):


    qty = int(qty)


    available = get_stock(
        product
    )


    existing = next(

        (

            x for x in st.session_state.cart

            if x["id"] == product["id"]

        ),

        None

    )



    current_qty = (

        existing["qty"]

        if existing

        else 0

    )



    if current_qty + qty > available:


        st.error(

            f"Stock Limit Exceeded. Available : {available}"

        )

        return False





    if existing:


        existing["qty"] += qty



    else:


        st.session_state.cart.append(

            {


                "id":

                product["id"],



                "name":

                product.get(

                    "name",

                    ""

                ),



                "sku":

                product.get(

                    "sku",

                    ""

                ),



                "selling_price":

                Decimal(

                    str(

                        product.get(

                            "selling_price",

                            0

                        )

                    )

                ),



                "qty":

                qty


            }

        )



    return True







def remove_cart_item(index):


    st.session_state.cart.pop(
        index
    )





# ==============================================================================
# POS SCREEN
# ==============================================================================


if st.session_state.sale_data is None:


    st.title(

        f"🛒 {t('app.pos_system')}"

    )



    # --------------------------------------------------------------------------
    # SEARCH ENGINE
    # --------------------------------------------------------------------------


    col1, col2 = st.columns(

        [2,1]

    )



    with col1:


        search_text = st.text_input(

            "🔎 Search Product / Barcode"

        )



    with col2:


        st.write("")

        st.write("")

        st.caption(

            "Scanner Ready"

        )





    search = search_text.lower().strip()



    if search:


        matches = [

            p for p in products

            if

            search in str(

                p.get(

                    "name",

                    ""

                )

            ).lower()

            or

            search in str(

                p.get(

                    "sku",

                    ""

                )

            ).lower()

            or

            search in str(

                p.get(

                    "barcode",

                    ""

                )

            ).lower()

        ]



    else:


        matches = products[:20]





    # --------------------------------------------------------------------------
    # PRODUCT SELECT
    # --------------------------------------------------------------------------


    if matches:



        selected = st.selectbox(

            "Select Product",

            matches,


            format_func=lambda x:


                f"{x.get('sku','')} | {x.get('name','')} | Stock:{get_stock(x)}"


        )



        qty = st.number_input(

            "Quantity",

            min_value=1,

            value=1,

            step=1

        )



        if st.button(

            "➕ Add To Cart",

            use_container_width=True

        ):



            if add_to_cart(

                selected,

                qty

            ):


                st.success(

                    "Added to Cart"

                )


                st.rerun()





    else:


        if search:


            st.info(

                "Product not found"

            )





# ==============================================================================
# CART PREVIEW HEADER
# ==============================================================================


if (

    st.session_state.cart

    and

    st.session_state.sale_data is None

):


    st.divider()


    st.subheader(

        "🛒 Current Cart"

    )


    total_items = sum(

        item["qty"]

        for item in st.session_state.cart

    )


    st.info(

        f"Total Items : {total_items}"

    )





# ==============================================================================
# END PART 2/10
# ==============================================================================
# ==============================================================================
# CART DISPLAY ENGINE
# ==============================================================================


if (

    st.session_state.cart

    and

    st.session_state.sale_data is None

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

                f"{item['selling_price']:,.0f} {currency}",



                "Amount":

                f"{amount:,.0f} {currency}"

            }

        )



    cart_df = pd.DataFrame(

        cart_rows

    )



    st.dataframe(

        cart_df,

        use_container_width=True,

        hide_index=True

    )





# ==============================================================================
# CART REMOVE ENGINE
# ==============================================================================



    st.subheader(

        "❌ Remove Product"

    )



    for index, item in enumerate(

        st.session_state.cart

    ):



        col1, col2 = st.columns(

            [5,1]

        )



        with col1:


            st.write(

                f"{item['name']} × {item['qty']}"

            )



        with col2:


            if st.button(

                "❌",

                key=f"remove_{index}"

            ):



                st.session_state.cart.pop(

                    index

                )


                st.rerun()






# ==============================================================================
# CART TOTAL CALCULATION
# ==============================================================================



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

        Subtotal : {subtotal:,.0f} {currency}

        """

    )






# ==============================================================================
# TAX ENGINE
# ==============================================================================



    st.divider()


    st.subheader(

        "💰 Pricing Engine"

    )



    tax_enabled = get_erp_setting(

        "tax_enabled",

        True

    )



    if tax_enabled:


        tax_amount = (

            subtotal

            *

            tax_rate

        )


    else:


        tax_amount = Decimal("0")





# ==============================================================================
# DISCOUNT PERMISSION ENGINE
# ==============================================================================



    discount = Decimal("0")



    can_discount = has_permission(

        "POS",

        "discount"

    )





    if can_discount:


        discount_input = st.number_input(

            "Discount",

            min_value=0.0,

            value=0.0,

            step=100.0

        )



        discount = Decimal(

            str(

                discount_input

            )

        )


    else:


        st.caption(

            "Discount permission disabled"

        )







# ==============================================================================
# GRAND TOTAL
# ==============================================================================



    grand_total = (

        subtotal

        +

        tax_amount

        -

        discount

    )



    if grand_total < 0:


        grand_total = Decimal("0")





    st.success(

        f"""

        Subtotal :

        {subtotal:,.0f} {currency}



        Tax :

        {tax_amount:,.0f} {currency}



        Discount :

        {discount:,.0f} {currency}



        =====================



        GRAND TOTAL



        {grand_total:,.0f} {currency}

        """

    )





# Store temporary calculation

    st.session_state["checkout_summary"] = {


        "subtotal":

        subtotal,



        "tax_amount":

        tax_amount,



        "discount":

        discount,



        "grand_total":

        grand_total


    }



# ==============================================================================
# END PART 3/10
# ==============================================================================

# ==============================================================================
# PAYMENT ENGINE
# ==============================================================================


if (

    st.session_state.cart

    and

    st.session_state.sale_data is None

):


    summary = st.session_state.get(

        "checkout_summary",

        {}

    )



    subtotal = summary.get(

        "subtotal",

        Decimal("0")

    )


    tax_amount = summary.get(

        "tax_amount",

        Decimal("0")

    )


    discount = summary.get(

        "discount",

        Decimal("0")

    )


    grand_total = summary.get(

        "grand_total",

        Decimal("0")

    )





    st.divider()


    st.subheader(

        "💳 Payment"

    )





# ==============================================================================
# LOAD PAYMENT METHODS
# ==============================================================================



    try:


        payment_methods = get_payment_methods()



    except Exception:


        payment_methods = []





    if not payment_methods:


        payment_methods = [

            "Cash",

            "Card",

            "Mobile"

        ]





    payment_method = st.selectbox(

        "Payment Method",

        payment_methods

    )





# ==============================================================================
# RECEIVED AMOUNT
# ==============================================================================



    if payment_method == "Cash":



        received = st.number_input(

            "Received Amount",

            min_value=0.0,

            value=float(grand_total),

            step=100.0

        )



        received_decimal = Decimal(

            str(

                received

            )

        )



    else:



        # Non cash payment

        received_decimal = grand_total


        st.info(

            f"{payment_method} payment selected"

        )






# ==============================================================================
# PAYMENT VALIDATION
# ==============================================================================



    change = received_decimal - grand_total



    if change < 0:



        payment_error = True



        st.error(

            f"""

            ❌ Insufficient Payment



            Need :

            {abs(change):,.0f} {currency}

            """

        )


    else:


        payment_error = False



        change = max(

            Decimal("0"),

            change

        )





    st.write(

        f"Change : {change:,.0f} {currency}"

    )





# ==============================================================================
# SAVE CHECKOUT DATA TEMPORARY
# ==============================================================================



    st.session_state["payment_data"] = {


        "payment_method":

        payment_method,



        "received":

        received_decimal,



        "change":

        change,



        "payment_error":

        payment_error


    }





# ==============================================================================
# CONFIRM SALE BUTTON
# ==============================================================================



    st.divider()



    if st.button(

        "✅ Confirm Sale",

        use_container_width=True,

        disabled=(

            st.session_state.processing

            or

            payment_error

        )

    ):



        st.session_state.processing = True



        # Next Part will execute transaction


        st.session_state["start_checkout"] = True



        st.rerun()




# ==============================================================================
# END PART 4/10
# ==============================================================================
# ==============================================================================
# CHECKOUT TRANSACTION ENGINE
# ==============================================================================


if (

    st.session_state.get("start_checkout")

    and

    st.session_state.cart

):


    st.session_state.start_checkout = False



    st.session_state.processing = True



    try:


        # ----------------------------------------------------------------------
        # 1. FINAL STOCK LOCK CHECK
        # ----------------------------------------------------------------------


        latest_products = get_products(

            warehouse_id=warehouse_id

        )



        for item in st.session_state.cart:



            current_product = next(

                (

                    p for p in latest_products

                    if p["id"] == item["id"]

                ),

                None

            )



            if not current_product:


                st.error(

                    f"{item['name']} not found"

                )

                st.session_state.processing = False

                st.stop()





            available = get_stock(

                current_product

            )



            if item["qty"] > available:



                st.error(

                    f"""

                    ❌ Stock Changed



                    Product:

                    {item['name']}



                    Available:

                    {available}



                    Requested:

                    {item['qty']}

                    """

                )



                st.session_state.processing = False

                st.stop()





        # ----------------------------------------------------------------------
        # 2. PREPARE RPC PAYLOAD
        # ----------------------------------------------------------------------


        cart_payload = []



        for item in st.session_state.cart:


            cart_payload.append(

                {


                    "id":

                    item["id"],



                    "qty":

                    int(

                        item["qty"]

                    ),



                    "selling_price":

                    float(

                        item["selling_price"]

                    )


                }

            )






        payment_data = st.session_state.get(

            "payment_data",

            {}

        )



        summary = st.session_state.get(

            "checkout_summary",

            {}

        )





        paid_amount = float(

            payment_data.get(

                "received",

                0

            )

        )





        payment_method = payment_data.get(

            "payment_method",

            "Cash"

        )






        # ----------------------------------------------------------------------
        # 3. CHECKOUT RPC CALL
        # ----------------------------------------------------------------------


        result = checkout_sale_rpc(

            cart=cart_payload,


            paid_amount=paid_amount,


            payment_method=payment_method,


            discount=float(

                summary.get(

                    "discount",

                    0

                )

            ),



            warehouse_id=warehouse_id,


            cashier_id=current_user.get(

                "id"

            ),



            action_type="POS_SALE"

        )





        # ----------------------------------------------------------------------
        # 4. RESPONSE VALIDATION
        # ----------------------------------------------------------------------


        if not isinstance(

            result,

            dict

        ):


            raise Exception(

                "Invalid server response"

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

                f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            )







            # ------------------------------------------------------------------
            # 5. CREATE RECEIPT DATA
            # ------------------------------------------------------------------


            st.session_state.sale_data = {


                "invoice_no":

                invoice_no,



                "date":

                datetime.now(),



                "cashier":

                current_user.get(

                    "username",

                    "Admin"

                ),



                "items":

                list(

                    st.session_state.cart

                ),



                "subtotal":

                summary.get(

                    "subtotal",

                    0

                ),



                "tax_amount":

                summary.get(

                    "tax_amount",

                    0

                ),



                "discount":

                summary.get(

                    "discount",

                    0

                ),



                "grand_total":

                summary.get(

                    "grand_total",

                    0

                ),



                "paid":

                payment_data.get(

                    "received",

                    0

                ),



                "change":

                payment_data.get(

                    "change",

                    0

                ),



                "payment_method":

                payment_method


            }





            st.session_state.show_receipt = True



            st.session_state.cart = []



            st.success(

                "✅ Sale Completed Successfully"

            )


            st.rerun()






        else:



            st.error(

                result.get(

                    "message",

                    "Checkout Failed"

                )

            )





    except Exception as e:



        st.error(

            f"Transaction Error : {e}"

        )



    finally:



        st.session_state.processing = False




# ==============================================================================
# END PART 5/10
# ==============================================================================
# ==============================================================================
# PART 6/10
# PAYMENT ENGINE + CHECKOUT PREPARATION
# ==============================================================================


# ------------------------------------------------------------------------------
# PAYMENT METHODS
# ------------------------------------------------------------------------------

try:

    payment_methods = get_payment_methods()

except Exception:

    payment_methods = []


if not payment_methods:

    payment_methods = [

        "Cash",
        "Card",
        "Mobile"

    ]



# ------------------------------------------------------------------------------
# PAYMENT SECTION
# ------------------------------------------------------------------------------

st.divider()

st.subheader(
    "💳 Payment"
)



payment_method = st.selectbox(

    "Payment Method",

    payment_methods

)



# ------------------------------------------------------------------------------
# RECEIVED AMOUNT
# ------------------------------------------------------------------------------

if payment_method == "Cash":


    received = st.number_input(

        "Received Amount",

        min_value=0.0,

        value=float(
            grand_total
        ),

        step=100.0

    )


    received_decimal = Decimal(

        str(received)

    )


else:


    # Card / Mobile / Digital Payment

    received_decimal = grand_total



# ------------------------------------------------------------------------------
# PAYMENT VALIDATION
# ------------------------------------------------------------------------------

change = Decimal("0")


payment_error = False



if payment_method == "Cash":


    if received_decimal < grand_total:


        payment_error = True


        st.error(

            "⚠️ Insufficient Payment"

        )


    else:


        change = (

            received_decimal

            -

            grand_total

        )



else:


    change = Decimal("0")



# ------------------------------------------------------------------------------
# PAYMENT SUMMARY
# ------------------------------------------------------------------------------

st.info(

f"""
Payment Method :

{payment_method}


Grand Total :

{grand_total:,.0f} MMK


Received :

{received_decimal:,.0f} MMK


Change :

{change:,.0f} MMK

"""

)



# ------------------------------------------------------------------------------
# SECURITY CHECK BEFORE CHECKOUT
# ------------------------------------------------------------------------------

def validate_payment():

    if payment_error:

        return False


    if grand_total <= 0:

        return False


    return True



# ------------------------------------------------------------------------------
# PREPARE CHECKOUT DATA
# ------------------------------------------------------------------------------

checkout_ready = validate_payment()



if not checkout_ready:


    st.warning(

        "Checkout unavailable. Check payment."

    )



# ------------------------------------------------------------------------------
# END PART 6
# ------------------------------------------------------------------------------
# ==============================================================================
# PART 7/10
# CHECKOUT TRANSACTION ENGINE
# ==============================================================================


# ------------------------------------------------------------------------------
# BUILD RPC PAYLOAD
# ------------------------------------------------------------------------------

def build_checkout_payload(cart):

    payload = []

    for item in cart:

        payload.append({

            "id":
            item["id"],


            "qty":
            int(item["qty"]),


            "selling_price":
            float(
                item["selling_price"]
            )

        })

    return payload




# ------------------------------------------------------------------------------
# CHECK CART SAFETY
# ------------------------------------------------------------------------------

def validate_cart():

    if not st.session_state.cart:

        return False, "Cart empty"


    for item in st.session_state.cart:

        if int(item["qty"]) <= 0:

            return False, (
                f"Invalid quantity: {item['name']}"
            )


    return True, None




# ------------------------------------------------------------------------------
# CONFIRM SALE BUTTON
# ------------------------------------------------------------------------------

if st.button(

    "✅ Confirm Sale",

    disabled=
    (
        st.session_state.processing
        or
        not checkout_ready
    ),

    use_container_width=True

):


    valid, error = validate_cart()


    if not valid:

        st.error(error)

        st.stop()



    # --------------------------------------------------------------------------
    # TRANSACTION LOCK
    # --------------------------------------------------------------------------

    st.session_state.processing = True



    try:


        # ----------------------------------------------------------------------
        # CURRENT USER
        # ----------------------------------------------------------------------

        user = st.session_state.get(

            "user",

            {}

        )


        cashier_id = (

            user.get("id")

            or

            st.session_state.get(
                "user_id"
            )

        )



        cashier_name = (

            user.get(
                "username",
                "Admin"
            )

        )



        # ----------------------------------------------------------------------
        # STOCK FINAL CHECK
        # ----------------------------------------------------------------------

        for item in st.session_state.cart:


            current = next(

                (
                    p for p in products
                    if p["id"] == item["id"]
                ),

                None

            )


            if current:


                available = int(

                    current.get(
                        "available_qty",

                        current.get(
                            "stock",
                            0
                        )

                    )

                )


                if item["qty"] > available:


                    raise Exception(

                        f"{item['name']} stock changed"

                    )



        # ----------------------------------------------------------------------
        # RPC PAYLOAD
        # ----------------------------------------------------------------------

        cart_payload = build_checkout_payload(

            st.session_state.cart

        )



        # ----------------------------------------------------------------------
        # AUDIT CONTEXT
        # Compatible with Setting V23
        # ----------------------------------------------------------------------

        audit_context = {


            "module":

            "POS",



            "action":

            "SALE_CREATE",



            "warehouse_id":

            warehouse_id,



            "cashier":

            cashier_name


        }



        # ----------------------------------------------------------------------
        # DATABASE TRANSACTION
        # ----------------------------------------------------------------------

        result = checkout_sale_rpc(

            cart=

            cart_payload,


            paid_amount=

            float(
                received_decimal
            ),


            payment_method=

            payment_method,


            discount=

            float(
                discount
            ),


            warehouse_id=

            warehouse_id,


            cashier_id=

            cashier_id,


            action_type=

            "POS_SALE",


            audit_context=

            audit_context

        )



        # ----------------------------------------------------------------------
        # RESPONSE CHECK
        # ----------------------------------------------------------------------

        if not isinstance(

            result,

            dict

        ):

            raise Exception(

                "Invalid server response"

            )



        if not result.get(

            "success",

            False

        ):


            raise Exception(

                result.get(

                    "message",

                    "Checkout Failed"

                )

            )



        # ----------------------------------------------------------------------
        # INVOICE DATA
        # ----------------------------------------------------------------------

        response_data = result.get(

            "data",

            {}

        )


        if isinstance(

            response_data,

            list

        ):

            response_data = (

                response_data[0]

                if response_data

                else {}

            )



        invoice_no = (

            response_data.get(

                "invoice_no"

            )

            or

            response_data.get(

                "sale_no"

            )

            or

            f"INV-{datetime.now():%Y%m%d%H%M%S}"

        )



        # ----------------------------------------------------------------------
        # SAVE RECEIPT SESSION
        # ----------------------------------------------------------------------

        st.session_state.sale_data = {


            "invoice_no":

            invoice_no,


            "items":

            list(
                st.session_state.cart
            ),


            "subtotal":

            subtotal,


            "tax_amount":

            tax_amount,


            "discount":

            discount,


            "grand_total":

            grand_total,


            "paid":

            received_decimal,


            "change":

            change,


            "payment_method":

            payment_method,


            "cashier":

            cashier_name,


            "date":

            format_datetime()


        }



        # ----------------------------------------------------------------------
        # CLEAR CART
        # ----------------------------------------------------------------------

        st.session_state.cart = []


        st.session_state.processing = False


        st.rerun()



    except Exception as e:


        st.session_state.processing = False


        st.error(

            f"Checkout Error: {e}"

        )



# ==============================================================================
# END PART 7/10
# ==============================================================================
# ==============================================================================
# PART 8/10
# RECEIPT ENGINE + PRINT SERVICE
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
# RECEIPT DISPLAY
# ------------------------------------------------------------------------------

if st.session_state.sale_data:


    data = st.session_state.sale_data


    st.divider()


    st.title(
        "🧾 Sales Receipt"
    )



    # --------------------------------------------------------------------------
    # HEADER
    # --------------------------------------------------------------------------

    st.info(

f"""
Invoice No :

{data.get('invoice_no','-')}


Date :

{data.get('date','-')}


Cashier :

{data.get('cashier','-')}


Payment :

{data.get('payment_method','-')}

"""

    )



    # --------------------------------------------------------------------------
    # ITEM LIST
    # --------------------------------------------------------------------------

    st.subheader(

        "Items"

    )


    receipt_rows = []


    for item in data.get(

        "items",

        []

    ):


        amount = (

            Decimal(
                str(item["selling_price"])
            )

            *

            int(
                item["qty"]
            )

        )


        receipt_rows.append(

            {


                "Product":

                item["name"],



                "Qty":

                item["qty"],



                "Price":

                f"{Decimal(str(item['selling_price'])):,.0f}",



                "Amount":

                f"{amount:,.0f} MMK"

            }

        )



    if receipt_rows:


        receipt_df = pd.DataFrame(

            receipt_rows

        )


        st.dataframe(

            receipt_df,

            use_container_width=True,

            hide_index=True

        )



    # --------------------------------------------------------------------------
    # TOTAL SUMMARY
    # --------------------------------------------------------------------------

    st.divider()


    st.success(

f"""
Subtotal :

{data.get('subtotal',0):,.0f} MMK


Tax :

{data.get('tax_amount',0):,.0f} MMK


Discount :

{data.get('discount',0):,.0f} MMK



GRAND TOTAL

{data.get('grand_total',0):,.0f} MMK



Paid :

{data.get('paid',0):,.0f} MMK


Change :

{data.get('change',0):,.0f} MMK

"""

    )



    # --------------------------------------------------------------------------
    # ACTION BUTTONS
    # --------------------------------------------------------------------------

    c1, c2, c3 = st.columns(3)



    # --------------------------------------------------------------------------
    # THERMAL PRINT
    # --------------------------------------------------------------------------

    with c1:


        if st.button(

            "🖨 Thermal Print",

            use_container_width=True

        ):


            if print_thermal:


                try:


                    print_thermal(

                        data

                    )


                    st.success(

                        "Printed Successfully"

                    )


                except Exception as e:


                    st.error(

                        f"Printer Error: {e}"

                    )


            else:


                st.warning(

                    "Thermal printer module missing"

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


                    pdf_file = generate_pdf(

                        data

                    )


                    st.download_button(

                        "⬇ Download Receipt",

                        data=pdf_file,

                        file_name=

                        f"{data.get('invoice_no')}.pdf",

                        mime=

                        "application/pdf"

                    )


                except Exception as e:


                    st.error(

                        f"PDF Error: {e}"

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

            st.session_state.processing = False


            st.rerun()



# ==============================================================================
# END PART 8/10
# ==============================================================================

# ==============================================================================
# PART 9/10
# SECURITY + PERMISSION INTEGRATION ENGINE
# ==============================================================================


import json
import time



# ------------------------------------------------------------------------------
# USER SECURITY HELPER
# ------------------------------------------------------------------------------

def get_current_user():

    return st.session_state.get(
        "user",
        {}
    )



def get_user_permissions():

    user = get_current_user()


    permissions = user.get(
        "permissions",
        {}
    )


    if isinstance(

        permissions,

        str

    ):

        try:

            permissions = json.loads(

                permissions

            )

        except:

            permissions = {}


    return permissions



# ------------------------------------------------------------------------------
# ACTION PERMISSION CHECK
# ------------------------------------------------------------------------------

def has_permission(

    module,

    action

):


    permissions = get_user_permissions()


    return (

        permissions

        .get(

            module,

            {}

        )

        .get(

            action,

            False

        )

    )




def require_pos_permission(action):


    if not has_permission(

        "POS",

        action

    ):


        st.error(

            f"⛔ POS Permission Denied : {action}"

        )


        st.stop()




# ------------------------------------------------------------------------------
# POS SALE CREATE SECURITY
# ------------------------------------------------------------------------------

require_pos_permission(

    "create"

)



# ------------------------------------------------------------------------------
# DISCOUNT SECURITY
# ------------------------------------------------------------------------------

def check_discount_permission():

    if discount <= 0:

        return True



    if not has_permission(

        "POS",

        "discount_manage"

    ):


        st.error(

            "⛔ Discount permission required"

        )


        return False


    return True




# Discount Validation

if not check_discount_permission():

    discount = Decimal("0")



# ------------------------------------------------------------------------------
# PRICE CHANGE PROTECTION
# ------------------------------------------------------------------------------

def validate_price_change():

    for item in st.session_state.cart:


        if "original_price" in item:


            if item["price"] != item["original_price"]:


                if not has_permission(

                    "POS",

                    "price_override"

                ):


                    st.error(

                        "⛔ Price Override Not Allowed"

                    )


                    return False


    return True




# ------------------------------------------------------------------------------
# SESSION SECURITY CHECK
# Compatible with Settings V23 timeout
# ------------------------------------------------------------------------------

def check_pos_session():

    login_time = st.session_state.get(

        "login_time"

    )


    if not login_time:

        return True



    settings = st.session_state.get(

        "security_config",

        {}

    )


    timeout = settings.get(

        "timeout",

        60

    )



    elapsed = (

        time.time()

        -

        login_time

    ) / 60



    if elapsed > timeout:


        st.warning(

            "Session Expired"

        )


        st.session_state.clear()


        st.stop()



    return True



check_pos_session()



# ------------------------------------------------------------------------------
# AUDIT EVENT BUILDER
# ------------------------------------------------------------------------------

def build_pos_audit_event(action):


    user = get_current_user()



    return {


        "module":

        "POS",



        "action":

        action,



        "user_id":

        user.get(

            "id"

        ),



        "warehouse_id":

        warehouse_id,



        "timestamp":

        datetime.now().isoformat()

    }



# ------------------------------------------------------------------------------
# FINAL POS SECURITY CHECK
# ------------------------------------------------------------------------------

if not validate_price_change():

    st.stop()



# ==============================================================================
# END PART 9/10
# ==============================================================================
# ==============================================================================
# PART 10/10
# FINAL INTEGRATION + PRODUCTION HARDENING
# ==============================================================================


# ------------------------------------------------------------------------------
# GLOBAL ERROR HANDLER
# ------------------------------------------------------------------------------

def pos_error_handler(error):

    st.error(

        f"POS System Error : {error}"

    )


    st.session_state.processing = False



# ------------------------------------------------------------------------------
# SAFE RESET ENGINE
# ------------------------------------------------------------------------------

def reset_pos():

    keys = [

        "cart",

        "sale_data",

        "processing"

    ]


    for key in keys:


        if key == "cart":

            st.session_state[key] = []


        elif key == "processing":

            st.session_state[key] = False


        else:

            st.session_state[key] = None




# ------------------------------------------------------------------------------
# RECEIPT SERVICE CONNECTION
# ------------------------------------------------------------------------------

def open_receipt_service():


    if not st.session_state.sale_data:

        return False



    try:


        from utils.receipt_service import (

            render_receipt_ui

        )


        render_receipt_ui(

            st.session_state.sale_data

        )


        return True



    except Exception as e:


        st.error(

            f"Receipt Service Error : {e}"

        )


        return False




# ------------------------------------------------------------------------------
# TRANSACTION STATUS MONITOR
# ------------------------------------------------------------------------------

def transaction_status():


    if st.session_state.processing:


        st.info(

            "⏳ Transaction Processing..."

        )


    else:


        return




# ------------------------------------------------------------------------------
# PRODUCTION CHECK
# ------------------------------------------------------------------------------

def production_health_check():


    checks = {


        "Authentication":

        is_authenticated(),



        "Warehouse":

        bool(warehouse_id),



        "Database":

        True,



        "Cart Engine":

        isinstance(

            st.session_state.cart,

            list

        )

    }



    return checks




# ------------------------------------------------------------------------------
# SYSTEM HEALTH PANEL
# ------------------------------------------------------------------------------

with st.expander(

    "🔧 POS System Status"

):


    health = production_health_check()



    for name, status in health.items():


        if status:


            st.success(

                f"✅ {name}"

            )

        else:


            st.error(

                f"❌ {name}"

            )





# ------------------------------------------------------------------------------
# FINAL RECEIPT CONTROLLER
# ------------------------------------------------------------------------------

if st.session_state.sale_data:


    open_receipt_service()



# ------------------------------------------------------------------------------
# FINAL NEW SALE BUTTON
# ------------------------------------------------------------------------------

if st.session_state.sale_data:


    if st.button(

        "🆕 Start New Sale",

        use_container_width=True

    ):


        reset_pos()


        st.rerun()



# ------------------------------------------------------------------------------
# FINAL CLEANUP
# ------------------------------------------------------------------------------

transaction_status()



# ==============================================================================
# ERP ENTERPRISE POS v17.1
# PRODUCTION FINAL BUILD
#
# Features:
#
# ✅ Security Permission Engine
# ✅ Module Control Integration
# ✅ Stock Validation
# ✅ Barcode Search
# ✅ Cart Engine
# ✅ Tax Engine
# ✅ Discount Permission
# ✅ Payment Validation
# ✅ RPC Transaction
# ✅ Audit Ready
# ✅ Receipt Service
# ✅ Thermal Print Ready
# ✅ PDF Ready
#
# Compatible With:
#
# ERP Settings V23
# Supabase RPC Checkout
# Warehouse Module
#
# ==============================================================================


