# ==========================================================
# pages/Search.py
# ERP ENTERPRISE v15
# GLOBAL SEARCH ENGINE
# ==========================================================

import streamlit as st
from database import get_supabase
from utils.ui import show_table

# ----------------------------------------------------------
# DATABASE
# ----------------------------------------------------------

supabase = get_supabase()


# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------

st.set_page_config(
    page_title="ERP Global Search",
    page_icon="🔎",
    layout="wide"
)


# ----------------------------------------------------------
# SAFE SEARCH FUNCTION
# ----------------------------------------------------------

def safe_search(table, filters):

    try:

        query = (
            supabase
            .table(table)
            .select("*")
        )

        for column, keyword in filters:

            query = query.ilike(
                column,
                f"%{keyword}%"
            )

        result = query.execute()

        return result.data or []


    except Exception:

        return []



# ----------------------------------------------------------
# TITLE
# ----------------------------------------------------------

st.title(
    "🔎 ERP Global Search Engine"
)

st.caption(
    "Search Products, Suppliers, Customers and Transactions"
)


# ----------------------------------------------------------
# SEARCH BOX
# ----------------------------------------------------------

keyword = st.text_input(
    "Enter search keyword",
    placeholder="Barcode / Name / Phone / Invoice..."
)


if keyword.strip():


    keyword = keyword.strip()


    # ------------------------------------------------------
    # PRODUCT SEARCH
    # ------------------------------------------------------

    st.subheader(
        "📦 Products"
    )


    products = []


    try:

        products = (
            supabase
            .table("products")
            .select("*")
            .or_(
                f"name.ilike.%{keyword}%,"
                f"barcode.ilike.%{keyword}%"
            )
            .execute()
            .data
            or []
        )

    except Exception:

        products = []


    if products:

        st.dataframe(
            products,
            use_container_width=True
        )

    else:

        st.info(
            "No products found"
        )



    st.divider()



    # ------------------------------------------------------
    # SUPPLIER SEARCH
    # ------------------------------------------------------

    st.subheader(
        "🏭 Suppliers"
    )


    suppliers = []


    try:

        suppliers = (
            supabase
            .table("suppliers")
            .select("*")
            .or_(
                f"supplier_code.ilike.%{keyword}%,"
                f"company_name.ilike.%{keyword}%,"
                f"phone.ilike.%{keyword}%"
            )
            .execute()
            .data
            or []
        )


    except Exception:

        suppliers = []


    if suppliers:

        st.dataframe(
            suppliers,
            use_container_width=True
        )

    else:

        st.info(
            "No suppliers found"
        )



    st.divider()



    # ------------------------------------------------------
    # CUSTOMER SEARCH
    # ------------------------------------------------------

    st.subheader(
        "👥 Customers"
    )


    customers = []


    try:

        customers = (
            supabase
            .table("customers")
            .select("*")
            .or_(
                f"name.ilike.%{keyword}%,"
                f"phone.ilike.%{keyword}%"
            )
            .execute()
            .data
            or []
        )


    except Exception:

        customers = []


    if customers:

        st.dataframe(
            customers,
            use_container_width=True
        )

    else:

        st.info(
            "No customers found"
        )



    st.divider()



    # ------------------------------------------------------
    # SALES SEARCH
    # ------------------------------------------------------

    st.subheader(
        "🧾 Sales"
    )


    sales = []


    try:

        sales = (
            supabase
            .table("sales")
            .select("*")
            .ilike(
                "invoice_no",
                f"%{keyword}%"
            )
            .execute()
            .data
            or []
        )


    except Exception:

        sales = []


    if sales:

        st.dataframe(
            sales,
            use_container_width=True
        )

    else:

        st.info(
            "No sales found"
        )


else:

    st.info(
        "🔍 Type something to search..."
    )
