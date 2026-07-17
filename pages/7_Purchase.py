import streamlit as st
import sys
import os

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


st.set_page_config(
    page_title="Purchase Receive",
    layout="centered",
    page_icon="📦"
)


# ==============================
# AUTH CHECK
# ==============================

if not is_authenticated():
    st.error("ကျေးဇူးပြု၍ Login အရင်ဝင်ပါ။")
    st.stop()


st.title("📦 Purchase Receive")


# ==============================
# LOAD DATA
# ==============================

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



# ==============================
# SESSION STATE
# ==============================

if "purchase_cart" not in st.session_state:
    st.session_state.purchase_cart = []


if "purchase_supplier" not in st.session_state:
    st.session_state.purchase_supplier = None


if "purchase_warehouse" not in st.session_state:
    st.session_state.purchase_warehouse = None



cart_exists = len(
    st.session_state.purchase_cart
) > 0



# ==============================
# SUPPLIER / WAREHOUSE
# ==============================


st.subheader("Supplier & Warehouse")


if cart_exists:
    st.warning(
        "Cart ထဲတွင် Item ရှိပါသည်။ "
        "Supplier/Warehouse မပြောင်းနိုင်ပါ။"
    )


supplier_index = 0

if st.session_state.purchase_supplier:

    for i,s in enumerate(suppliers):
        if s["id"] == st.session_state.purchase_supplier["id"]:
            supplier_index=i


selected_supplier = st.selectbox(
    "Supplier",
    suppliers,
    index=supplier_index,
    format_func=lambda x:x["name"],
    disabled=cart_exists
)


warehouse_index = 0

if st.session_state.purchase_warehouse:

    for i,w in enumerate(warehouses):
        if w["id"] == st.session_state.purchase_warehouse["id"]:
            warehouse_index=i



selected_warehouse = st.selectbox(
    "Warehouse",
    warehouses,
    index=warehouse_index,
    format_func=lambda x:
        f'{x["name"]} - {x["branch"]}',
    disabled=cart_exists
)



if not cart_exists:

    st.session_state.purchase_supplier = selected_supplier
    st.session_state.purchase_warehouse = selected_warehouse



# ==============================
# ADD PRODUCT
# ==============================


st.divider()

st.subheader("➕ Add Product")


with st.container(border=True):

    product = st.selectbox(
        "Product",
        products,
        format_func=lambda x:
            f'{x["name"]} ({x.get("sku","")})'
    )


    c1,c2 = st.columns(2)


    qty = c1.number_input(
        "Quantity",
        min_value=1,
        value=1,
        step=1
    )


    cost = c2.number_input(
        "Cost Price",
        min_value=0.0,
        value=float(
            product.get("purchase_price") or 0
        )
    )



    if st.button(
        "➕ Add To Cart",
        use_container_width=True
    ):

        found=False


        for item in st.session_state.purchase_cart:

            if item["product_id"] == product["id"]:


                old_qty=item["qty"]
                old_cost=item["cost"]


                new_qty = old_qty + qty


                # Weighted Average Cost

                item["cost"] = (
                    (old_qty*old_cost)
                    +
                    (qty*cost)
                ) / new_qty


                item["qty"]=new_qty

                found=True
                break



        if not found:

            st.session_state.purchase_cart.append(
                {
                    "product_id":product["id"],
                    "name":product["name"],
                    "qty":qty,
                    "cost":cost
                }
            )


        st.rerun()



# ==============================
# CART
# ==============================


if st.session_state.purchase_cart:


    st.divider()

    st.subheader("🛒 Purchase Cart")


    total=0


    for item in st.session_state.purchase_cart:


        subtotal = (
            item["qty"]
            *
            item["cost"]
        )

        total += subtotal


        st.write(
            f"""
            **{item['name']}**

            Qty : {item['qty']}

            Cost : {item['cost']:,.0f}

            Amount : {subtotal:,.0f}

            ---
            """
        )



    st.metric(
        "Total Amount MMK",
        f"{total:,.0f}"
    )



    # ==============================
    # CONFIRM
    # ==============================


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
            "Saving Purchase..."
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



                # Accept different RPC return styles

                if isinstance(result,dict):

                    if (
                        result.get("success")
                        or
                        result.get("purchase_no")
                        or
                        result.get("id")
                    ):


                        po = (
                            result.get("purchase_no")
                            or
                            str(result.get("id"))
                        )


                        success.append(po)


                        create_audit_log(
                            user_id,
                            "PURCHASE_RECEIVE",
                            f"{po} - {item['name']}"
                        )


                    else:

                        errors.append(
                            f"{item['name']} : {result.get('message')}"
                        )


                else:

                    errors.append(
                        f"{item['name']} : RPC Error"
                    )



        if success:

            st.success(
                "Purchase Completed : "
                +
                ", ".join(success)
            )

            st.session_state.purchase_cart=[]
            st.session_state.purchase_supplier=None
            st.session_state.purchase_warehouse=None

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
        st.session_state.purchase_supplier=None
        st.session_state.purchase_warehouse=None

        st.rerun()
