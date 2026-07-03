import streamlit as st
import pandas as pd
from database import get_supabase

supabase = get_supabase()

st.set_page_config(page_title="Reports", layout="wide")
st.title("📊 POS Reports (Synced with Checkout RPC)")

# =========================
# LOAD DATA (SOURCE OF TRUTH)
# =========================
sales = supabase.table("sales").select("*").execute().data or []
items = supabase.table("sale_items").select("*").execute().data or []
products = supabase.table("products").select("*").execute().data or []

sales_df = pd.DataFrame(sales)
items_df = pd.DataFrame(items)
products_df = pd.DataFrame(products)

if sales_df.empty:
    st.warning("No sales found")
    st.stop()

# =========================
# DATE HANDLING
# =========================
sales_df["created_at"] = pd.to_datetime(sales_df["created_at"])

# =========================
# FILTER
# =========================
st.sidebar.header("Filters")

start = st.sidebar.date_input("Start", sales_df["created_at"].min().date())
end = st.sidebar.date_input("End", sales_df["created_at"].max().date())

sales_df = sales_df[
    (sales_df["created_at"].dt.date >= start) &
    (sales_df["created_at"].dt.date <= end)
]

# =========================
# KPI (BASED ON SALES TABLE ONLY)
# =========================
total_sales = sales_df["total_amount"].sum()
total_orders = sales_df["id"].nunique()
avg_sale = total_sales / total_orders if total_orders else 0

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Sales", f"{total_sales:,.0f}")
col2.metric("🧾 Orders", f"{total_orders}")
col3.metric("📊 Avg Order", f"{avg_sale:,.0f}")

st.divider()

# =========================
# DAILY SALES TREND
# =========================
daily = sales_df.groupby(sales_df["created_at"].dt.date)["total_amount"].sum()
st.subheader("📈 Daily Sales")
st.line_chart(daily)

# =========================
# TOP PRODUCTS (FROM sale_items ONLY)
# =========================
st.subheader("🏆 Top Products")

if not items_df.empty:
    top = items_df.groupby("product_id")["qty"].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top)
else:
    st.info("No item data")

# =========================
# RECEIPT VIEW
# =========================
st.subheader("🧾 Recent Transactions")

st.dataframe(
    sales_df.sort_values("created_at", ascending=False),
    use_container_width=True
)