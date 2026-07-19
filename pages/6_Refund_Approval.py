import streamlit as st
from database import db
from auth import require_login


st.set_page_config(
    page_title="Refund Approval",
    layout="wide"
)


# ==========================================
# AUTH
# ==========================================

user = require_login()


# ==========================================
# MANAGER ONLY
# ==========================================

if user["role_id"] != 2:
    st.error("⛔ Access Denied. Manager permission required.")
    st.stop()


st.title("✅ Refund Approval Center")


# ==========================================
# LOAD PENDING REFUNDS
# ==========================================

try:

    refunds = (
        db()
        .table("refunds")
        .select(
            """
            id,
            sale_id,
            refund_amount,
            status,
            cashier_id,
            refund_date
            """
        )
        .eq("status", "PENDING")
        .order("id", desc=True)
        .execute()
    )


    data = refunds.data


except Exception as e:

    st.error(e)
    st.stop()



# ==========================================
# DISPLAY
# ==========================================

if not data:

    st.info("No Pending Refunds")

else:

    st.subheader(
        f"Pending Refund Count : {len(data)}"
    )


    for refund in data:

        with st.container():

            st.divider()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(
                    f"Refund ID: {refund['id']}"
                )
                st.write(
                    f"Sale ID: {refund['sale_id']}"
                )

            with col2:
                st.write(
                    f"Amount: {refund['refund_amount']:,.0f} MMK"
                )

            with col3:
                st.write(
                    f"Date: {refund['refund_date']}"
                )


            if st.button(
                "View / Approve",
                key=f"refund_{refund['id']}"
            ):

                st.session_state.selected_refund = refund
                st.rerun()