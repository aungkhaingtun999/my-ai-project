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
        .eq("status", "PENDING")
        .order("id", desc=True)
        .execute()
    )

    data = refunds.data

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

            # Approve Button Logic
            if st.button("✅ Approve Refund", key=f"approve_{refund['id']}"):
                try:
                    result = (
                        db()
                        .rpc(
                            "approve_refund_rpc",
                            {
                                "p_refund_id": refund["id"],
                                "p_manager_id": user["id"]
                            }
                        )
                        .execute()
                    )

                    st.success(f"Refund ID {refund['id']} Approved Successfully")
                    st.rerun()

                except Exception as e:
                    st.error(f"Approve Error: {e}")

            # Reject Reason Input and Reject Button Logic
            reject_reason = st.text_input(
                "Reject Reason",
                key=f"reject_reason_{refund['id']}"
            )

            if st.button("❌ Reject Refund", key=f"reject_{refund['id']}"):
                if not reject_reason.strip():
                    st.warning("Please enter reject reason")
                else:
                    try:
                        result = (
                            db()
                            .rpc(
                                "reject_refund_rpc",
                                {
                                    "p_refund_id": refund["id"],
                                    "p_manager_id": user["id"],
                                    "p_reason": reject_reason
                                }
                            )
                            .execute()
                        )

                        response = result.data

                        if isinstance(response, dict) and response.get("success"):
                            st.success(f"Refund ID {refund['id']} Rejected")
                            st.rerun()
                        else:
                            st.error(response)

                    except Exception as e:
                        st.error(f"Reject Error: {e}")
                
