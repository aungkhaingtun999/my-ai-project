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
if user.get("role_id") != 2:
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
        .select("*")
        .execute()
    )

    data = refunds.data

    # Debug Section
    st.write("DEBUG USER:", user)
    st.write("DEBUG REFUNDS:")
    st.write(refunds.data)

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# ==========================================
# DISPLAY
# ==========================================
if not data:
    st.info("No Pending Refunds")
else:
    st.subheader(f"Pending Refund Count : {len(data)}")

    for refund in data:
        with st.container():
            st.divider()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"Refund ID: {refund.get('id')}")
                st.write(f"Sale ID: {refund.get('sale_id')}")

            with col2:
                st.write(f"Amount: {refund.get('refund_amount', 0):,.0f} MMK")

            with col3:
                st.write(f"Date: {refund.get('refund_date')}")
                st.write(f"Status: {refund.get('status')}")

            if st.button("View / Approve", key=f"refund_{refund.get('id')}"):
                st.session_state.selected_refund = refund
                st.rerun()

