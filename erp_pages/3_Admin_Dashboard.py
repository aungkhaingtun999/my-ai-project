# ==============================================================================
# pages/3_Dashboard.py
# ERP ENTERPRISE ANALYTICS & DASHBOARD
# ==============================================================================

import streamlit as st
import pandas as pd
from decimal import Decimal
from datetime import datetime, timedelta

from database import (
    db,
    require_login,
    current_user,
    get_warehouses,
    get_default_warehouse_id
)
from database.utils import money, safe_float

# ------------------------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="ERP Enterprise Dashboard",
    page_icon="📈",
    layout="wide"
)

# Authentication check
require_login()
user = current_user()

st.title("📈 Enterprise Analytics Dashboard")
st.markdown("Real-time financial, inventory, and sales performance metrics.")
st.markdown("---")

# ------------------------------------------------------------------------------
# SIDEBAR FILTERS & CONTROLS
# ------------------------------------------------------------------------------
st.sidebar.header("📊 Dashboard Filters")

# Warehouse selection
warehouses = get_warehouses()
warehouse_options = [{"id": None, "name": "All Warehouses"}]
if warehouses:
    for w in warehouses:
        warehouse_options.append({"id": w.get("id"), "name": w.get("name")})

selected_wh = st.sidebar.selectbox(
    "Select Warehouse / Branch",
    options=warehouse_options,
    format_func=lambda x: x["name"]
)
warehouse_id = selected_wh["id"]

# Date range selection
date_range_option = st.sidebar.selectbox(
    "Time Period",
    ["Today", "Last 7 Days", "This Month", "Year to Date", "Custom Range"]
)

now = datetime.now()
if date_range_option == "Today":
    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = now
elif date_range_option == "Last 7 Days":
    start_date = now - timedelta(days=7)
    end_date = now
elif date_range_option == "This Month":
    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_date = now
elif date_range_option == "Year to Date":
    start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    end_date = now
else:
    col_d1, col_d2 = st.sidebar.columns(2)
    with col_d1:
        start_date = st.date_input("Start Date", now - timedelta(days=30))
    with col_d2:
        end_date = st.date_input("End Date", now)
    start_date = datetime.combine(start_date, datetime.min.time())
    end_date = datetime.combine(end_date, datetime.max.time())

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Analytics Data"):
    st.cache_data.clear()
    st.rerun()

# ------------------------------------------------------------------------------
# DATA FETCHING ENGINE (FIXED QUERY)
# ------------------------------------------------------------------------------
supabase = db()

try:
    sales_query = supabase.table("sales").select(
        """
        id,
        total,
        total_amount,
        created_at,
        paid_amount,
        sale_status,
        warehouse_id
        """
    )

    if warehouse_id:
        sales_query = sales_query.eq("warehouse_id", warehouse_id)

    if start_date and end_date:
        sales_query = sales_query.gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat())

    sales_response = sales_query.execute()
    df_sales = pd.DataFrame(sales_response.data or [])

except Exception as e:
    st.error("Unable to load filtered sales data")
    if getattr(st.secrets, "DEBUG", False):
        st.exception(e)
    df_sales = pd.DataFrame()

# ------------------------------------------------------------------------------
# METRICS COMPUTATION (KPI CARDS)
# ------------------------------------------------------------------------------
st.subheader("📌 Key Performance Indicators")

if not df_sales.empty:
    total_sales_col = (
        "total_amount"
        if "total_amount" in df_sales.columns
        else ("total" if "total" in df_sales.columns else None)
    )

    if total_sales_col:
        gross_sales = df_sales[total_sales_col].apply(safe_float).sum()
    else:
        gross_sales = 0.0

    total_transactions = len(df_sales)
    total_paid = df_sales["paid_amount"].apply(safe_float).sum() if "paid_amount" in df_sales.columns else 0.0
    
    # Refund calculation check
    total_refund = (
        df_sales["refund_amount"].apply(safe_float).sum()
        if "refund_amount" in df_sales.columns
        else 0.0
    )
else:
    gross_sales = 0.0
    total_transactions = 0
    total_paid = 0.0
    total_refund = 0.0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Gross Revenue",
        value=f"{gross_sales:,.2f} MMK",
        delta=f"{total_transactions} transactions"
    )

with col2:
    st.metric(
        label="Total Collections",
        value=f"{total_paid:,.2f} MMK"
    )

with col3:
    st.metric(
        label="Total Refunds",
        value=f"{total_refund:,.2f} MMK",
        delta_color="inverse"
    )

with col4:
    net_revenue = gross_sales - total_refund
    st.metric(
        label="Net Revenue",
        value=f"{net_revenue:,.2f} MMK"
    )

st.markdown("---")

# ------------------------------------------------------------------------------
# CHARTS & VISUAL ANALYTICS
# ------------------------------------------------------------------------------
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("📈 Sales Trend Over Time")
    if not df_sales.empty and "created_at" in df_sales.columns:
        try:
            df_sales["date"] = pd.to_datetime(df_sales["created_at"]).dt.date
            trend_col = total_sales_col if total_sales_col else "total"
            daily_sales = df_sales.groupby("date")[trend_col].sum().reset_index()
            st.line_chart(daily_sales.set_index("date"))
        except Exception:
            st.info("Insufficient timestamp detail for trend aggregation.")
    else:
        st.info("No sales data available for the selected range.")

with col_chart2:
    st.subheader("📦 Inventory Stock Health")
    try:
        inv_query = supabase.table("pos_products_view").select("name, stock, minimum_stock")
        if warehouse_id:
            inv_query = inv_query.eq("warehouse_id", warehouse_id)
        inv_data = inv_query.execute().data or []
        df_inv = pd.DataFrame(inv_data)

        if not df_inv.empty:
            low_stock_df = df_inv[df_inv["stock"] <= df_inv.get("minimum_stock", 5)]
            st.metric(label="Items Needing Restock", value=len(low_stock_df), delta_color="inverse")
            if not low_stock_df.empty:
                st.dataframe(low_stock_df[["name", "stock"]], use_container_width=True)
            else:
                st.success("All stock levels are optimal!")
        else:
            st.info("No inventory data found.")
    except Exception as e:
        st.warning("Could not fetch inventory health metrics.")

st.markdown("---")

# ------------------------------------------------------------------------------
# RECENT TRANSACTIONS TABLE
# ------------------------------------------------------------------------------
st.subheader("📋 Recent Sales Transactions")
if not df_sales.empty:
    display_cols = [c for c in ["id", "invoice_no", "total", "total_amount", "paid_amount", "sale_status", "created_at"] if c in df_sales.columns]
    st.dataframe(df_sales[display_cols].head(15), use_container_width=True)
else:
    st.info("No transaction records found matching the active filters.")
