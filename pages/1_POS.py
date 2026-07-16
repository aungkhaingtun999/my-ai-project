# ==========================================
# pages/1_POS.py
# ERP ENTERPRISE POS v4
# PART 1/2
# ==========================================

import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

from database import get_products, checkout_sale_rpc
from auth import is_authenticated

# ===============================
# PRINT MODULES
# ===============================

try:
    from utils.thermal_receipt import print_thermal
except ImportError:
    def print_thermal(data):
        st.warning("Thermal printer utility missing.")


try:
    from utils.receipt_pdf import generate_pdf
except ImportError:
    def generate_pdf(data):
        st.warning("PDF utility missing.")


# ===============================
# PAGE CONFIG
# ===============================

st.set_page_config(
    page_title="Enterprise POS",
    page_icon="🛒",
    layout="wide"
)


# ===============================
# AUTH
# ===============================

if not is_authenticated():
    st.error("ကျေးဇူးပြု၍ Login အရင်ဝင်ပါ။")
    st.stop()


# ===============================
# SESSION STATE
# ===============================

defaults = {
    "cart": [],
    "show_receipt": False,
    "sale_data": None
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ===============================
# TIME
# ===============================

def get_mst_now():
    return datetime.now(
        ZoneInfo("Asia/Yangon")
    ).strftime("%Y-%m-%d %H:%M:%S")


# ===============================
# LOAD PRODUCTS
# ===============================

products = get_products() or []


st.title("🛒 Enterprise POS")


# ===============================
# PRODUCT SEARCH
# ===============================

col1, col2 = st.columns(2)

name_search = col1.text_input(
    "🔍 Search Product Name"
)

code_search = col2.text_input(
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


elif code_search:

    matches = [
        p for p in products
        if code_search.lower()
        in str(p.get("barcode","")).lower()
        or code_search.lower()
        in str(p.get("sku","")).lower()
    ]

    if matches:
        selected_product = matches[0]


# ===============================
# ADD CART
# ===============================

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

        existing = next(
            (
                x for x in st.session_state.cart
                if x["id"] == selected_product["id"]
            ),
            None
        )


        if existing:

            existing["qty"] += int(qty)

        else:

            st.session_state.cart.append(
                {
                    "id": selected_product["id"],
                    "name": selected_product["name"],
                    "selling_price": float(
                        selected_product["selling_price"]
                    ),
                    "qty": int(qty),
                    "stock": selected_product["stock"]
                }
            )


        st.rerun()
        # ==========================================
# PART 2/2
# CART + CHECKOUT + RECEIPT
# ==========================================


# ===============================
# CART VIEW
# ===============================

if st.session_state.cart and not st.session_state.show_receipt:

    st.divider()
    st.subheader("🛒 Shopping Cart")


    subtotal = 0.0


    for index, item in enumerate(
        st.session_state.cart.copy()
    ):

        c1, c2, c3, c4 = st.columns(
            [4, 1, 2, 1]
        )


        c1.write(
            f"**{item['name']}**"
        )


        new_qty = c2.number_input(
            "Qty",
            min_value=1,
            max_value=999,
            value=int(item["qty"]),
            key=f"qty_{item['id']}"
        )


        st.session_state.cart[index]["qty"] = int(new_qty)


        item_total = (
            float(item["selling_price"])
            *
            int(new_qty)
        )


        c3.write(
            f"{item_total:,.0f} MMK"
        )


        if c4.button(
            "🗑",
            key=f"delete_{item['id']}"
        ):

            st.session_state.cart.pop(index)
            st.rerun()


        subtotal += item_total



    # ===============================
    # TAX DISCOUNT
    # ===============================

    st.divider()


    c1, c2 = st.columns(2)


    tax_rate = c1.number_input(
        "Tax (%)",
        min_value=0.0,
        value=0.0
    )


    discount = c2.number_input(
        "Discount (MMK)",
        min_value=0.0,
        value=0.0
    )


    tax_amount = (
        subtotal
        *
        tax_rate
        /
        100
    )


    final_total = (
        subtotal
        -
        discount
        +
        tax_amount
    )


    if final_total < 0:
        final_total = 0



    st.markdown(
        f"""
        ### 💰 Total
        **{final_total:,.0f} MMK**
        """
    )



    # ===============================
    # PAYMENT
    # ===============================

    st.divider()

    st.subheader(
        "💳 Payment"
    )


    payment_method = st.radio(
        "Payment Method",
        [
            "Cash",
            "Card",
            "Mobile Banking",
            "Credit"
        ],
        horizontal=True
    )


    paid_amount = final_total
    change_amount = 0



    if payment_method == "Cash":

        paid_amount = st.number_input(
            "Received Amount",
            min_value=0.0,
            value=float(final_total)
        )


        change_amount = max(
            0,
            paid_amount - final_total
        )


        st.info(
            f"Change: {change_amount:,.0f} MMK"
        )



    # ===============================
    # CHECKOUT
    # ===============================

    if st.button(
        "✅ Confirm Sale",
        type="primary"
    ):


        if paid_amount < final_total:

            st.error(
                "Payment amount is not enough."
            )

            st.stop()



        # RPC JSON PAYLOAD
        prepared_cart = []


        for item in st.session_state.cart:

            prepared_cart.append(
                {
                    "id": item["id"],
                    "qty": int(item["qty"]),
                    "selling_price":
                        float(item["selling_price"])
                }
            )



        # Get logged user id
        cashier_id = st.session_state.get(
            "user_id"
        )



        result = checkout_sale_rpc(
            prepared_cart,
            float(paid_amount),
            cashier_id
        )



        if (
            result
            and result.get("success")
        ):


            st.session_state.sale_data = {

                "receipt_no":
                    result.get("receipt_no"),

                "sale_id":
                    result.get("sale_id"),

                "items":
                    st.session_state.cart.copy(),

                "subtotal":
                    subtotal,

                "discount":
                    discount,

                "tax":
                    tax_amount,

                "total":
                    final_total,

                "method":
                    payment_method,

                "paid":
                    paid_amount,

                "change":
                    change_amount,

                "timestamp":
                    get_mst_now()
            }



            st.session_state.show_receipt = True

            st.rerun()



        else:

            st.error(
                f"Checkout Failed: {result.get('error')}"
            )





# ===============================
# RECEIPT
# ===============================


if st.session_state.show_receipt:


    data = st.session_state.sale_data


    st.success(
        f"✅ Sale Completed\n\n"
        f"Receipt : {data.get('receipt_no','N/A')}"
    )



    st.write(
        f"""
        **Payment:** {data['method']}

        **Total:** {data['total']:,.0f} MMK

        **Paid:** {data['paid']:,.0f} MMK

        **Change:** {data['change']:,.0f} MMK

        **Time:** {data['timestamp']}
        """
    )



    c1, c2 = st.columns(2)



    if c1.button(
        "🖨 Thermal Print"
    ):

        print_thermal(data)



    if c2.button(
        "📄 Generate PDF"
    ):

        generate_pdf(data)



    st.divider()



    if st.button(
        "🔄 New Sale"
    ):

        st.session_state.cart = []

        st.session_state.sale_data = None

        st.session_state.show_receipt = False

        st.rerun()
