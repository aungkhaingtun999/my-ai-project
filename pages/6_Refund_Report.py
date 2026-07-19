# ==================================================
# pages/6_Refund_Report.py
# ERP REFUND REPORT v2
# ==================================================

import streamlit as st
import pandas as pd
from datetime import date
import io

from database import db
from auth import require_login


# ==========================
# AUTH
# ==========================

user = require_login()


st.set_page_config(
    page_title="Refund Report",
    layout="wide"
)


st.title("📊 Refund Report v2")


# ==========================
# LOAD DATA
# ==========================

@st.cache_data(ttl=60)
def get_refund_report():

    response = (
        db()
        .table("view_refund_report")
        .select("*")
        .order("refund_date", desc=True)
        .execute()
    )

    return pd.DataFrame(response.data)


df = get_refund_report()


if df.empty:
    st.info("No refund records found.")
    st.stop()



df["refund_date"] = pd.to_datetime(
    df["refund_date"]
)



# ==========================
# FILTER
# ==========================

st.sidebar.header("🔍 Report Filter")


invoice_search = st.sidebar.text_input(
    "Invoice No"
)


cashier_filter = st.sidebar.multiselect(
    "Cashier",
    df["cashier_name"].dropna().unique()
)


warehouse_filter = st.sidebar.multiselect(
    "Warehouse",
    df["warehouse_name"].dropna().unique()
)


from_date = st.sidebar.date_input(
    "From Date",
    df["refund_date"].min().date()
)


to_date = st.sidebar.date_input(
    "To Date",
    date.today()
)



filtered = df.copy()


filtered = filtered[
    (filtered["refund_date"].dt.date >= from_date)
    &
    (filtered["refund_date"].dt.date <= to_date)
]


if invoice_search:
    filtered = filtered[
        filtered["invoice_no"]
        .str.contains(
            invoice_search,
            case=False,
            na=False
        )
    ]


if cashier_filter:
    filtered = filtered[
        filtered["cashier_name"]
        .isin(cashier_filter)
    ]


if warehouse_filter:
    filtered = filtered[
        filtered["warehouse_name"]
        .isin(warehouse_filter)
    ]



# ==========================
# KPI
# ==========================

c1,c2,c3,c4 = st.columns(4)


with c1:
    st.metric(
        "Refund Count",
        filtered["refund_id"].nunique()
    )


with c2:
    st.metric(
        "Refund Amount",
        f"{filtered['refund_amount'].sum():,.0f} MMK"
    )


with c3:
    st.metric(
        "Refund Qty",
        filtered["quantity"].sum()
    )


with c4:
    avg = 0

    if filtered["refund_id"].nunique():
        avg = (
            filtered["refund_amount"].sum()
            /
            filtered["refund_id"].nunique()
        )

    st.metric(
        "Average Refund",
        f"{avg:,.0f}"
    )



# ==========================
# CHART
# ==========================

st.divider()

st.subheader("📈 Refund By Product")


product_chart = (
    filtered
    .groupby("product_name")["quantity"]
    .sum()
    .sort_values(
        ascending=False
    )
)


st.bar_chart(product_chart)



# ==========================
# CASHIER SUMMARY
# ==========================

st.subheader("👤 Cashier Summary")


cashier_report = (
    filtered
    .groupby("cashier_name")
    .agg(
        Refund_Count=("refund_id","nunique"),
        Refund_Amount=("refund_amount","sum")
    )
    .reset_index()
)


st.dataframe(
    cashier_report,
    use_container_width=True,
    hide_index=True
)



# ==========================
# DETAIL TABLE
# ==========================

st.divider()

st.subheader("Refund Details")


columns = [
    "refund_id",
    "invoice_no",
    "refund_date",
    "product_name",
    "quantity",
    "item_total",
    "cashier_name",
    "warehouse_name",
    "reason"
]


st.dataframe(
    filtered[columns],
    use_container_width=True,
    hide_index=True
)



# ==========================
# EXPORT
# ==========================

st.divider()

st.subheader("📥 Export")


excel_buffer = io.BytesIO()


with pd.ExcelWriter(
    excel_buffer,
    engine="openpyxl"
) as writer:

    filtered.to_excel(
        writer,
        index=False,
        sheet_name="Refund_Report"
    )


st.download_button(
    label="📥 Download Excel",
    data=excel_buffer.getvalue(),
    file_name="refund_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


csv = filtered.to_csv(
    index=False
)


st.download_button(
    label="📄 Download CSV",
    data=csv,
    file_name="refund_report.csv",
    mime="text/csv"
)
