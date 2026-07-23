import streamlit as st
from datetime import datetime
from database import get_supabase
from utils.ui import show_table


supabase = get_supabase()


def run():

    st.title("👥 Customer Management")


    # ================================
    # LOAD CUSTOMERS
    # ================================

    try:
        result = (
            supabase
            .table("customers")
            .select("*")
            .order("id", desc=True)
            .execute()
        )

        customers = result.data or []

    except Exception as e:
        st.error(e)
        customers = []


    st.subheader("Customer List")


    if not customers:
        st.info("No customers found.")

    else:

        for c in customers:

            with st.expander(
                f"👤 {c.get('full_name')}"
            ):

                st.write(
                    f"Code : {c.get('customer_code')}"
                )

                st.write(
                    f"Phone : {c.get('phone')}"
                )

                st.write(
                    f"Address : {c.get('address')}"
                )


                col1, col2 = st.columns(2)


                # =====================
                # EDIT
                # =====================

                with col1:

                    if st.button(
                        "✏️ Edit",
                        key=f"edit_{c['id']}"
                    ):

                        st.session_state.edit_customer = c


                # =====================
                # DELETE
                # =====================

                with col2:

                    if st.button(
                        "🗑 Delete",
                        key=f"delete_{c['id']}"
                    ):

                        try:

                            supabase.table(
                                "customers"
                            ).delete().eq(
                                "id",
                                c["id"]
                            ).execute()


                            st.success(
                                "Customer deleted"
                            )

                            st.rerun()


                        except Exception as e:

                            st.error(e)



    st.divider()



    # ================================
    # EDIT FORM
    # ================================

    if "edit_customer" in st.session_state:


        c = st.session_state.edit_customer


        st.subheader(
            "✏️ Edit Customer"
        )


        new_name = st.text_input(
            "Customer Name",
            value=c.get("full_name","")
        )


        new_phone = st.text_input(
            "Phone",
            value=c.get("phone","")
        )


        new_address = st.text_area(
            "Address",
            value=c.get("address","")
        )


        if st.button(
            "💾 Update Customer"
        ):

            try:

                supabase.table(
                    "customers"
                ).update({

                    "full_name":
                        new_name,

                    "phone":
                        new_phone,

                    "address":
                        new_address,

                    "updated_at":
                        datetime.now().isoformat()

                }).eq(
                    "id",
                    c["id"]
                ).execute()


                st.success(
                    "Customer updated"
                )


                del st.session_state.edit_customer

                st.rerun()


            except Exception as e:

                st.error(e)



    st.divider()



    # ================================
    # ADD CUSTOMER
    # ================================

    st.subheader(
        "➕ Add Customer"
    )


    name = st.text_input(
        "Customer Name"
    )

    phone = st.text_input(
        "Phone Number"
    )

    address = st.text_area(
        "Address"
    )


    if st.button(
        "Save Customer"
    ):


        if not name.strip():

            st.error(
                "Customer name required"
            )

            return


        try:

            supabase.table(
                "customers"
            ).insert({

                "customer_code":
                    "CUS" +
                    datetime.now()
                    .strftime("%Y%m%d%H%M%S"),

                "full_name":
                    name,

                "phone":
                    phone,

                "address":
                    address,

                "loyalty_points":
                    0,

                "is_active":
                    True

            }).execute()


            st.success(
                "Customer added"
            )

            st.rerun()


        except Exception as e:

            st.error(e)



if __name__ == "__main__":
    run()
