# ==================================================
# pages/6_Refund_Report.py
# ERP REFUND REPORT v1
# ==================================================

import streamlit as st
import pandas as pd
from datetime import date

from database import db
from auth import require_login


# ==========================
# AUTH
# ==========================

user = require_login()


# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="Refund Report",
    layout="wide"
)


st.title("📊 Refund Report")


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



# ==========================
# FILTER AREA
# ==========================

st.sidebar.header("🔍 Filters")


invoice_search = st.sidebar.text_input(
    "Invoice No"
)


cashier_filter = st.sidebar.multiselect(
    "Cashier",
    options=df["cashier_name"].dropna().unique()
)


warehouse_filter = st.sidebar.multiselect(
    "Warehouse",
    options=df["warehouse_name"].dropna().unique()
)


# Date Filter

df["refund_date"] = pd.to_datetime(df["refund_date"])


from_date = st.sidebar.date_input(
    "From Date",
    value=df["refund_date"].min().date()
)


to_date = st.sidebar.date_input(
    "To Date",
    value=date.today()
)



# Apply filters

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
        filtered["cashier_name"].isin(cashier_filter)
    ]


if warehouse_filter:
    filtered = filtered[
        filtered["warehouse_name"].isin(warehouse_filter)
    ]



# ==========================
# KPI
# ==========================

col1, col2, col3 = st.columns(3)


with col1:
    st.metric(
        "Refund Transactions",
        filtered["refund_id"].nunique()
    )


with col2:
    st.metric(
        "Refund Amount",
        f"{filtered['refund_amount'].sum():,.0f} MMK"
    )


with col3:
    st.metric(
        "Refund Items",
        filtered["quantity"].sum()
    )



# ==========================
# TABLE
# ==========================

st.divider()

st.subheader("Refund Details")


show_columns = [
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
    filtered[show_columns],
    use_container_width=True,
    hide_index=True
)