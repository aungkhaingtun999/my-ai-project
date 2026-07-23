# ==========================================================
# pages/10_Suppliers.py
# ERP ENTERPRISE v15
# Supplier Management
# ==========================================================

import streamlit as st
import time
from database import get_supabase
from utils.ui import show_table
# ----------------------------------------------------------
# DATABASE
# ----------------------------------------------------------

supabase = get_supabase()

# ----------------------------------------------------------
# FUNCTIONS
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
        st.error("Failed to load suppliers.")
        st.exception(e)
        return []

def add_supplier(company_name, phone, address, email="", contact_name=""):
    try:
        supplier_code = f"SUP-{int(time.time())}"
        response = (
            supabase
            .table("suppliers")
            .insert({
                "supplier_code": supplier_code,
                "company_name": company_name,
                "contact_name": contact_name,
                "phone": phone,
                "email": email,
                "address": address,
                "is_active": True
            })
            .execute()
        )
        return response.data
    except Exception as e:
        st.error("Supplier insert failed")
        st.exception(e)
        return None

def Show_table(suppliers):
    if suppliers:
        search = st.text_input("🔍 Search Supplier")
        filtered = suppliers

        if search:
            search_lower = search.lower()
            filtered = [
                s for s in suppliers
                if search_lower in str(s.get("company_name", "")).lower()
            ]

        st.dataframe(filtered, use_container_width=True)
    else:
        st.info("No suppliers found")

# ----------------------------------------------------------
# MAIN RUN FUNCTION
# ----------------------------------------------------------
   def run():

    st.set_page_config(
        page_title="Supplier Management",
        page_icon="🏭",
        layout="wide"
    )


    st.title("🏭 Supplier Management")


    # Supplier List
    st.subheader("📋 Supplier List")

    suppliers = get_suppliers()


    Show_table(suppliers)



    # ==================================================
    # EDIT / DELETE SUPPLIER
    # ==================================================

    st.divider()

    st.subheader("✏️ Edit / Delete Supplier")


    if suppliers:

        supplier_map = {
            f"{s.get('supplier_code')} - {s.get('company_name')}": s
            for s in suppliers
        }


        selected_supplier = st.selectbox(
            "Select Supplier",
            supplier_map.keys()
        )


        supplier = supplier_map[selected_supplier]


        edit_company = st.text_input(
            "Supplier Name",
            value=supplier.get("company_name","")
        )


        edit_contact = st.text_input(
            "Contact Person",
            value=supplier.get("contact_name","")
        )


        edit_phone = st.text_input(
            "Phone",
            value=supplier.get("phone","")
        )


        edit_email = st.text_input(
            "Email",
            value=supplier.get("email","")
        )


        edit_address = st.text_area(
            "Address",
            value=supplier.get("address","")
        )


        if st.button("💾 Update Supplier"):

            supabase.table(
                "suppliers"
            ).update({

                "company_name": edit_company,
                "contact_name": edit_contact,
                "phone": edit_phone,
                "email": edit_email,
                "address": edit_address

            }).eq(
                "id",
                supplier["id"]
            ).execute()


            st.success("Supplier Updated")
            time.sleep(1)
            st.rerun()



        if st.button("🗑 Delete Supplier"):

            supabase.table(
                "suppliers"
            ).delete().eq(
                "id",
                supplier["id"]
            ).execute()


            st.success("Supplier Deleted")
            time.sleep(1)
            st.rerun()


    else:

        st.info("No suppliers found")



    # ==================================================
    # ADD SUPPLIER
    # ==================================================

    st.divider()

    st.subheader("➕ Add Supplier")

    with st.form("supplier_form", clear_on_submit=True):

        company_name = st.text_input("Supplier Name *")
        contact_name = st.text_input("Contact Person")
        phone = st.text_input("Phone")
        email = st.text_input("Email")
        address = st.text_area("Address")

        submit = st.form_submit_button(
            "💾 Save Supplier",
            use_container_width=True
        )

        if submit:
            ...                     
