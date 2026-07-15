import streamlit as st
from supabase_client import supabase
from datetime import date, timedelta

st.set_page_config(page_title="ERP Reports", layout="wide")

st.title("📊 ERP Executive Reports (Warehouse-Based)")

# =========================
# DATE FILTER
# =========================
col1, col2, col3 = st.columns([2, 2, 6])

start_date = col1.date_input("Start Date", value=date.today())
end_date = col2.date_input("End Date", value=date.today())

# End date ကို နောက်တစ်ရက်အထိယူမှသာ ထိုနေ့က အရောင်းအားလုံးပါမည်
start_iso = start_date.isoformat()
end_iso = (end_date + timedelta(days=1)).isoformat()

# =========================
# DATA FETCH
# =========================
sales = supabase.table("sales") \
    .select("*") \
    .gte("created_at", start_iso) \
    .lt("created_at", end_iso) \
    .order("created_at", desc=True) \
    .execute().data or []

refunds = supabase.table("refunds") \
    .select("*") \
    .gte("created_at", start_iso) \
    .lt("created_at", end_iso) \
    .execute().data or []

products = supabase.table("products").select("*").execute().data or []
sale_items = supabase.table("sale_items").select("*").execute().data or []

# =========================
# WAREHOUSE STOCK
# =========================
stock_rows = supabase.table("warehouse_stock").select("*").execute().data or []
stock_map = {}
for s in stock_rows:
    pid = s["product_id"]
    stock_map[pid] = stock_map.get(pid, 0) + (s.get("qty") or 0)

# =========================
# PRE-CALC
# =========================
total_sales = sum(s["total"] for s in sales)
total_refund = sum(r["refund_amount"] for r in refunds)
net_profit = total_sales - total_refund

low_stock_items = [p for p in products if stock_map.get(p["id"], 0) <= (p.get("minimum_stock") or 0)]

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
# TABLES (FIXED: ရက်စွဲ filter ကြောင့် ပျောက်နေတာကို ပြင်ဆင်ထားသည်)
# =========================
t1, t2 = st.columns(2)

with t1:
    st.subheader("💰 Recent Sales")
    # Date filter မပါဘဲ နောက်ဆုံး အရောင်း ၁၀ ခုကို ပြပါမည်
    recent_all_sales = supabase.table("sales").select("*").order("created_at", desc=True).limit(10).execute().data or []
    st.dataframe(recent_all_sales, use_container_width=True)

with t2:
    st.subheader("↩️ Recent Refunds")
    recent_all_refunds = supabase.table("refunds").select("*").order("created_at", desc=True).limit(10).execute().data or []
    st.dataframe(recent_all_refunds, use_container_width=True)

st.success("ERP Reports Engine Fully Warehouse-Integrated 🚀")

