import streamlit as st
from supabase_client import supabase
from datetime import date, timedelta

st.set_page_config(page_title="ERP Dashboard", layout="wide")

st.title("📊 ERP Executive Dashboard")

# =========================
# DATE FILTER
# =========================
col1, col2, col3 = st.columns([2, 2, 6])

start_date = col1.date_input("Start Date", value=date.today())
end_date = col2.date_input("End Date", value=date.today())

start_iso = start_date.isoformat()
end_iso = end_date.isoformat()

# =========================
# DATA FETCH
# =========================
sales = supabase.table("sales") \
    .select("*") \
    .gte("created_at", start_iso) \
    .lte("created_at", end_iso) \
    .execute().data or []

refunds = supabase.table("refunds") \
    .select("*") \
    .gte("created_at", start_iso) \
    .lte("created_at", end_iso) \
    .execute().data or []

products = supabase.table("products").select("*").execute().data or []
sale_items = supabase.table("sale_items").select("*").execute().data or []

# =========================
# PRE-CALC
# =========================
total_sales = sum(s["total"] for s in sales)
total_refund = sum(r["refund_amount"] for r in refunds)
net_profit = total_sales - total_refund

low_stock_items = [p for p in products if p["stock"] <= p["minimum_stock"]]

# =========================
# KPI
# =========================
st.markdown("## 📌 Key Performance Indicators")

k1, k2, k3, k4 = st.columns(4)

k1.metric("💰 Revenue", f"{total_sales:,.0f}")
k2.metric("↩️ Refunds", f"{total_refund:,.0f}")
k3.metric("📦 Low Stock", len(low_stock_items))
k4.metric("📊 Net Profit", f"{net_profit:,.0f}")

st.divider()

# =========================
# AI INSIGHTS
# =========================
st.subheader("🧠 AI Insights Engine")

avg_sales = total_sales / len(sales) if sales else 0

last_3_days = date.today() - timedelta(days=3)

recent_sales = [
    s for s in sales
    if s["created_at"][:10] >= last_3_days.isoformat()
]

recent_avg = (
    sum(s["total"] for s in recent_sales) / len(recent_sales)
    if recent_sales else 0
)

if sales:
    if recent_avg < avg_sales * 0.7:
        st.error("📉 Sales Drop Alert")
    elif recent_avg > avg_sales * 1.1:
        st.success("🚀 Growth Detected")
    else:
        st.info("📊 Stable Sales")

critical_stock = [
    p for p in products
    if p["stock"] <= (p["minimum_stock"] * 1.5)
]

if critical_stock:
    st.warning(f"⚠️ {len(critical_stock)} products at risk")
else:
    st.success("📦 Stock Healthy")

product_sales = {}
for i in sale_items:
    product_sales[i["product_id"]] = product_sales.get(i["product_id"], 0) + i["quantity"]

top_list = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)

if top_list:
    st.info(f"🏆 Top Product ID {top_list[0][0]} ({top_list[0][1]} units)")

profit_margin = (net_profit / total_sales * 100) if total_sales else 0

if total_sales:
    if profit_margin < 10:
        st.error(f"💰 Low Profit Margin: {profit_margin:.2f}%")
    elif profit_margin < 30:
        st.warning(f"💰 Medium Profit Margin: {profit_margin:.2f}%")
    else:
        st.success(f"💰 Healthy Profit Margin: {profit_margin:.2f}%")

st.divider()

# =========================
# FORECAST
# =========================
st.subheader("🔮 Forecast AI")

today = date.today()
start_7 = today - timedelta(days=7)

sales_7 = [
    s for s in sales
    if s["created_at"][:10] >= start_7.isoformat()
]

daily = {}

for s in sales_7:
    day = s["created_at"][:10]
    daily[day] = daily.get(day, 0) + s["total"]

trend = [
    {"day": k, "sales": v}
    for k, v in sorted(daily.items())
]

values = list(daily.values())

if values:
    avg = sum(values) / len(values)

    growth = 0
    if len(values) > 1 and values[0] != 0:
        growth = (values[-1] - values[0]) / values[0]

    forecast = []
    for i in range(1, 8):
        forecast.append({
            "day": f"Day +{i}",
            "sales": round(avg * (1 + growth * i / 7), 2)
        })

    st.line_chart(forecast, x="day", y="sales")

    st.metric("📈 Forecast Revenue (7 Days)", f"{sum(f['sales'] for f in forecast):,.0f}")

st.divider()

# =========================
# CHARTS (FIXED)
# =========================
left, right = st.columns(2)

with left:
    st.subheader("📈 Sales Trend")

    # ✅ FIXED HERE (main bug)
    if trend:
        st.line_chart(trend, x="day", y="sales")
    else:
        st.info("No data")

with right:
    st.subheader("🏆 Top Products")

    top_data = [
        {"product": str(k), "qty": v}
        for k, v in top_list[:5]
    ]

    st.bar_chart(top_data, x="product", y="qty")

st.divider()

# =========================
# TABLES
# =========================
t1, t2 = st.columns(2)

with t1:
    st.subheader("💰 Recent Sales")
    st.dataframe(sales[-10:], use_container_width=True)

with t2:
    st.subheader("↩️ Recent Refunds")
    st.dataframe(refunds[-10:], use_container_width=True)

st.divider()

# =========================
# INVENTORY
# =========================
st.subheader("📦 Inventory Health")

col1, col2 = st.columns(2)

col1.metric("Total Products", len(products))
col2.metric("Low Stock Alerts", len(low_stock_items))

st.warning("⚠️ Low Stock Items")
st.dataframe(low_stock_items, use_container_width=True)

st.success("Dashboard Fully Loaded 🚀")
