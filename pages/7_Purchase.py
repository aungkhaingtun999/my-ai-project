# ==========================================
# pages/7_Purchase.py
# ERP ENTERPRISE PURCHASE RECEIVE v2
# ==========================================

import streamlit as st
import sys
import os
from decimal import Decimal


sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)


from database import (
    get_suppliers,
    get_warehouses,
    get_products,
    purchase_receive_rpc,
    create_audit_log
)

from auth import is_authenticated


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Purchase Receive",
    page_icon="📦",
    layout="wide"
)


# ==========================================
# AUTH
# ==========================================

if not is_authenticated():
    st.error("ကျေးဇူးပြု၍ Login အရင်ဝင်ပါ။")
    st.stop()



st.title("📦 Purchase Receive")


# ==========================================
# LOAD DATA
# ==========================================

suppliers = get_suppliers()
warehouses = get_warehouses()
products = get_products()


if not suppliers:
    st.error("Supplier မရှိပါ")
    st.stop()


if not warehouses:
    st.error("Warehouse မရှိပါ")
    st.stop()


if not products:
    st.error("Product မရှိပါ")
    st.stop()



# ==========================================
# SESSION
# ==========================================

if "purchase_cart" not in st.session_state:
    st.session_state.purchase_cart = []


if "purchase_supplier_id" not in st.session_state:
    st.session_state.purchase_supplier_id = None


if "purchase_warehouse_id" not in st.session_state:
    st.session_state.purchase_warehouse_id = None


cart_exists = len(
    st.session_state.purchase_cart
) > 0



# ==========================================
# SUPPLIER / WAREHOUSE
# ==========================================

st.subheader("🏭 Purchase Information")


supplier_ids = [
    x["id"] for x in suppliers
]


warehouse_ids = [
    x["id"] for x in warehouses
]


if st.session_state.purchase_supplier_id in supplier_ids:
    supplier_index = supplier_ids.index(
        st.session_state.purchase_supplier_id
    )
else:
    supplier_index = 0



selected_supplier = st.selectbox(
    "Supplier",
    suppliers,
    index=supplier_index,
    format_func=lambda x:x["name"],
    disabled=cart_exists
)



if st.session_state.purchase_warehouse_id in warehouse_ids:
    warehouse_index = warehouse_ids.index(
        st.session_state.purchase_warehouse_id
    )
else:
    warehouse_index = 0



selected_warehouse = st.selectbox(
    "Warehouse",
    warehouses,
    index=warehouse_index,
    format_func=lambda x:
        f"{x['name']} - {x.get('branch','')}",
    disabled=cart_exists
)



if not cart_exists:

    st.session_state.purchase_supplier_id = (
        selected_supplier["id"]
    )

    st.session_state.purchase_warehouse_id = (
        selected_warehouse["id"]
    )



# ==========================================
# ADD ITEM
# ==========================================

st.divider()

st.subheader("➕ Add Product")


with st.container(border=True):

    product = st.selectbox(
        "Product",
        products,
        format_func=lambda x:
        f"{x['name']} ({x.get('sku','')})"
    )


    c1,c2 = st.columns(2)


    qty = c1.number_input(
        "Quantity",
        min_value=1,
        step=1
    )


    cost = c2.number_input(
        "Cost Price",
        min_value=0.0,
        value=float(
            product.get(
                "purchase_price"
            ) or 0
        )
    )


    if st.button(
        "➕ Add To Cart",
        use_container_width=True
    ):


        exist = False


        for item in st.session_state.purchase_cart:

            if item["product_id"] == product["id"]:


                old_qty = item["qty"]

                old_cost = Decimal(
                    str(item["cost"])
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
                        Decimal(str(cost))
                        *
                        qty
                    )
                ) / new_qty


                item["qty"] = new_qty

                item["cost"] = float(
                    new_cost
                )


                exist=True
                break



        if not exist:

            st.session_state.purchase_cart.append(
                {
                    "product_id":product["id"],
                    "name":product["name"],
                    "qty":int(qty),
                    "cost":float(cost)
                }
            )


        st.rerun()



# ==========================================
# CART
# ==========================================

if st.session_state.purchase_cart:


    st.divider()

    st.subheader("🛒 Purchase Cart")


    total = 0


    for item in st.session_state.purchase_cart:


        amount = (
            item["qty"]
            *
            item["cost"]
        )


        total += amount


        st.write(
            f"""
**{item['name']}**

Qty : {item['qty']}

Cost : {item['cost']:,.0f}

Amount : {amount:,.0f}

---
"""
        )


    st.metric(
        "Total Purchase Amount",
        f"{total:,.0f} MMK"
    )



    # ==================================
    # SAVE
    # ==================================

    if st.button(
        "✅ Confirm Purchase Receive",
        type="primary",
        use_container_width=True
    ):


        user_id = st.session_state.get(
            "user_id"
        )


        success=[]
        errors=[]


        with st.spinner(
            "Processing Purchase..."
        ):


            for item in st.session_state.purchase_cart:


                result = purchase_receive_rpc(

                    item["product_id"],

                    selected_supplier["id"],

                    selected_warehouse["id"],

                    item["qty"],

                    item["cost"],

                    "Mobile Purchase Entry",

                    user_id
                )



                if isinstance(result,dict):

                    if result.get("success"):

                        po = result.get(
                            "purchase_no",
                            "SUCCESS"
                        )

                        success.append(po)


                        create_audit_log(
                            user_id,
                            "PURCHASE_RECEIVE",
                            f"{po} {item['name']}"
                        )


                    else:

                        errors.append(
                            f"{item['name']} : "
                            f"{result.get('message','Unknown Error')}"
                        )


                else:

                    errors.append(
                        f"{item['name']} RPC Return Error"
                    )



        if success:

            st.success(
                "Purchase Completed : "
                +
                ", ".join(success)
            )

            st.session_state.purchase_cart=[]

            st.session_state.purchase_supplier_id=None

            st.session_state.purchase_warehouse_id=None

            st.rerun()



        if errors:

            st.error(
                "\n".join(errors)
            )



    if st.button(
        "🗑 Clear Cart",
        use_container_width=True
    ):

        st.session_state.purchase_cart=[]

        st.session_state.purchase_supplier_id=None

        st.session_state.purchase_warehouse_id=None

        st.rerun()
