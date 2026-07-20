import streamlit as st
from database import get_supabase
from utils.ui import show_table
# Supabase client ကို initialize လုပ်ခြင်း
supabase = get_supabase()

def run():
    st.title("👥 Customer Management")

    # Fetch data from Supabase
    try:
        response = supabase.table("customers").select("*").execute()
        data = response.data or []
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        data = []

    st.subheader("Customer List")

    if data:
        st.dataframe(data, use_container_width=True)
    else:
        st.info("No customers found.")

    # Show_table function ကို ထည့်သွင်းခြင်း
    show_table("customers")

    st.divider()

    st.subheader("➕ Add Customer")

    # Form inputs
    name = st.text_input("Customer Name")
    phone = st.text_input("Phone Number")
    address = st.text_area("Address")

    if st.button("Save Customer"):
        # Validation
        if not name.strip():
            st.error("Customer name is required.")
            st.stop()

        try:
            # Insert into Supabase
            supabase.table("customers").insert({
                "name": name.strip(),
                "phone": phone.strip(),
                "address": address.strip()
            }).execute()

            st.success("Customer added successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    run()
    
