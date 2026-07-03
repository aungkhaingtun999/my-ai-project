import streamlit as st
from database import get_supabase
from collections import defaultdict

supabase = get_supabase()

st.title("📊 Admin Dashboard (ERP Level)")

# =========================
# DATA LOAD
# =========================
sales_resp = supabase.table("sales").select("*").execute()
products_resp = supabase.table("products").select("*").execute()
items_resp = supabase.table("sale_items").select("*").execute()

sales = sales_resp.data or []
products = products_resp.data or []
sale_items = items_resp.data or []

# =========================
# KPI METRICS
# =========================
total_sales = sum(s.get("total", 0) for s in sales)
total_orders = len(sales)

# =========================
# REAL PROFIT CALCULATION
# =========================
total_profit = 0

for item in sale_items:
    product = next((p for p in products if p["id"] == item.get("product_id")), None)
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
    product = next((p for p in products if p["id"] == item.get("product_id")), None)
    sale = next((s for s in sales if s["id"] == item.get("sale_id")), None)

    if not product or not sale:
        continue

    date = str(sale.get("created_at", "Unknown"))[:10]

    profit = (item.get("unit_price", 0) - product.get("purchase_price", 0)) * item.get("quantity", 0)
    daily_profit[date] += profit

chart_data = [
    {"date": k, "profit": v}
    for k, v in sorted(daily_profit.items())
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

product_qty = {}

for item in sale_items:
    pid = item.get("product_id")
    qty = item.get("quantity", 0)

    product_qty[pid] = product_qty.get(pid, 0) + qty

top_products = sorted(product_qty.items(), key=lambda x: x[1], reverse=True)[:5]

for pid, qty in top_products:
    product = next((p for p in products if p["id"] == pid), None)
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