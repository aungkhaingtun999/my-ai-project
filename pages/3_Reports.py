# ==============================================================================
# pages/3_Reports.py
# ERP EXECUTIVE REPORTS v3.2 - STABLE EXPORT ENGINE (FIXED)
# ==============================================================================

import streamlit as st
import pandas as pd
import json
from datetime import date, timedelta
from io import BytesIO
from database import db 

st.set_page_config(page_title="ERP Reports v3.2", layout="wide")

st.title("📊 ERP Executive Reports v3.2")

# =====================================================
# DATE FILTER
# =====================================================
c1, c2, c3 = st.columns([2, 2, 6])
start_date = c1.date_input("Start Date", value=date.today())
end_date = c2.date_input("End Date", value=date.today())

start_iso = start_date.isoformat()
end_iso = (end_date + timedelta(days=1)).isoformat()

# =====================================================
# FETCH SALES
# =====================================================
@st.cache_data(ttl=60)
def get_sales(start_iso, end_iso):
    try:
        return db().table("sales").select("*").gte("created_at", start_iso).lt("created_at", end_iso).order("created_at", desc=True).execute().data or []
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

sales = get_sales(start_iso, end_iso)
df = pd.DataFrame(sales)

if df.empty:
    st.warning("No sales data found.")
    st.stop()

# =====================================================
# NORMALIZE DATA
# =====================================================
numeric_cols = ["total", "total_amount", "discount", "tax", "subtotal", "paid_amount"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col].fillna(0))
    else:
        df[col] = 0

df["created_at"] = pd.to_datetime(df["created_at"])

# =====================================================
# KPI
# =====================================================
revenue = df["total"].sum()
discount = df["discount"].sum()
tax = df["tax"].sum()
bills = len(df)

k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Revenue", f"{revenue:,.0f} MMK")
k2.metric("🧾 Bills", bills)
k3.metric("🏷 Discount", f"{discount:,.0f}")
k4.metric("🧮 Tax", f"{tax:,.0f}")

st.divider()

# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3, tab4 = st.tabs(["📈 Sales Summary", "👨‍💼 Cashier Report", "💳 Payment Report", "📥 Export Center"])

with tab1:
    st.subheader("Daily Sales")
    daily = df.groupby(df["created_at"].dt.date)["total"].sum().reset_index()
    st.dataframe(daily, use_container_width=True)

    st.subheader("Monthly Sales")
    monthly = df.groupby(df["created_at"].dt.to_period("M").astype(str))["total"].sum().reset_index()
    st.dataframe(monthly, use_container_width=True)

with tab2:
    st.subheader("👨‍💼 Cashier Performance")
    cashier = df.groupby("cashier_id").agg(Bills=("id", "count"), Sales=("total", "sum")).reset_index()
    st.dataframe(cashier, use_container_width=True)

with tab3:
    st.subheader("💳 Payment Methods")
    payment = df.groupby("payment_method").agg(Bills=("id", "count"), Amount=("total", "sum")).reset_index()
    st.dataframe(payment, use_container_width=True)

with tab4:
    st.subheader("📥 Export Reports")
    
    # --- DATA CLEANING FOR EXCEL ---
    export_df = df.copy()
    
    # 1. Complex Objects (Dicts/Lists) များကို JSON String သို့ပြောင်းခြင်း
    for col in export_df.columns:
        if export_df[col].dtype == 'object':
            export_df[col] = export_df[col].apply(
                lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x
            )
            
    # 2. Datetime များကို string သို့ ပြောင်းပါ
    for col in export_df.select_dtypes(include=['datetime64', 'timedelta64']).columns:
        export_df[col] = export_df[col].astype(str)
        
    # 3. NaN တန်ဖိုးများကို empty string သို့ ပြောင်းပါ
    export_df = export_df.fillna('')

    # CSV Download
    csv = export_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Download CSV", csv, "sales_report.csv", "text/csv")

    # Excel Download
    try:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            export_df.to_excel(writer, index=False, sheet_name="Sales")
        
        st.download_button(
            "⬇ Download Excel",
            output.getvalue(),
            "ERP_Sales_Report.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"Excel Export Error: {e}")

st.success("ERP Reports Engine v3.2 Ready 🚀")
    
