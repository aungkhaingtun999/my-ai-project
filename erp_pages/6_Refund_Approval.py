import streamlit as st
from database import db
from auth import require_login
from utils.ui import show_table
# ==========================================
# ACTION FUNCTIONS
# ==========================================
def handle_approval(refund_id, manager_id):
    try:
        db().rpc("approve_refund_rpc", {
            "p_refund_id": refund_id, 
            "p_manager_id": manager_id
        }).execute()
        st.success(f"Refund ID {refund_id} successfully approved.")
        st.rerun()
    except Exception as e:
        st.error(f"Approval error: {e}")

def handle_rejection(refund_id, manager_id, reason):
    try:
        result = db().rpc("reject_refund_rpc", {
            "p_refund_id": refund_id,
            "p_manager_id": manager_id,
            "p_reason": reason
        }).execute()
        
        if result.data and isinstance(result.data, dict) and result.data.get("success"):
            st.success(f"Refund ID {refund_id} rejected.")
            st.rerun()
        else:
            st.error(f"Rejection failed: {result.data}")
    except Exception as e:
        st.error(f"Rejection error: {e}")

# ==========================================
# MAIN RUN FUNCTION
# ==========================================
def run():
    st.set_page_config(page_title="Refund Approval", layout="wide")

    # AUTH
    user = require_login()

    # MANAGER ONLY
    if user.get("role_id") != 2:
        st.error("⛔ Access Denied. Manager permission required.")
        st.stop()

    st.title("✅ Refund Approval Center")

    # LOAD PENDING REFUNDS
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

    # DISPLAY
    if not data:
        st.info("No Pending Refunds")
    else:
        st.subheader(f"Pending Refund Count : {len(data)}")

        for refund in data:
            with st.container(border=True):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.write(f"**Refund ID:** {refund.get('id')}")
                    st.write(f"**Sale ID:** {refund.get('sale_id')}")

                with col2:
                    st.write(f"**Amount:** {refund.get('refund_amount', 0):,.0f} MMK")

                with col3:
                    st.write(f"**Date:** {refund.get('refund_date')}")
                    st.write(f"**Status:** {refund.get('status')}")

                # Approve/Reject UI
                app_col, rej_col = st.columns([1, 2])
                
                with app_col:
                    if st.button("✅ Approve", key=f"approve_{refund['id']}", type="primary"):
                        handle_approval(refund['id'], user['id'])

                with rej_col:
                    reject_reason = st.text_input("Reject Reason", key=f"reject_reason_{refund['id']}")
                    if st.button("❌ Reject", key=f"reject_{refund['id']}"):
                        if not reject_reason.strip():
                            st.warning("Please enter reject reason")
                        else:
                            handle_rejection(refund['id'], user['id'], reject_reason)

if __name__ == "__main__":
    run()
    
