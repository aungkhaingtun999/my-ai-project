# ==========================================================
# pages/10_Suppliers.py
# ERP ENTERPRISE v15
# Supplier Management
# ==========================================================

import streamlit as st
import time
from database import get_supabase


# ----------------------------------------------------------
# DATABASE
# ----------------------------------------------------------

supabase = get_supabase()


# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------

st.set_page_config(
    page_title="Suppliers Management",
    page_icon="🏭",
    layout="wide"
)


# ----------------------------------------------------------
# TITLE
# ----------------------------------------------------------

st.title("🏭 Suppliers Management")


# ----------------------------------------------------------
# LOAD SUPPLIERS
# ----------------------------------------------------------

def get_suppliers():

    try:
        response = (
            supabase
            .table("suppliers")
            .select("*")
            .order("id", desc=True)
            .execute()
        )

        return response.data or []

    except Exception as e:
        st.error("Failed to load suppliers")
        st.exception(e)
        return []



# ----------------------------------------------------------
# ADD SUPPLIER
# ----------------------------------------------------------

def add_supplier(
    company_name,
    phone,
    address,
    email="",
    contact_name=""
):

    try:

        supplier_code = (
            f"SUP-{int(time.time())}"
        )

        response = (
            supabase
            .table("suppliers")
            .insert(
                {
                    "supplier_code": supplier_code,
                    "company_name": company_name,
                    "contact_name": contact_name,
                    "phone": phone,
                    "email": email,
                    "address": address,
                    "is_active": True
                }
            )
            .execute()
        )

        return response.data

    except Exception as e:

        st.error("Supplier insert failed")
        st.exception(e)

        return None



# ----------------------------------------------------------
# SUPPLIER LIST
# ----------------------------------------------------------

st.subheader("📋 Supplier List")


suppliers = get_suppliers()


if suppliers:

    search = st.text_input(
        "🔍 Search Supplier"
    )


    filtered = suppliers


    if search:

        filtered = [
            s for s in suppliers
            if search.lower()
            in str(
                s.get("company_name","")
            ).lower()
        ]


    st.dataframe(
        filtered,
        use_container_width=True
    )


else:

    st.info(
        "No suppliers found"
    )



# ----------------------------------------------------------
# ADD SUPPLIER FORM
# ----------------------------------------------------------

st.divider()

st.subheader(
    "➕ Add Supplier"
)


with st.form(
    "supplier_form",
    clear_on_submit=True
):

    company_name = st.text_input(
        "Supplier Name *"
    )

    contact_name = st.text_input(
        "Contact Person"
    )


    phone = st.text_input(
        "Phone"
    )


    email = st.text_input(
        "Email"
    )


    address = st.text_area(
        "Address"
    )


    submit = st.form_submit_button(
        "💾 Save Supplier",
        use_container_width=True
    )


    if submit:

        if not company_name.strip():

            st.error(
                "Supplier name required"
            )

            st.stop()



        result = add_supplier(
            company_name.strip(),
            phone.strip(),
            address.strip(),
            email.strip(),
            contact_name.strip()
        )


        if result:

            st.success(
                "Supplier added successfully"
            )

            time.sleep(1)

            st.rerun()
