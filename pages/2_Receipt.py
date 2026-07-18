# ==========================================
# pages/6_Receipt.py
# ERP ENTERPRISE RECEIPT VIEWER v2
# ==========================================

import streamlit as st

from database import (
    get_receipt,
    get_sale_items,
    search_receipts
)


# =========================
# PAGE
# =========================

st.title("🧾 Receipt Viewer (ERP Level)")


# =========================
# INPUT
# =========================
if "selected_receipt" in st.session_state:

    receipt_no = (
        st.session_state.selected_receipt
    )
receipt_no = st.text_input(
    "🔎 Search Receipt"
)


# =========================
# FLOATING SEARCH RESULT
# =========================

if receipt_no:


    suggestions = search_receipts(
        receipt_no
    )


    if suggestions:


        st.caption(
            "Matching Receipts"
        )


        for r in suggestions:


            label = (
                f"🧾 {r.get('invoice_no')}"
                f" | "
                f"{r.get('total',0):,.0f} MMK"
                f" | "
                f"{r.get('created_at','')}"
            )


            if st.button(
                label,
                key=f"receipt_{r['id']}"
            ):

                st.session_state.selected_receipt = (
                    r["invoice_no"]
                )

                st.rerun()



# =========================
# LOAD RECEIPT
# =========================

if st.button(
    "🔍 Load Receipt",
    type="primary"
):

    if not receipt_no.strip():

        st.warning(
            "Please enter receipt number"
        )

        st.stop()



    # =========================
    # GET SALE HEADER
    # =========================

    receipt = get_receipt(
        receipt_no.strip()
    )



    if not receipt:

        st.error(
            "❌ Receipt not found"
        )

        st.stop()



    st.success(
        "✅ Receipt Found"
    )



    sale_id = receipt.get(
        "id"
    )



    # =========================
    # GET ITEMS
    # =========================

    items = []

    if sale_id:

        items = get_sale_items(
            str(sale_id)
        )



    # =========================
    # SUMMARY
    # =========================

    st.divider()

    st.subheader(
        "🧾 Receipt Summary"
    )


    col1, col2, col3 = st.columns(3)



    with col1:

        st.metric(
            "Invoice No",
            receipt.get(
                "invoice_no",
                "-"
            )
        )


    with col2:

        st.metric(
            "Total",
            f"{receipt.get('total',0):,.0f} MMK"
        )


    with col3:

        st.metric(
            "Status",
            receipt.get(
                "sale_status",
                receipt.get(
                    "status",
                    "-"
                )
            )
        )



    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Paid",
            f"{receipt.get('paid_amount',0):,.0f}"
            " MMK"
        )


    with col2:

        st.metric(
            "Change",
            f"{receipt.get('change_amount',0):,.0f}"
            " MMK"
        )


    with col3:

        st.metric(
            "Payment",
            receipt.get(
                "payment_method",
                "-"
            )
        )



    # =========================
    # ITEMS TABLE
    # =========================

    st.divider()

    st.subheader(
        "🛒 Items"
    )


    if items:


        table = []


        for item in items:

            table.append(
                {
                    "Product ID":
                        item.get(
                            "product_id"
                        ),

                    "Qty":
                        item.get(
                            "quantity"
                        ),

                    "Price":
                        item.get(
                            "unit_price"
                        ),

                    "Total":
                        item.get(
                            "total"
                        )
                }
            )


        st.dataframe(
            table,
            use_container_width=True
        )


    else:

        st.info(
            "No sale items found"
        )



    # =========================
    # FINANCIAL DETAIL
    # =========================

    st.divider()

    st.subheader(
        "💰 Financial Details"
    )


    c1, c2 = st.columns(2)


    with c1:

        st.write(
            "Subtotal:",
            f"{receipt.get('subtotal',0):,.0f}"
        )

        st.write(
            "Discount:",
            f"{receipt.get('discount',0):,.0f}"
        )


    with c2:

        st.write(
            "Tax:",
            f"{receipt.get('tax',0):,.0f}"
        )

        st.write(
            "Grand Total:",
            f"{receipt.get('total',0):,.0f} MMK"
        )



    if receipt.get(
        "created_at"
    ):

        st.write(
            "📅 Date:",
            receipt["created_at"]
        )



    # =========================
    # ACTIONS
    # =========================

    st.divider()

    c1, c2 = st.columns(2)



    with c1:

        st.info(
            "🖨 Thermal Reprint / PDF Reprint "
            "can be connected here."
        )



    with c2:

        st.download_button(

            label="⬇ Export Receipt Data",

            data=str(receipt),

            file_name=
            f"{receipt_no}.txt"

        )
