# ==============================================================================
# pages/3_Reports.py
# ERP EXECUTIVE REPORTS v3.0
# SALES + CASHIER + PAYMENT + EXPORT ENGINE
# ==============================================================================

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from io import BytesIO

from supabase_client import supabase


st.set_page_config(
    page_title="ERP Reports v3.0",
    layout="wide"
)


st.title("📊 ERP Executive Reports v3.0")


# =====================================================
# DATE FILTER
# =====================================================

c1, c2, c3 = st.columns([2,2,6])

start_date = c1.date_input(
    "Start Date",
    value=date.today()
)

end_date = c2.date_input(
    "End Date",
    value=date.today()
)


start_iso = start_date.isoformat()
end_iso = (
    end_date + timedelta(days=1)
).isoformat()



# =====================================================
# FETCH SALES
# =====================================================

@st.cache_data(ttl=60)
def get_sales(start_iso,end_iso):

    data = (
        supabase
        .table("sales")
        .select("*")
        .gte("created_at", start_iso)
        .lt("created_at", end_iso)
        .order(
            "created_at",
            desc=True
        )
        .execute()
        .data
        or []
    )

    return data



sales = get_sales(
    start_iso,
    end_iso
)


df = pd.DataFrame(sales)



if df.empty:

    st.warning(
        "No sales data found."
    )

    st.stop()



# =====================================================
# NORMALIZE DATA
# =====================================================

for col in [
    "total",
    "total_amount",
    "discount",
    "tax",
    "subtotal",
    "paid_amount"
]:

    if col not in df.columns:
        df[col] = 0


df["created_at"] = pd.to_datetime(
    df["created_at"]
)



# =====================================================
# KPI
# =====================================================


revenue = (
    df["total"]
    .fillna(0)
    .sum()
)


discount = (
    df["discount"]
    .fillna(0)
    .sum()
)


tax = (
    df["tax"]
    .fillna(0)
    .sum()
)


bills = len(df)



k1,k2,k3,k4 = st.columns(4)


k1.metric(
    "💰 Revenue",
    f"{revenue:,.0f} MMK"
)


k2.metric(
    "🧾 Bills",
    bills
)


k3.metric(
    "🏷 Discount",
    f"{discount:,.0f}"
)


k4.metric(
    "🧮 Tax",
    f"{tax:,.0f}"
)



st.divider()



# =====================================================
# TABS
# =====================================================


tab1,tab2,tab3,tab4 = st.tabs(
[
"📈 Sales Summary",
"👨‍💼 Cashier Report",
"💳 Payment Report",
"📥 Export Center"
]
)



# =====================================================
# SALES SUMMARY
# =====================================================


with tab1:


    st.subheader(
        "Daily Sales"
    )


    daily = (
        df
        .groupby(
            df["created_at"].dt.date
        )
        ["total"]
        .sum()
        .reset_index()
    )


    st.dataframe(
        daily,
        use_container_width=True
    )



    st.subheader(
        "Monthly Sales"
    )


    monthly = (
        df
        .groupby(
            df["created_at"]
            .dt.to_period("M")
            .astype(str)
        )
        ["total"]
        .sum()
        .reset_index()
    )


    st.dataframe(
        monthly,
        use_container_width=True
    )



# =====================================================
# CASHIER REPORT
# =====================================================


with tab2:


    st.subheader(
        "👨‍💼 Cashier Performance"
    )


    cashier = (
        df
        .groupby(
            "cashier_id"
        )
        .agg(
            Bills=("id","count"),
            Sales=("total","sum")
        )
        .reset_index()
    )


    cashier["Sales"] = (
        cashier["Sales"]
        .map(
            "{:,.0f}".format
        )
    )


    st.dataframe(
        cashier,
        use_container_width=True
    )



# =====================================================
# PAYMENT REPORT
# =====================================================


with tab3:


    st.subheader(
        "💳 Payment Methods"
    )


    payment = (
        df
        .groupby(
            "payment_method"
        )
        .agg(
            Bills=("id","count"),
            Amount=("total","sum")
        )
        .reset_index()
    )


    st.dataframe(
        payment,
        use_container_width=True
    )



# =====================================================
# EXPORT CENTER
# =====================================================


with tab4:


    st.subheader(
        "📥 Export Reports"
    )


    export_df = df.copy()


    csv = export_df.to_csv(
        index=False
    ).encode(
        "utf-8"
    )


    st.download_button(
        "⬇ Download CSV",
        csv,
        "sales_report.csv",
        "text/csv"
    )



    output = BytesIO()


    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        export_df.to_excel(
            writer,
            index=False,
            sheet_name="Sales"
        )


    st.download_button(
        "⬇ Download Excel",
        output.getvalue(),
        "ERP_Sales_Report.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )



st.success(
    "ERP Reports Engine v3.0 Ready 🚀"
    )
