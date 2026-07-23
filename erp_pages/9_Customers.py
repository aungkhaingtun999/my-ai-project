import streamlit as st
from datetime import datetime
from database import get_supabase
from utils.ui import show_table

supabase = get_supabase()


def run():

    st.title("👥 Customer Management")


    # ==================================================
    # FETCH CUSTOMER DATA
    # ==================================================

    try:
        response = (
            supabase
            .table("customers")
            .select("*")
            .order("id", desc=True)
            .execute()
        )

        data = response.data or []

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        data = []


    st.subheader("Customer List")


    if data:
        st.dataframe(
            data,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No customers found.")


    show_table("customers")


    st.divider()


    # ==================================================
    # ADD CUSTOMER
    # ==================================================

    st.subheader("➕ Add Customer")


    full_name = st.text_input(
        "Customer Name"
    )

    phone = st.text_input(
        "Phone Number"
    )

    address = st.text_area(
        "Address"
    )


    if st.button("Save Customer"):


        if not full_name.strip():

            st.error(
                "Customer name is required."
            )

            st.stop()



        try:

            customer_data = {

                "customer_code":
                    "CUS" +
                    datetime.now()
                    .strftime("%Y%m%d%H%M%S"),

                "full_name":
                    full_name.strip(),

                "phone":
                    phone.strip(),

                "address":
                    address.strip(),

                "loyalty_points":
                    0,

                "is_active":
                    True
            }


            supabase.table(
                "customers"
            ).insert(
                customer_data
            ).execute()


            st.success(
                "Customer added successfully!"
            )

            st.rerun()


        except Exception as e:

            st.error(
                f"An error occurred: {e}"
            )



if __name__ == "__main__":
    run()
