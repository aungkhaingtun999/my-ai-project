 # ==============================================================================
# pages/3_Dashboard.py
# ERP ENTERPRISE EXECUTIVE DASHBOARD v2.6 (Complete Final Release)
# ==============================================================================

from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal

import pandas as pd
import streamlit as st

from database import get_fifo_cogs, get_supabase

try:
    from postgrest.exceptions import APIError
except ImportError:
    APIError = Exception


supabase = get_supabase()


# ==============================================================================
# HELPERS
# ==============================================================================

def get_myanmar_today():
    utc_now = datetime.utcnow()
    mm_time = utc_now + timedelta(hours=6, minutes=30)
    return mm_time.date()


def safe_float(value):
    if value is None:
        return 0.0

    if isinstance(value, Decimal):
        return float(value)

    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


# ==============================================================================
# MAIN
# ==============================================================================

def run():
    st.title("📊 Executive Dashboard (ERP Level Analytics v2.6)")

    # ==========================================================================
    # FILTERS
    # ==========================================================================

    st.sidebar.header("🔍 Global Filters")

    try:
        warehouses_data = (
            supabase.table("warehouses").select("id,name").execute().data or []
        )
    except Exception:
        warehouses_data = []

    wh_map = {w["id"]: w["name"] for w in warehouses_data}
    all_wh_ids = list(wh_map.keys())

    selected_wh_name = st.sidebar.selectbox(
        "🏪 Warehouse", ["All Branches"] + list(wh_map.values())
    )

    selected_wh_id = None
    for wid, name in wh_map.items():
        if name == selected_wh_name:
            selected_wh_id = wid
            break

    # ==========================================================================
    # DATE RANGE
    # ==========================================================================

    date_filter = st.sidebar.selectbox(
        "📅 Date Range",
        ["All Time", "Today", "This Week", "This Month", "Custom Range"],
    )

    today = get_myanmar_today()
    start_date = None
    end_date = None

    if date_filter == "Today":
        start_date = today.isoformat()
        end_date = (today + timedelta(days=1)).isoformat()

    elif date_filter == "This Week":
        start_date = (today - timedelta(days=today.weekday())).isoformat()
        end_date = (today + timedelta(days=1)).isoformat()

    elif date_filter == "This Month":
        start_date = today.replace(day=1).isoformat()
        end_date = (today + timedelta(days=1)).isoformat()

    elif date_filter == "Custom Range":
        c1, c2 = st.sidebar.columns(2)
        with c1:
            custom_start = st.date_input("Start", today - timedelta(days=30))
        with c2:
            custom_end = st.date_input("End", today)

        start_date = custom_start.isoformat()
        end_date = (custom_end + timedelta(days=1)).isoformat()

    # ==========================================================================
    # SALES
    # ==========================================================================

    try:
        sales_query = supabase.table("sales").select(
            """
            id,
            total,
            grand_total,
            created_at,
            paid_amount,
            sale_status,
            refund_amount,
            warehouse_id
            """
        )

        if start_date and end_date:
            sales_query = sales_query.gte("created_at", start_date).lt(
                "created_at", end_date
            )

        sales_data = sales_query.execute().data or []

    except APIError:
        st.error("Unable to load filtered sales data")
        return

    except Exception as e:
        st.error(f"Sales loading failed: {e}")
        return

    # ==========================================================================
    # PRODUCTS
    # ==========================================================================

    products_data = (
        supabase.table("products")
        .select(
            """
            id,
            name,
            minimum_stock,
            stock
            """
        )
        .execute()
        .data
        or []
    )

    # ==========================================================================
    # SALE ITEMS
    # ==========================================================================

    try:
        sale_items_data = (
            supabase.table("sale_items")
            .select(
                """
                id,
                sale_id,
                product_id,
                quantity,
                unit_price,
                subtotal,
                discount_amount,
                tax_amount,
                line_total
                """
            )
            .execute()
            .data
            or []
        )
    except Exception:
        sale_items_data = (
            supabase.table("sale_items")
            .select(
                """
                id,
                sale_id,
                product_id,
                quantity,
                unit_price
                """
            )
            .execute()
            .data
            or []
        )

    # ==========================================================================
    # REFUND ITEMS
    # ==========================================================================

    try:
        refund_items_data = (
            supabase.table("refund_items")
            .select(
                """
                id,
                sale_item_id,
                product_id,
                quantity
                """
            )
            .execute()
            .data
            or []
        )
    except Exception:
        refund_items_data = []

    # ==========================================================================
    # INVENTORY COST TRANSACTION
    # ==========================================================================

    try:
        inv_query = supabase.table("inventory_cost_transactions").select(
            """
            sale_id,
            qty,
            total_cost,
            unit_cost,
            transaction_type,
            created_at
            """
        )

        if start_date and end_date:
            inv_query = inv_query.gte("created_at", start_date).lt(
                "created_at", end_date
            )

        inventory_tx_data = inv_query.execute().data or []
    except Exception:
        inventory_tx_data = []

    # ==========================================================================
    # WAREHOUSE STOCK
    # ==========================================================================

    warehouse_stock_data = (
        supabase.table("warehouse_stock")
        .select(
            """
            warehouse_id,
            product_id,
            qty
            """
        )
        .execute()
        .data
        or []
    )

    # ==========================================================================
    # BASIC VALIDATION
    # ==========================================================================

    if not sales_data or not products_data or not sale_items_data:
        st.info("Insufficient data available.")
        return

    # ==========================================================================
    # WAREHOUSE FILTER
    # ==========================================================================

    if selected_wh_id is not None and "warehouse_id" in sales_data[0]:
        sales_data = [
            s for s in sales_data if s.get("warehouse_id") == selected_wh_id
        ]

    valid_sale_ids = {s["id"] for s in sales_data}

    sale_items_data = [
        x for x in sale_items_data if x.get("sale_id") in valid_sale_ids
    ]
    valid_sale_item_ids = {item["id"] for item in sale_items_data}

    if refund_items_data:
        refund_items_data = [
            r for r in refund_items_data if r.get("sale_item_id") in valid_sale_item_ids
        ]

    if selected_wh_id is not None:
        warehouse_stock_data = [
            x for x in warehouse_stock_data if x.get("warehouse_id") == selected_wh_id
        ]

    # ==========================================================================
    # DATAFRAME & MAPPING SETUP
    # ==========================================================================

    df_sales = pd.DataFrame(sales_data)
    df_products = pd.DataFrame(products_data)
    df_items = pd.DataFrame(sale_items_data)

    df_refund_items = (
        pd.DataFrame(refund_items_data)
        if refund_items_data
        else pd.DataFrame(columns=["id", "sale_item_id", "product_id", "quantity"])
    )

    df_warehouse_stock = (
        pd.DataFrame(warehouse_stock_data)
        if warehouse_stock_data
        else pd.DataFrame()
    )

    try:
        df_products["id"] = df_products["id"].astype(int)
        product_map = {
            int(k): v
            for k, v in df_products.set_index("id").to_dict("index").items()
        }
    except Exception:
        product_map = df_products.set_index("id").to_dict("index")

    if not df_warehouse_stock.empty and "product_id" in df_warehouse_stock.columns:
        df_warehouse_stock["product_id"] = (
            df_warehouse_stock["product_id"].apply(safe_float).astype(int)
        )

    if not df_warehouse_stock.empty and "warehouse_id" in df_warehouse_stock.columns:
        df_warehouse_stock["warehouse_id"] = (
            df_warehouse_stock["warehouse_id"].apply(safe_float).astype(int)
        )

    sale_map = df_sales.set_index("id").to_dict(orient="index")

    if df_sales.empty:
        st.warning("No sales records found.")
        return

    # ==========================================================================
    # KPI ENGINE
    # ==========================================================================

    total_sales_col = (
        "grand_total"
        if "grand_total" in df_sales.columns
        else ("total" if "total" in df_sales.columns else None)
    )

    gross_sales = (
        df_sales[total_sales_col].apply(safe_float).sum()
        if total_sales_col
        else 0.0
    )

    total_refund = (
        df_sales["refund_amount"].apply(safe_float).sum()
        if "refund_amount" in df_sales.columns
        else 0.0
    )

    net_sales = gross_sales - total_refund
    total_orders = len(df_sales)

    # ==========================================================================
    # FIFO COGS
    # ==========================================================================

    try:
        fifo = (
            get_fifo_cogs(
                sale_ids=list(valid_sale_ids),
                start_date=start_date,
                end_date=end_date,
            )
            or {}
        )
    except TypeError:
        try:
            fifo = get_fifo_cogs(sale_ids=list(valid_sale_ids)) or {}
        except TypeError:
            fifo = get_fifo_cogs() or {}

    raw_cogs = safe_float(fifo.get("cogs", 0))
    adjusted_cogs = max(raw_cogs, 0)

    total_profit = net_sales - adjusted_cogs
    gross_margin = (total_profit / net_sales * 100) if net_sales > 0 else 0

    # ==========================================================================
    # KPI METRIC CARDS UI
    # ==========================================================================

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("💰 Net Sales", f"{net_sales:,.0f} MMK", f"Gross {gross_sales:,.0f}")
    col2.metric("🔄 Refunds", f"{total_refund:,.0f} MMK")
    col3.metric("📦 Total COGS", f"{adjusted_cogs:,.0f} MMK")
    col4.metric(
        "📈 Gross Profit",
        f"{total_profit:,.0f} MMK",
        f"{gross_margin:.1f}% Margin",
    )
    col5.metric("🧾 Total Orders", f"{total_orders:,}")

    st.divider()

    # ==========================================================================
    # COMPUTATION FOR CHARTS & TRENDS
    # ==========================================================================

    sale_revenue_map = defaultdict(float)
    if not df_items.empty:
        for _, item in df_items.iterrows():
            s_id = item.get("sale_id")
            if not s_id:
                continue
            if "line_total" in item and item.get("line_total") is not None:
                rev = safe_float(item.get("line_total"))
            else:
                unit_p = safe_float(item.get("unit_price"))
                qty = safe_float(item.get("quantity"))
                disc = safe_float(item.get("discount_amount", 0))
                tax = safe_float(item.get("tax_amount", 0))
                rev = (unit_p * qty) - disc + tax
            sale_revenue_map[s_id] += rev

    for s_id in sale_map.keys():
        if sale_revenue_map.get(s_id, 0) == 0:
            s_record = sale_map.get(s_id, {})
            sale_revenue_map[s_id] = safe_float(
                s_record.get("grand_total") or s_record.get("total")
            )

    filtered_tx_data = [
        tx for tx in inventory_tx_data if tx.get("sale_id") in valid_sale_ids
    ]
    sale_cost_map = defaultdict(float)
    for tx in filtered_tx_data:
        sale_id = tx.get("sale_id")
        if sale_id:
            tx_qty = safe_float(tx.get("qty"))
            tx_unit_cost = safe_float(tx.get("unit_cost"))
            tx_total_cost = safe_float(tx.get("total_cost")) or (tx_unit_cost * tx_qty)
            tx_type = str(tx.get("transaction_type", "SALE")).upper()
            if tx_type == "REFUND":
                sale_cost_map[sale_id] -= abs(tx_total_cost)
            else:
                sale_cost_map[sale_id] += tx_total_cost

    daily_profit = defaultdict(float)
    daily_sales = defaultdict(float)

    for sale_id, cogs_val in sale_cost_map.items():
        sale = sale_map.get(sale_id)
        if not sale:
            continue
        date_str = str(sale.get("created_at", ""))[:10]
        if not date_str:
            continue

        base_revenue = sale_revenue_map.get(sale_id, 0.0)
        refund = (
            safe_float(sale.get("refund_amount", 0))
            if "refund_amount" in sale
            else 0.0
        )
        net_revenue = base_revenue - refund

        daily_profit[date_str] += net_revenue - max(cogs_val, 0.0)
        daily_sales[date_str] += net_revenue

    # ==========================================================================
    # FINANCIAL PERFORMANCE CHARTS UI
    # ==========================================================================

    st.subheader("📈 Financial Performance Trends")

    chart_dates = sorted(set(list(daily_sales.keys()) + list(daily_profit.keys())))

    if chart_dates:
        df_sales_trend = pd.DataFrame(
            [{"date": d, "Net Sales": daily_sales[d]} for d in chart_dates]
        )

        df_profit_trend = pd.DataFrame(
            [{"date": d, "Gross Profit": daily_profit[d]} for d in chart_dates]
        )

        chart1, chart2 = st.columns(2)

        with chart1:
            st.markdown("##### 💰 Net Sales Trend")
            st.line_chart(df_sales_trend, x="date", y="Net Sales")

        with chart2:
            st.markdown("##### 📈 Gross Profit Trend")
            st.line_chart(df_profit_trend, x="date", y="Gross Profit")
    else:
        st.info("No daily performance data available.")

    st.divider()

    # ==========================================================================
    # TOP SELLING PRODUCTS UI
    # ==========================================================================

    st.subheader("🔥 Top Selling Products (Net of Refunds)")

    if not df_items.empty and "product_id" in df_items.columns:
        gross_qty = (
            df_items.groupby("product_id")["quantity"]
            .apply(lambda x: x.apply(safe_float).sum())
            .to_dict()
        )

        refunded_qty = defaultdict(float)

        if not df_refund_items.empty and "product_id" in df_refund_items.columns:
            refunded_qty = (
                df_refund_items.groupby("product_id")["quantity"]
                .apply(lambda x: x.apply(safe_float).sum())
                .to_dict()
            )

        net_products = {}

        for pid, qty in gross_qty.items():
            try:
                pid_key = int(pid)
            except:
                pid_key = pid

            net_qty = qty - refunded_qty.get(pid_key, 0)
            if net_qty > 0:
                net_products[pid_key] = net_qty

        top_products = sorted(
            net_products.items(), key=lambda x: x[1], reverse=True
        )[:5]

        if top_products:
            for pid, qty in top_products:
                product = product_map.get(pid, {})
                st.write(
                    f"✔ **{product.get('name', 'Unknown')}** — {qty:,.0f} net sold"
                )
        else:
            st.info("No product sales data.")
    else:
        st.info("No sale item records.")

    st.divider()

    # ==========================================================================
    # LOW STOCK ALERTS UI
    # ==========================================================================

    st.subheader("⚠️ Low Stock Alerts")

    if not df_warehouse_stock.empty and "warehouse_id" in df_warehouse_stock.columns:
        stock_map = (
            df_warehouse_stock.groupby(["product_id", "warehouse_id"])["qty"]
            .apply(lambda x: x.apply(safe_float).sum())
            .to_dict()
        )

        warehouse_ids = [selected_wh_id] if selected_wh_id else all_wh_ids
        low_stock = []

        for pid, product in product_map.items():
            minimum = safe_float(product.get("minimum_stock", 0))
            if minimum <= 0:
                continue

            try:
                pid_key = int(pid)
            except Exception:
                pid_key = pid

            for wid in warehouse_ids:
                try:
                    wid_key = int(wid)
                except Exception:
                    wid_key = wid

                current = safe_float(stock_map.get((pid_key, wid_key), 0))
                if current <= minimum:
                    low_stock.append((
                        product.get("name", "Unknown"),
                        wh_map.get(wid, "Unknown"),
                        current,
                        minimum,
                    ))

        if low_stock:
            for item in low_stock:
                st.error(
                    f"🏢 {item[1]} | 📦 {item[0]} → Current: {item[2]:,.0f} (Min"
                    f" {item[3]:,.0f})"
                )
        else:
            st.success("All warehouse stock levels are healthy 👍")
    else:
        st.info("No warehouse stock configuration available.")


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    run()
    
