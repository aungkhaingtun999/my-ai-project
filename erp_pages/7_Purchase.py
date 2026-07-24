# ==============================================================================
# pages/4_Purchase.py
# ERP ENTERPRISE PURCHASE RECEIVE v3.0
# PART 1/3
# RUN() COMPATIBLE BUILD
# ==============================================================================

import os
import sys
from decimal import Decimal

import streamlit as st


# ==============================================================================
# ROOT PATH
# ==============================================================================

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)


# ==============================================================================
# IMPORTS
# ==============================================================================

from auth import is_authenticated

from database import (
    create_audit_log
)

from erp_core import (
    get_products,
    get_suppliers,
    get_warehouses,
    purchase_receive_rpc
)

from utils.ui import show_table



# ==============================================================================
# PAGE CONFIG
# ==============================================================================

st.set_page_config(
    page_title="Purchase Receive",
    page_icon="📦",
    layout="wide"
)



# ==============================================================================
# SAFE NAME HELPERS
# ==============================================================================


def supplier_name(data):

    return (
        data.get("company_name")
        or
        data.get("name")
        or
        data.get("supplier_name")
        or
        f"Supplier #{data.get('id')}"
    )



def warehouse_name(data):

    return (
        data.get("name")
        or
        data.get("warehouse_name")
        or
        data.get("code")
        or
        f"Warehouse #{data.get('id')}"
    )



def product_name(data):

    return (
        data.get("name")
        or
        data.get("product_name")
        or
        f"Product #{data.get('id')}"
    )



# ==============================================================================
# MAIN RUN
# ==============================================================================


def run():


    # --------------------------------------------------------------------------
    # AUTH
    # --------------------------------------------------------------------------

    if not is_authenticated():

        st.error(
            "ကျေးဇူးပြု၍ Login အရင်ဝင်ပါ။"
        )

        st.stop()



    # --------------------------------------------------------------------------
    # TITLE
    # --------------------------------------------------------------------------

    st.title(
        "📦 Purchase Receive"
    )



    # --------------------------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------------------------

    try:

        suppliers = get_suppliers()

        warehouses = get_warehouses()

        products = get_products()


    except Exception as e:

        st.error(
            f"Data loading error : {e}"
        )

        st.stop()



    if not suppliers:

        st.error(
            "Supplier မရှိပါ"
        )

        st.stop()



    if not warehouses:

        st.error(
            "Warehouse မရှိပါ"
        )

        st.stop()



    if not products:

        st.error(
            "Product မရှိပါ"
        )

        st.stop()



    # --------------------------------------------------------------------------
    # SESSION
    # --------------------------------------------------------------------------

    if "purchase_cart" not in st.session_state:

        st.session_state.purchase_cart = []



    if "purchase_supplier_id" not in st.session_state:

        st.session_state.purchase_supplier_id = None



    if "purchase_warehouse_id" not in st.session_state:

        st.session_state.purchase_warehouse_id = None



    cart_exists = (
        len(
            st.session_state.purchase_cart
        )
        >
        0
    )



    # --------------------------------------------------------------------------
    # PURCHASE INFORMATION
    # --------------------------------------------------------------------------

    st.subheader(
        "🏭 Purchase Information"
    )


    supplier_ids = [
        s["id"]
        for s in suppliers
    ]


    warehouse_ids = [
        w["id"]
        for w in warehouses
    ]



    if (
        st.session_state.purchase_supplier_id
        in supplier_ids
    ):

        supplier_index = supplier_ids.index(
            st.session_state.purchase_supplier_id
        )

    else:

        supplier_index = 0




    selected_supplier = st.selectbox(

        "Supplier",

        suppliers,

        index=supplier_index,

        format_func=supplier_name,

        disabled=cart_exists

    )



    if (
        st.session_state.purchase_warehouse_id
        in warehouse_ids
    ):

        warehouse_index = warehouse_ids.index(
            st.session_state.purchase_warehouse_id
        )

    else:

        warehouse_index = 0



    selected_warehouse = st.selectbox(

        "Warehouse",

        warehouses,

        index=warehouse_index,

        format_func=warehouse_name,

        disabled=cart_exists

    )



    if not cart_exists:

        st.session_state.purchase_supplier_id = (
            selected_supplier["id"]
        )


        st.session_state.purchase_warehouse_id = (
            selected_warehouse["id"]
        )



    st.divider()
    # ==============================================================================
# PART 2/3
# PRODUCT ADD + PURCHASE CART ENGINE
# ==============================================================================


    # --------------------------------------------------------------------------
    # ADD PRODUCT
    # --------------------------------------------------------------------------

    st.subheader(
        "➕ Add Product"
    )


    with st.container(border=True):


        product = st.selectbox(

            "Product",

            products,

            format_func=lambda x: (
                f"{product_name(x)} "
                f"({x.get('sku','')})"
            )

        )


        col1, col2 = st.columns(2)



        qty = col1.number_input(

            "Quantity",

            min_value=1,

            step=1

        )



        cost = col2.number_input(

            "Cost Price",

            min_value=0.0,

            value=float(
                product.get(
                    "purchase_price",
                    0
                )
                or 0
            )

        )



        if st.button(

            "➕ Add To Cart",

            use_container_width=True

        ):



            exists = False



            for item in st.session_state.purchase_cart:


                if item["product_id"] == product["id"]:



                    old_qty = item["qty"]

                    old_cost = Decimal(
                        str(
                            item["cost"]
                        )
                    )


                    new_qty = (
                        old_qty
                        +
                        qty
                    )


                    new_cost = (

                        (
                            old_cost
                            *
                            old_qty
                        )

                        +

                        (
                            Decimal(
                                str(cost)
                            )
                            *
                            qty
                        )

                    ) / new_qty



                    item["qty"] = new_qty


                    item["cost"] = float(
                        new_cost
                    )


                    exists = True


                    break




            if not exists:


                st.session_state.purchase_cart.append(

                    {

                        "product_id":
                            product["id"],


                        "name":
                            product_name(product),


                        "qty":
                            int(qty),


                        "cost":
                            float(cost)

                    }

                )



            st.success(
                "Product Added"
            )


            st.rerun()



    # --------------------------------------------------------------------------
    # PURCHASE CART
    # --------------------------------------------------------------------------


    if st.session_state.purchase_cart:


        st.divider()


        st.subheader(
            "🛒 Purchase Cart"
        )



        total = 0


        table_data = []



        for index, item in enumerate(

            st.session_state.purchase_cart

        ):



            amount = (

                item["qty"]

                *

                item["cost"]

            )


            total += amount



            table_data.append(

                {

                    "No":
                        index + 1,


                    "Product Name":
                        item["name"],


                    "Qty":
                        item["qty"],


                    "Cost":
                        f"{item['cost']:,.2f}",


                    "Amount":
                        f"{amount:,.2f}"

                }

            )



        show_table(
            table_data
        )



        st.metric(

            "Total Purchase Amount",

            f"{total:,.2f} MMK"

        )



        # ----------------------------------------------------------------------
        # REMOVE ITEM
        # ----------------------------------------------------------------------


        col1, col2 = st.columns(2)



        with col1:


            remove_index = st.selectbox(

                "Select item to remove",

                options=range(

                    len(
                        st.session_state.purchase_cart
                    )

                ),


                format_func=lambda i:

                    (
                        f"{i+1}. "
                        +
                        st.session_state.purchase_cart[i]["name"]
                    )

            )



        with col2:


            st.write("")


            st.write("")



            if st.button(

                "❌ Remove Selected Item",

                use_container_width=True

            ):


                st.session_state.purchase_cart.pop(

                    remove_index

                )


                st.rerun()



        st.divider()
# ==============================================================================
# PART 3/3
# SAVE PURCHASE + RPC + RESET
# ==============================================================================


        # ----------------------------------------------------------------------
        # CONFIRM PURCHASE
        # ----------------------------------------------------------------------

        if st.button(

            "✅ Confirm Purchase Receive",

            type="primary",

            use_container_width=True

        ):



            user_id = st.session_state.get(
                "user_id"
            )


            success = []

            errors = []



            with st.spinner(

                "Processing Purchase..."

            ):



                for item in st.session_state.purchase_cart:



                    try:


                        result = purchase_receive_rpc(

                            item["product_id"],

                            selected_supplier["id"],

                            selected_warehouse["id"],

                            item["qty"],

                            item["cost"],

                            "cash",

                            "Purchase Receive Entry",

                            user_id

                        )



                        if isinstance(

                            result,

                            dict

                        ):



                            if result.get(

                                "success",

                                False

                            ):



                                purchase_no = (

                                    result.get(
                                        "purchase_no"
                                    )

                                    or

                                    "SUCCESS"

                                )



                                success.append(

                                    purchase_no

                                )



                                # ------------------------------------------
                                # AUDIT LOG
                                # ------------------------------------------


                                create_audit_log(

                                    user_id,

                                    "PURCHASE_RECEIVE",

                                    (
                                        f"{purchase_no} "
                                        f"{item['name']}"
                                    )

                                )



                            else:



                                errors.append(

                                    (
                                        item["name"]

                                        +

                                        " : "

                                        +

                                        str(

                                            result.get(

                                                "message",

                                                "Unknown Error"

                                            )

                                        )

                                    )

                                )



                        else:



                            errors.append(

                                (
                                    item["name"]

                                    +

                                    " : RPC Return Error"

                                )

                            )



                    except Exception as e:



                        errors.append(

                            (
                                item["name"]

                                +

                                " : "

                                +

                                str(e)

                            )

                        )



            # ------------------------------------------------------------------
            # RESULT
            # ------------------------------------------------------------------


            if success:



                st.success(

                    "Purchase Completed : "

                    +

                    ", ".join(success)

                )



                st.session_state.purchase_cart = []

                st.session_state.purchase_supplier_id = None

                st.session_state.purchase_warehouse_id = None



                st.rerun()




            if errors:



                st.error(

                    "\n".join(errors)

                )



        # ----------------------------------------------------------------------
        # CLEAR CART
        # ----------------------------------------------------------------------


        if st.button(

            "🗑 Clear Cart",

            use_container_width=True

        ):



            st.session_state.purchase_cart = []

            st.session_state.purchase_supplier_id = None

            st.session_state.purchase_warehouse_id = None


            st.rerun()





# ==============================================================================
# DIRECT RUN SUPPORT
# ==============================================================================


if __name__ == "__main__":

    run()
