# ==========================================
# pages/1_POS.py
# ERP ENTERPRISE POS v4.1
# STABLE CHECKOUT ENGINE
# ==========================================

import streamlit as st

from datetime import datetime
from zoneinfo import ZoneInfo


from database import (
    get_products,
    checkout_sale_rpc,
    get_setting
)

from auth import is_authenticated



# ==========================================
# PRINT MODULES
# ==========================================

try:
    from utils.thermal_receipt import print_thermal

except ImportError:

    def print_thermal(data):
        st.warning("Thermal printer utility missing.")



try:
    from utils.receipt_pdf import generate_pdf

except ImportError:

    def generate_pdf(data):
        st.warning("PDF generator missing.")



# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Enterprise POS",
    page_icon="🛒",
    layout="wide"
)



if not is_authenticated():

    st.error("ကျေးဇူးပြု၍ Login အရင်ဝင်ပါ။")
    st.stop()



# ==========================================
# SESSION
# ==========================================

if "cart" not in st.session_state:
    st.session_state.cart = []

if "show_receipt" not in st.session_state:
    st.session_state.show_receipt = False

if "sale_data" not in st.session_state:
    st.session_state.sale_data = None



def get_mst_now():

    return datetime.now(
        ZoneInfo("Asia/Yangon")
    ).strftime("%Y-%m-%d %H:%M:%S")



# ==========================================
# LOAD PRODUCTS
# ==========================================

products = get_products() or []


if not products:

    st.warning("Product မရှိသေးပါ။")
    st.stop()



st.title("🛒 Enterprise POS")



# ==========================================
# SEARCH
# ==========================================

c1, c2 = st.columns(2)


name_search = c1.text_input(
    "🔍 Product Name"
)


barcode_search = c2.text_input(
    "🔍 Barcode / SKU"
)


selected_product = None



if name_search:


    matches = [

        p for p in products

        if name_search.lower()
        in p["name"].lower()

    ]


    if matches:

        selected_product = st.selectbox(

            "Choose Product",

            matches,

            format_func=lambda x:
            f"{x['name']} | {x.get('sku','')}"

        )



elif barcode_search:


    matches = [

        p for p in products

        if barcode_search.lower()
        in str(p.get("barcode","")).lower()

        or barcode_search.lower()
        in str(p.get("sku","")).lower()

    ]


    if matches:

        selected_product = matches[0]



# ==========================================
# ADD CART
# ==========================================

if selected_product:


    qty = st.number_input(
        "Quantity",
        min_value=1,
        value=1
    )


    if st.button(
        "➕ Add To Cart",
        type="primary"
    ):


        found = False


        for item in st.session_state.cart:


            if item["id"] == selected_product["id"]:

                item["qty"] += int(qty)

                found = True

                break



        if not found:


            st.session_state.cart.append({

                "id":
                selected_product["id"],


                "name":
                selected_product["name"],


                "selling_price":
                float(selected_product["selling_price"]),


                "qty":
                int(qty),


                "stock":
                selected_product.get("stock",0)

            })


        st.rerun()



# ==========================================
# CART
# ==========================================

if st.session_state.cart and not st.session_state.show_receipt:


    st.divider()

    st.subheader("🛒 Cart")


    subtotal = 0


    for index,item in enumerate(
        st.session_state.cart.copy()
    ):


        a,b,c,d = st.columns(
            [4,1,2,1]
        )


        a.write(
            item["name"]
        )


        new_qty = b.number_input(

            "Qty",

            1,

            999,

            item["qty"],

            key=f"qty_{item['id']}"

        )


        st.session_state.cart[index]["qty"] = int(new_qty)



        amount = (
            item["selling_price"]
            *
            new_qty
        )


        c.write(
            f"{amount:,.0f}"
        )


        subtotal += amount



        if d.button(
            "🗑",
            key=f"del_{item['id']}"
        ):

            st.session_state.cart.pop(index)

            st.rerun()



    default_tax = float(
        get_setting(
            "default_tax_rate",
            0
        )
    )


    x,y = st.columns(2)


    tax_rate = x.number_input(
        "Tax %",
        value=default_tax
    )


    discount = y.number_input(
        "Discount",
        min_value=0.0
    )


    tax_amount = (
        subtotal *
        tax_rate /
        100
    )


    total = max(
        0,
        subtotal
        -
        discount
        +
        tax_amount
    )


    st.success(
        f"Total : {total:,.0f} MMK"
    )



    payment = st.radio(

        "Payment",

        [
            "Cash",
            "Card",
            "Mobile Banking",
            "Credit"
        ],

        horizontal=True

    )



    paid = total

    change = 0



    if payment == "Cash":


        paid = st.number_input(

            "Received Amount",

            min_value=0.0,

            value=float(total)

        )


        change = max(
            0,
            paid-total
        )

        st.info(
            f"Change : {change:,.0f}"
        )



    if st.button(

        "✅ Confirm Sale",

        type="primary"

    ):



        if paid < total:

            st.error(
                "Payment မလုံလောက်ပါ"
            )


        else:



            cart_payload = [


                {

                "id":i["id"],

                "qty":int(i["qty"]),

                "selling_price":
                float(i["selling_price"])

                }


                for i in st.session_state.cart

            ]



            result = checkout_sale_rpc(

                cart_payload,

                paid,

                st.session_state.get(
                    "user_id"
                )

            )



            if (

                isinstance(result,dict)

                and

                result.get("success")

            ):



                st.session_state.sale_data={


                    "receipt_no":
                    result.get("invoice_no"),


                    "sale_id":
                    result.get("sale_id"),


                    "items":
                    st.session_state.cart.copy(),


                    "total":
                    total,


                    "paid":
                    paid,


                    "change":
                    change,


                    "method":
                    payment,


                    "timestamp":
                    get_mst_now()

                }


                st.session_state.show_receipt=True

                st.rerun()



            else:


                st.error(

                    "Checkout Failed: "

                    +

                    str(
                        result.get(
                            "message",
                            "Unknown Error"
                        )
                    )

                )


                st.write(
                    "Debug:",
                    result
                )



# ==========================================
# RECEIPT
# ==========================================

if st.session_state.show_receipt:


    data = st.session_state.sale_data


    st.success(
        f"Sale Completed\nReceipt: {data['receipt_no']}"
    )


    st.write(
        f"Total {data['total']:,.0f} MMK"
    )


    p1,p2 = st.columns(2)


    if p1.button("🖨 Print"):

        print_thermal(data)



    if p2.button("📄 PDF"):

        generate_pdf(data)



    if st.button(
        "🔄 New Sale"
    ):

        st.session_state.cart=[]

        st.session_state.sale_data=None

        st.session_state.show_receipt=False

        st.rerun()
