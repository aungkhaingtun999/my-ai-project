import streamlit as st
from database import get_receipt

st.title("🧾 Receipt Viewer")

receipt_no = st.text_input("Enter Receipt No (e.g. RCP-1)")

if st.button("Load Receipt"):

    result = get_receipt(receipt_no)

    if result.data:

        r = result.data

        st.success("Receipt Found")

        st.write("### Receipt Details")
        st.write("Receipt No:", r["receipt_no"])
        st.write("Total:", r["total"])
        st.write("Paid:", r["paid_amount"])
        st.write("Change:", r["change_amount"])
        st.write("Date:", r["created_at"])

        st.divider()

        st.info("🧾 Printable format coming next step (PDF export)")

    else:
        st.error("Receipt not found")