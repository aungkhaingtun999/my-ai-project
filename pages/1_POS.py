# ==============================================================================
# pages/1_POS.py v4.7.0 - ENTERPRISE POS RELEASE
# SKU + BARCODE SEARCH ENABLED
# ==============================================================================

import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

import streamlit as st

from database import (
    get_products,
    checkout_sale_rpc,
    get_setting,
    get_default_warehouse_id
)

from auth import is_authenticated
from language import t, language_selector


# ---------------- Utilities ----------------

try:
    from utils.thermal_receipt import print_thermal
except:
    print_thermal = None


try:
    from utils.receipt_pdf import generate_pdf
except:
    generate_pdf = None



# ---------------- Page ----------------

st.set_page_config(
    page_title="Enterprise POS",
    layout="wide"
)

language_selector()


if not is_authenticated():
    st.warning(t("auth.login_required"))
    st.stop()



# ---------------- Session ----------------

if "cart" not in st.session_state:
    st.session_state.cart = []

if "show_receipt" not in st.session_state:
    st.session_state.show_receipt = False

if "processing" not in st.session_state:
    st.session_state.processing = False

if "sale_data" not in st.session_state:
    st.session_state.sale_data = None



# ---------------- Load Data ----------------

warehouse_id = get_default_warehouse_id()

products = get_products(
    warehouse_id=warehouse_id
)


if not products:
    st.error(t("app.no_product"))
    st.stop()



st.title("🛒 Enterprise POS")



# ==================================================
# PRODUCT SEARCH
# Name + SKU + Barcode
# ==================================================

st.subheader("🔍 Product Search")


col1, col2, col3 = st.columns(3)


with col1:
    name_search = st.text_input(
        "Product Name"
    )


with col2:
    sku_search = st.text_input(
        "SKU"
    )


with col3:
    barcode_search = st.text_input(
        "Barcode"
    )



selected = None



# Search Engine

if name_search or sku_search or barcode_search:

    matches = []


    for p in products:

        name_match = (
            name_search.lower() in str(p.get("name","")).lower()
            if name_search else True
        )

        sku_match = (
            sku_search.lower() in str(p.get("sku","")).lower()
            if sku_search else True
        )


        barcode_match = (
            barcode_search in str(p.get("barcode",""))
            if barcode_search else True
        )


        if name_match and sku_match and barcode_match:
            matches.append(p)



    if matches:

        selected = st.selectbox(
            "Select Product",
            matches,
            format_func=lambda x:
            f"{x['name']} | SKU:{x.get('sku','')} | Barcode:{x.get('barcode','')} | Stock:{x.get('stock',0)}"
        )

    else:
        st.warning("No product found")



# ==================================================
# ADD CART
# ==================================================

if selected:


    qty = st.number_input(
        "Quantity",
        min_value=1,
        value=1
    )


    if st.button(
        "➕ Add To Cart"
    ):


        current_qty = sum(
            item["qty"]
            for item in st.session_state.cart
            if item["id"] == selected["id"]
        )


        if current_qty + qty > selected["stock"]:

            st.error(
                f"Not enough stock. Available {selected['stock']}"
            )


        else:

            exists = False


            for item in st.session_state.cart:

                if item["id"] == selected["id"]:

                    item["qty"] += int(qty)
                    exists = True
                    break



            if not exists:

                st.session_state.cart.append(
                    {
                        "id": selected["id"],
                        "name": selected["name"],
                        "sku": selected.get("sku"),
                        "barcode": selected.get("barcode"),
                        "selling_price": float(
                            selected["selling_price"]
                        ),
                        "qty": int(qty),
                        "stock": selected["stock"]
                    }
                )


            st.rerun()



# ==================================================
# CART + CHECKOUT
# ==================================================

if st.session_state.cart and not st.session_state.show_receipt:


    st.subheader("🛒 Cart")


    subtotal = 0


    for item in st.session_state.cart:


        line_total = (
            item["selling_price"]
            *
            item["qty"]
        )


        subtotal += line_total


        st.write(
            f"""
            {item['name']}  
            SKU:{item.get('sku')}  
            Qty:{item['qty']}  
            Amount:{line_total:,.0f} MMK
            """
        )



    tax_rate = float(
        get_setting(
            "default_tax_rate",
            0
        )
    )


    discount = st.number_input(
        "Discount",
        min_value=0.0,
        value=0.0
    )



    total = (
        subtotal
        +
        subtotal * tax_rate / 100
        -
        discount
    )


    st.write(
        f"""
        ### Total : {total:,.0f} MMK
        """
    )



    payment_method = st.radio(
        "Payment",
        [
            "cash",
            "card",
            "mobile"
        ],
        horizontal=True
    )


    received = total


    if payment_method == "cash":

        received = st.number_input(
            "Received Amount",
            value=float(total)
        )


    if received < total:

        st.error(
            "Insufficient payment"
        )

    else:


        if st.button(
            "✅ Confirm Sale",
            disabled=st.session_state.processing
        ):


            st.session_state.processing = True


            try:


                cart_payload = [

                    {
                        "id":x["id"],
                        "qty":int(x["qty"]),
                        "selling_price":float(
                            x["selling_price"]
                        )
                    }

                    for x in st.session_state.cart

                ]



                result = checkout_sale_rpc(

                    cart=cart_payload,

                    paid_amount=received,

                    warehouse_id=warehouse_id,

                    cashier_id=st.session_state.get(
                        "user_id"
                    ),

                    payment_method=payment_method,

                    tax_rate=tax_rate,

                    discount=discount
                )



                if result.get("success"):


                    st.session_state.sale_data = {

                        "invoice_no":
                        result.get(
                            "data",
                            {}
                        ).get(
                            "invoice_no",
                            "N/A"
                        ),

                        "total":total

                    }


                    st.session_state.show_receipt=True

                    st.session_state.processing=False

                    st.rerun()



                else:

                    raise Exception(
                        result.get("message")
                    )



            except Exception as e:

                st.session_state.processing=False

                st.error(
                    str(e)
                )



# ==================================================
# RECEIPT
# ==================================================

if st.session_state.show_receipt:


    st.success(
        f"Invoice : {st.session_state.sale_data['invoice_no']}"
    )


    if print_thermal:

        if st.button("🖨 Print Thermal"):

            print_thermal(
                st.session_state.sale_data
            )



    if generate_pdf:

        if st.button("📄 PDF Receipt"):

            generate_pdf(
                st.session_state.sale_data
            )



    if st.button(
        "🆕 New Sale"
    ):


        st.session_state.update(

            {
                "cart":[],
                "show_receipt":False,
                "processing":False,
                "sale_data":None
            }

        )


        st.rerun()
