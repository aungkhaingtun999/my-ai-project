import streamlit as st
from collections import defaultdict
from database import get_supabase

supabase = get_supabase()

st.title("📊 Admin Dashboard (ERP Level Analytics)")

# =========================
# DATA LOAD
# =========================
sales = supabase.table("sales").select("*").execute().data or []
products = supabase.table("products").select("*").execute().data or []
sale_items = supabase.table("sale_items").select("*").execute().data or []

# =========================
# INDEX PRODUCTS (FAST LOOKUP)
# =========================
product_map = {p["id"]: p for p in products}

# =========================
# KPI CALCULATIONS
# =========================
total_sales = sum(s.get("total", 0) for s in sales)
total_orders = len(sales)

total_profit = 0

for item in sale_items:
    product = product_map.get(item.get("product_id"))
    if not product:
        continue

    selling = item.get("unit_price", 0)
    cost = product.get("purchase_price", 0)
    qty = item.get("quantity", 0)

    total_profit += (selling - cost) * qty

# =========================
# KPI UI
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Sales", f"{total_sales:,.0f} MMK")
col2.metric("🧾 Total Orders", total_orders)
col3.metric("📈 Real Profit", f"{total_profit:,.0f} MMK")

st.divider()

# =========================
# 📈 PROFIT CHART (DAILY)
# =========================
st.subheader("📈 Daily Profit Trend")

daily_profit = defaultdict(float)

for item in sale_items:
    product = product_map.get(item.get("product_id"))
    if not product:
        continue

    sale = next((s for s in sales if s["id"] == item.get("sale_id")), None)
    if not sale:
        continue

    date = str(sale.get("created_at", ""))[:10]

    profit = (item.get("unit_price", 0) - product.get("purchase_price", 0)) * item.get("quantity", 0)
    daily_profit[date] += profit

chart_data = [
    {"date": d, "profit": p}
    for d, p in sorted(daily_profit.items())
]

if chart_data:
    st.line_chart(chart_data, x="date", y="profit")
else:
    st.info("No profit data available yet")

st.divider()

# =========================
# 🔥 TOP SELLING PRODUCTS
# =========================
st.subheader("🔥 Top Selling Products")

product_qty = defaultdict(int)

for item in sale_items:
    pid = item.get("product_id")
    product_qty[pid] += item.get("quantity", 0)

top_products = sorted(product_qty.items(), key=lambda x: x[1], reverse=True)[:5]

for pid, qty in top_products:
    product = product_map.get(pid)
    if product:
        st.write(f"✔ {product.get('name','Unknown')} — {qty} sold")

st.divider()

# =========================
# ⚠️ LOW STOCK ALERT
# =========================
st.subheader("⚠️ Low Stock Alerts")

low_stock = [
    p for p in products
    if p.get("stock", 0) <= p.get("minimum_stock", 0)
]

if not low_stock:
    st.success("All stock levels are healthy 👍")

for p in low_stock:
    st.error(
        f"{p.get('name','Unknown')} → "
        f"Stock: {p.get('stock',0)} (Min: {p.get('minimum_stock',0)})"
    )

st.divider()

# =========================
# 🧾 RECENT SALES
# =========================
st.subheader("🧾 Recent Sales")

recent_sales = sorted(sales, key=lambda x: x.get("id", 0), reverse=True)[:10]

for s in recent_sales:
    st.write(
        f"Sale #{s.get('id')} | "
        f"Total: {s.get('total',0)} MMK | "
        f"Paid: {s.get('paid_amount',0)} | "
        f"Status: {s.get('sale_status','UNKNOWN')}"
    )
