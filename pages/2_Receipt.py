import streamlit as st
from database import get_receipt

st.title("🧾 Receipt Viewer (ERP Level)")

# =========================
# INPUT
# =========================
receipt_no = st.text_input("Enter Receipt No (e.g. RCP-1)")

# =========================
# LOAD
# =========================
if st.button("🔍 Load Receipt"):

    if not receipt_no:
        st.warning("Please enter receipt number")

    else:
        result = get_receipt(receipt_no)

        if not result or not result.data:
            st.error("❌ Receipt not found")

        else:
            r = result.data

            st.success("✅ Receipt Found")

            # =========================
            # HEADER CARD
            # =========================
            st.subheader("🧾 Receipt Summary")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Receipt No", r.get("receipt_no", "-"))
                st.metric("Total", f"{r.get('total',0):,.0f} MMK")

            with col2:
                st.metric("Paid", f"{r.get('paid_amount',0):,.0f} MMK")
                st.metric("Change", f"{r.get('change_amount',0):,.0f} MMK")

            # =========================
            # EXTRA INFO
            # =========================
            st.divider()

            st.subheader("📌 Details")

            st.write("🧾 Receipt No:", r.get("receipt_no"))
            st.write("💰 Total:", r.get("total"))
            st.write("💵 Paid:", r.get("paid_amount"))
            st.write("🔄 Change:", r.get("change_amount"))

            # created_at may not exist depending schema
            if "created_at" in r:
                st.write("📅 Date:", r["created_at"])

            # =========================
            # ACTIONS
            # =========================
            st.divider()

            col1, col2 = st.columns(2)

            with col1:
                st.info("🖨️ Print / PDF feature will be added next step")

            with col2:
                st.download_button(
                    label="⬇ Export (future PDF)",
                    data=str(r),
                    file_name=f"{receipt_no}.txt"
                )