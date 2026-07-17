# ==============================================================================
# pages/2_Inventory.py
# ERP INVENTORY MANAGEMENT v1.0
# SUPABASE READY
# ==============================================================================

import streamlit as st
from datetime import datetime

from database import db


st.set_page_config(
    page_title="Inventory Management",
    layout="wide"
)


st.title("📦 Inventory Management System")


# ==============================================================================
# LOAD PRODUCTS
# ==============================================================================

def load_products():

    try:
        result = (
            db()
            .table("products")
            .select("*")
            .order("id")
            .execute()
        )

        return result.data or []

    except Exception as e:
        st.error(e)
        return []



# ==============================================================================
# ADD PRODUCT
# ==============================================================================

st.subheader("➕ Add New Product")


c1,c2 = st.columns(2)

with c1:

    name = st.text_input(
        "Product Name"
    )

    sku = st.text_input(
        "SKU"
    )

    barcode = st.text_input(
        "Barcode"
    )


with c2:

    purchase_price = st.number_input(
        "Purchase Price",
        min_value=0
    )

    selling_price = st.number_input(
        "Selling Price",
        min_value=0
    )

    stock = st.number_input(
        "Opening Stock",
        min_value=0,
        step=1
    )


minimum_stock = st.number_input(
    "Minimum Stock Alert",
    min_value=0,
    value=5
)



if st.button(
    "➕ Save Product",
    type="primary"
):

    if not name:

        st.error(
            "Product name required"
        )

    else:

        try:

            db().table(
                "products"
            ).insert({

                "name": name,

                "sku": sku,

                "barcode": barcode,

                "purchase_price": purchase_price,

                "selling_price": selling_price,

                "stock": stock,

                "minimum_stock": minimum_stock,

                "is_active": True

            }).execute()


            st.success(
                "Product added successfully"
            )

            st.rerun()


        except Exception as e:

            st.error(e)



# ==============================================================================
# INVENTORY LIST
# ==============================================================================

st.divider()

st.subheader(
    "📋 Inventory List"
)


products = load_products()


total_cost = 0
total_sell = 0
low_stock = 0



for p in products:


    col1,col2,col3,col4,col5 = st.columns(
        [3,2,2,2,1]
    )


    with col1:

        st.write(
            f"🛒 {p['name']}"
        )


    with col2:

        st.write(
            f"Cost: {p['purchase_price']:,.0f}"
        )


    with col3:

        st.write(
            f"Sell: {p['selling_price']:,.0f}"
        )


    with col4:

        stock = p.get(
            "stock",
            0
        )

        if stock <= p.get(
            "minimum_stock",
            5
        ):

            st.warning(
                f"Stock: {stock}"
            )

            low_stock += 1

        else:

            st.write(
                f"Stock: {stock}"
            )


    with col5:

        if st.button(
            "❌",
            key=f"del_{p['id']}"
        ):

            db().table(
                "products"
            ).update({

                "is_active":False

            }).eq(
                "id",
                p["id"]

            ).execute()


            st.rerun()



    total_cost += (
        p["purchase_price"]
        *
        p["stock"]
    )


    total_sell += (
        p["selling_price"]
        *
        p["stock"]
    )



# ==============================================================================
# SUMMARY
# ==============================================================================

st.divider()

st.subheader(
    "📊 Inventory Summary"
)


a,b,c = st.columns(3)


a.metric(
    "Total Products",
    len(products)
)


b.metric(
    "Stock Cost Value",
    f"{total_cost:,.0f} MMK"
)


c.metric(
    "Stock Selling Value",
    f"{total_sell:,.0f} MMK"
)



st.info(
    f"⚠️ Low Stock Items: {low_stock}"
)
