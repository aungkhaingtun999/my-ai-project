# ==========================================
# pages/6_Receipt.py
# ERP ENTERPRISE RECEIPT VIEWER v3
# AUTOCOMPLETE + AUTO LOAD ENGINE
# ==========================================

import streamlit as st
import pandas as pd

from database import (
    get_receipt,
    get_sale_items,
    search_receipts
)
from utils.receipt_pdf import generate_pdf
from utils.ui import show_table


def run():
    # ==========================================
    # SESSION STATE
    # ==========================================

    if "selected_receipt" not in st.session_state:
        st.session_state.selected_receipt = None

    if "receipt_data" not in st.session_state:
        st.session_state.receipt_data = None


    # ==========================================
    # PAGE HEADER
    # ==========================================

    st.title(
        "🧾 ERP Enterprise Receipt Viewer"
    )


    # ==========================================
    # SEARCH INPUT
    # ==========================================

    search_text = st.text_input(
        "🔎 Search Receipt Number",
        value=(
            st.session_state.selected_receipt
            or ""
        ),
        placeholder="Type invoice number..."
    )


    # ==========================================
    # FLOATING AUTOCOMPLETE RESULT
    # ==========================================

    if search_text:

        results = search_receipts(
            search_text
        )

        if results:

            st.caption(
                "Matching Receipts"
            )

            for r in results:

                invoice = r.get(
                    "invoice_no",
                    "-"
                )

                total = r.get(
                    "total",
                    0
                )

                date = r.get(
                    "created_at",
                    ""
                )

                label = (
                    f"🧾 {invoice}"
                    f" | "
                    f"{total:,.0f} MMK"
                    f" | "
                    f"{date}"
                )

                if st.button(
                    label,
                    key=f"receipt_{r.get('id')}"
                ):

                    st.session_state.selected_receipt = invoice

                    receipt = get_receipt(
                        invoice
                    )

                    st.session_state.receipt_data = receipt

                    st.rerun()


    # ==========================================
    # MANUAL LOAD SUPPORT
    # ==========================================

    if (
        st.session_state.receipt_data is None
        and st.session_state.selected_receipt
    ):

        receipt = get_receipt(
            st.session_state.selected_receipt
        )

        if receipt:

            st.session_state.receipt_data = receipt


    # ==========================================
    # RECEIPT DISPLAY
    # ==========================================

    receipt = st.session_state.receipt_data

    if not receipt:

        st.info(
            "🔎 Search and select a receipt to view details."
        )

        st.stop()


    # ==========================================
    # LOAD ITEMS
    # ==========================================

    sale_id = receipt.get(
        "id"
    )

    items = []

    if sale_id:

        items = get_sale_items(
            str(sale_id)
        )


    # ==========================================
    # HEADER SUMMARY
    # ==========================================

    st.divider()

    st.subheader(
        "🧾 Receipt Summary"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Invoice No",
            receipt.get(
                "invoice_no",
                "-"
            )
        )

    with c2:

        st.metric(
            "Total",
            f"{receipt.get('total', 0):,.0f} MMK"
        )

    with c3:

        st.metric(
            "Status",
            receipt.get(
                "status",
                "-"
            )
        )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Paid Amount",
            f"{receipt.get('paid_amount', 0):,.0f} MMK"
        )

    with c2:

        st.metric(
            "Change Amount",
            f"{receipt.get('change_amount', 0):,.0f} MMK"
        )

    with c3:

        st.metric(
            "Payment Method",
            receipt.get(
                "payment_method",
                "-"
            )
        )


    # ==========================================
    # ITEMS
    # ==========================================

    st.divider()

    st.subheader(
        "🛒 Sale Items"
    )

    if items:

        rows = []
        pdf_items = []

        for item in items:

            product_name = (
                f"Product #{item.get('product_id', '')}"
            )

            qty = item.get(
                "quantity",
                0
            )

            price = item.get(
                "unit_price",
                0
            )

            total = item.get(
                "total",
                0
            )

            rows.append(
                {
                    "Product": product_name,
                    "Qty": qty,
                    "Unit Price": price,
                    "Total": total
                }
            )

            # PDF FORMAT
            pdf_items.append(
                {
                    "name": product_name,
                    "qty": qty,
                    "price": price,
                    "amount": total
                }
            )

        st.session_state.pdf_items = pdf_items

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "No items found"
        )


    # ==========================================
    # FINANCIAL
    # ==========================================

    st.divider()

    st.subheader(
        "💰 Financial Details"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            "Subtotal:",
            f"{receipt.get('subtotal', 0):,.0f} MMK"
        )

        st.write(
            "Discount:",
            f"{receipt.get('discount', 0):,.0f} MMK"
        )

    with col2:

        st.write(
            "Tax:",
            f"{receipt.get('tax', 0):,.0f} MMK"
        )

        st.write(
            "Grand Total:",
            f"{receipt.get('total', 0):,.0f} MMK"
        )

    if receipt.get("created_at"):

        st.write(
            "📅 Date:",
            receipt["created_at"]
        )


    # ==========================================
    # ACTION AREA
    # ==========================================

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:

        st.button(
            "🖨 Reprint",
            disabled=True
        )

    with c2:

        if st.button("📄 PDF"):

            receipt_data = {
                "invoice_no": receipt.get("invoice_no"),
                "date": receipt.get("created_at"),
                "cashier": receipt.get(
                    "cashier",
                    "Admin"
                ),
                "items": st.session_state.get(
                    "pdf_items",
                    []
                ),
                "subtotal": receipt.get(
                    "subtotal",
                    0
                ),
                "discount": receipt.get(
                    "discount",
                    0
                ),
                "tax_amount": receipt.get(
                    "tax",
                    0
                ),
                "grand_total": receipt.get(
                    "total",
                    0
                ),
                "paid": receipt.get(
                    "paid_amount",
                    0
                ),
                "change": receipt.get(
                    "change_amount",
                    0
                )
            }

            result = generate_pdf(
                receipt_data
            )

            if result:

                pdf_bytes, filename = result

                st.download_button(
                    label="⬇️ Download Receipt PDF",
                    data=pdf_bytes,
                    file_name=f"{filename}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

    with c3:

        if st.button(
            "🆕 Clear"
        ):

            st.session_state.selected_receipt = None
            st.session_state.receipt_data = None
            st.session_state.pdf_items = None

            st.rerun()


    # ==========================================
    # EXPORT
    # ==========================================

    st.download_button(
        label="⬇ Export Receipt Data",
        data=str(receipt),
        file_name=f"{receipt.get('invoice_no', 'receipt')}.txt"
    )


if __name__ == "__main__":
    run()
