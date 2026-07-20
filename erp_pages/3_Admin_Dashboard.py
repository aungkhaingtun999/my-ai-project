# ==============================================================================
# pages/3_Dashboard.py
# ERP ENTERPRISE EXECUTIVE DASHBOARD v2.6
# PART 1/3
# Production Analytics + Payment Analytics Foundation
# ==============================================================================

from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal

import pandas as pd
import streamlit as st


# ==============================================================================
# DATABASE IMPORT
# ==============================================================================

from database import get_supabase, get_fifo_cogs


try:
    from postgrest.exceptions import APIError
except ImportError:
    APIError = Exception


supabase = get_supabase()


# ==============================================================================
# HELPERS
# ==============================================================================

def get_myanmar_today():
    """
    Myanmar timezone (+06:30)
    Avoid server timezone dependency
    """
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

    st.title(
        "📊 Executive Dashboard "
        "(ERP Enterprise Analytics v2.6)"
    )


    # ==========================================================================
    # GLOBAL FILTERS
    # ==========================================================================

    st.sidebar.header(
        "🔍 Global Filters & Ranges"
    )


    # --------------------------------------------------------------------------
    # Warehouse Filter
    # --------------------------------------------------------------------------

    try:

        warehouses_data = (
            supabase
            .table("warehouses")
            .select(
                "id,name"
            )
            .execute()
            .data
            or []
        )

    except Exception:

        warehouses_data = []


    wh_map = {
        w["id"]: w["name"]
        for w in warehouses_data
    }


    all_wh_ids = [
        w["id"]
        for w in warehouses_data
    ]


    selected_wh_name = st.sidebar.selectbox(
        "🏪 Select Branch / Warehouse",
        [
            "All Branches"
        ]
        +
        list(wh_map.values())
    )


    selected_wh_id = None


    if selected_wh_name != "All Branches":

        for wid, name in wh_map.items():

            if name == selected_wh_name:
                selected_wh_id = wid
                break



    # --------------------------------------------------------------------------
    # Date Filter
    # --------------------------------------------------------------------------

    date_filter = st.sidebar.selectbox(
        "📅 Date Range",
        [
            "All Time",
            "Today",
            "This Week",
            "This Month",
            "Custom Range"
        ]
    )


    today = get_myanmar_today()


    start_date = None
    end_date = None



    if date_filter == "Today":

        start_date = today.isoformat()

        end_date = (
            today
            +
            timedelta(days=1)
        ).isoformat()



    elif date_filter == "This Week":

        start_date = (
            today
            -
            timedelta(days=today.weekday())
        ).isoformat()


        end_date = (
            today
            +
            timedelta(days=1)
        ).isoformat()



    elif date_filter == "This Month":

        start_date = (
            today.replace(day=1)
        ).isoformat()


        end_date = (
            today
            +
            timedelta(days=1)
        ).isoformat()



    elif date_filter == "Custom Range":

        c1, c2 = st.sidebar.columns(2)


        with c1:

            custom_start = st.date_input(
                "Start Date",
                today - timedelta(days=30)
            )


        with c2:

            custom_end = st.date_input(
                "End Date",
                today
            )


        start_date = custom_start.isoformat()

        end_date = (
            custom_end
            +
            timedelta(days=1)
        ).isoformat()



    # ==========================================================================
    # SALES QUERY
    # ==========================================================================

    try:

        sales_query = (
            supabase
            .table("sales")
            .select(
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
        )


        # IMPORTANT:
        # Never remove date filter during error handling

        if start_date and end_date:

            sales_query = (
                sales_query
                .gte(
                    "created_at",
                    start_date
                )
                .lt(
                    "created_at",
                    end_date
                )
            )


        sales_data = (
            sales_query
            .execute()
            .data
            or []
        )


    except APIError:


        st.error(
            "❌ Unable to load filtered sales data."
        )

        return


    except Exception as e:


        st.error(
            f"❌ Sales loading failed: {e}"
        )

        return



    # ==========================================================================
    # PRODUCTS
    # ==========================================================================


    products_data = (

        supabase
        .table("products")
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

            supabase
            .table("sale_items")
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

            supabase
            .table("sale_items")
            .select(
                """
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
    # REFUNDS
    # ==========================================================================


    try:

        refund_items_data = (

            supabase
            .table("refund_items")
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
    # INVENTORY COST TRANSACTIONS
    # FIX: REAL DATE FILTER
    # ==========================================================================


    try:

        inv_tx_query = (

            supabase
            .table(
                "inventory_cost_transactions"
            )
            .select(
                """
                sale_id,
                qty,
                total_cost,
                unit_cost,
                transaction_type,
                created_at
                """
            )

        )


        if start_date and end_date:


            inv_tx_query = (

                inv_tx_query
                .gte(
                    "created_at",
                    start_date
                )
                .lt(
                    "created_at",
                    end_date
                )

            )


        inventory_tx_data = (

            inv_tx_query
            .execute()
            .data

            or []

        )


    except Exception:


        inventory_tx_data = []



    # ==========================================================================
    # WAREHOUSE STOCK
    # ==========================================================================


    warehouse_stock_data = (

        supabase
        .table("warehouse_stock")
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
# ==============================================================================
# PART 2/3
# DATA PROCESSING + KPI + PAYMENT ANALYTICS + CHART ENGINE
# ==============================================================================


    # ==========================================================================
    # DATA VALIDATION
    # ==========================================================================

    if (
        not sales_data
        or not products_data
        or not sale_items_data
    ):

        st.info(
            "Insufficient data available to render dashboard."
        )

        return



    # ==========================================================================
    # WAREHOUSE FILTER
    # ==========================================================================


    if (
        selected_wh_id is not None
        and "warehouse_id" in sales_data[0]
    ):

        sales_data = [

            s for s in sales_data

            if s.get(
                "warehouse_id"
            )
            ==
            selected_wh_id

        ]



    valid_sale_ids = {

        s["id"]

        for s in sales_data

    }



    sale_items_data = [

        item

        for item in sale_items_data

        if item.get(
            "sale_id"
        )
        in valid_sale_ids

    ]



    valid_sale_item_ids = {

        item.get(
            "id"
        )

        for item in sale_items_data

    }



    if refund_items_data:


        refund_items_data = [

            r

            for r in refund_items_data

            if r.get(
                "sale_item_id"
            )
            in valid_sale_item_ids

        ]



    if selected_wh_id:


        warehouse_stock_data = [

            x

            for x in warehouse_stock_data

            if x.get(
                "warehouse_id"
            )
            ==
            selected_wh_id

        ]



    # ==========================================================================
    # DATAFRAME SETUP
    # ==========================================================================


    df_sales = pd.DataFrame(
        sales_data
    )


    df_products = pd.DataFrame(
        products_data
    )


    df_items = pd.DataFrame(
        sale_items_data
    )


    df_refund_items = (

        pd.DataFrame(
            refund_items_data
        )

        if refund_items_data

        else

        pd.DataFrame(
            columns=[
                "id",
                "sale_item_id",
                "product_id",
                "quantity"
            ]
        )

    )


    df_warehouse_stock = (

        pd.DataFrame(
            warehouse_stock_data
        )

        if warehouse_stock_data

        else

        pd.DataFrame()

    )



    # Product Mapping

    df_products["id"] = (

        df_products["id"]
        .astype(int)

    )


    product_map = (

        df_products
        .set_index(
            "id"
        )
        .to_dict(
            orient="index"
        )

    )


    sale_map = (

        df_sales
        .set_index(
            "id"
        )
        .to_dict(
            orient="index"
        )

    )



    if df_sales.empty:

        st.warning(
            "No sales records found."
        )

        return



    # ==========================================================================
    # KPI CALCULATION
    # ==========================================================================


    total_sales_col = (

        "grand_total"

        if "grand_total"
        in df_sales.columns

        else

        "total"

        if "total"
        in df_sales.columns

        else

        None

    )



    gross_sales = (

        df_sales[total_sales_col]
        .apply(
            safe_float
        )
        .sum()

        if total_sales_col

        else

        0

    )



    total_refund = (

        df_sales["refund_amount"]
        .apply(
            safe_float
        )
        .sum()

        if "refund_amount"
        in df_sales.columns

        else

        0

    )



    net_sales = (

        gross_sales

        -
        
        total_refund

    )


    total_orders = len(
        df_sales
    )



    # ==========================================================================
    # FIFO COGS ACCOUNTING SAFETY
    # ==========================================================================


    try:


        fifo = (

            get_fifo_cogs(

                sale_ids=list(
                    valid_sale_ids
                ),

                start_date=start_date,

                end_date=end_date

            )

            or {}

        )


    except TypeError:


        fifo = (

            get_fifo_cogs()

            or {}

        )



    raw_cogs = safe_float(

        fifo.get(
            "cogs",
            0
        )

    )


    # Dashboard display safety

    adjusted_cogs = max(
        raw_cogs,
        0
    )



    total_profit = (

        net_sales

        -
        
        adjusted_cogs

    )



    gross_margin = (

        total_profit
        /
        net_sales
        *
        100

        if net_sales > 0

        else

        0

    )



    # ==========================================================================
    # PAYMENT ANALYTICS
    # ==========================================================================


    payment_summary = defaultdict(float)


    try:


        payments_data = (

            supabase
            .table(
                "payments"
            )
            .select(
                """
                sale_id,
                method,
                amount
                """
            )
            .execute()
            .data

            or []

        )



        for p in payments_data:


            if p.get(
                "sale_id"
            ) in valid_sale_ids:


                payment_summary[
                    str(
                        p.get(
                            "method",
                            "UNKNOWN"
                        )
                    ).upper()

                ] += safe_float(
                    p.get(
                        "amount"
                    )
                )


    except Exception:


        payments_data = []



    # ==========================================================================
    # KPI CARDS
    # ==========================================================================


    c1,c2,c3,c4,c5 = st.columns(5)



    c1.metric(
        "💰 Net Sales",
        f"{net_sales:,.0f} MMK"
    )


    c2.metric(
        "🔄 Refunds",
        f"{total_refund:,.0f} MMK"
    )


    c3.metric(
        "📦 FIFO COGS",
        f"{adjusted_cogs:,.0f} MMK"
    )


    c4.metric(
        "📈 Gross Profit",
        f"{total_profit:,.0f} MMK",
        f"{gross_margin:.1f}%"
    )


    c5.metric(
        "🧾 Orders",
        f"{total_orders:,}"
    )



    st.divider()



    # ==========================================================================
    # PAYMENT KPI
    # ==========================================================================


    st.subheader(
        "💳 Payment Analytics"
    )


    pc1,pc2,pc3,pc4 = st.columns(4)


    pc1.metric(
        "💵 Cash",
        f"{payment_summary.get('CASH',0):,.0f}"
    )


    pc2.metric(
        "💳 Card",
        f"{payment_summary.get('CARD',0):,.0f}"
    )


    pc3.metric(
        "📱 Mobile",
        f"{payment_summary.get('MOBILE',0):,.0f}"
    )


    pc4.metric(
        "🏦 Credit",
        f"{payment_summary.get('CREDIT',0):,.0f}"
    )



    st.divider()



    # ==========================================================================
    # REVENUE MAP FOR CHART
    # ==========================================================================


    sale_revenue_map = defaultdict(float)


    for _, item in df_items.iterrows():


        sale_id = item.get(
            "sale_id"
        )


        if not sale_id:

            continue



        if item.get(
            "line_total"
        ) is not None:


            revenue = safe_float(
                item.get(
                    "line_total"
                )
            )


        elif item.get(
            "subtotal"
        ) is not None:


            revenue = (

                safe_float(
                    item.get(
                        "subtotal"
                    )
                )

                -

                safe_float(
                    item.get(
                        "discount_amount",
                        0
                    )
                )

                +

                safe_float(
                    item.get(
                        "tax_amount",
                        0
                    )
                )

            )


        else:


            revenue = (

                safe_float(
                    item.get(
                        "unit_price"
                    )
                )

                *
                safe_float(
                    item.get(
                        "quantity"
                    )
                )

            )


        sale_revenue_map[
            sale_id
        ] += revenue
# ==============================================================================
# PART 3/3
# TOP PRODUCTS + LOW STOCK + RECENT SALES + END
# ==============================================================================


    st.divider()


    # ==========================================================================
    # TOP SELLING PRODUCTS (NET OF REFUND)
    # ==========================================================================

    st.subheader(
        "🔥 Top Selling Products (Net)"
    )


    if not df_items.empty and "product_id" in df_items.columns:


        gross_qty = (

            df_items
            .groupby("product_id")["quantity"]
            .apply(
                lambda x:
                x.apply(safe_float).sum()
            )
            .to_dict()

        )


        refunded_qty = defaultdict(float)



        if (
            not df_refund_items.empty
            and "product_id" in df_refund_items.columns
        ):


            refunded_qty = (

                df_refund_items
                .groupby("product_id")["quantity"]
                .apply(
        
