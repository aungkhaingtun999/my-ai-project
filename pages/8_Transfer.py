# ==========================================
# pages/8_Transfer.py
# ERP ENTERPRISE WAREHOUSE TRANSFER
# PART 1
# ==========================================

import streamlit as st
from database import get_supabase
from datetime import datetime

supabase = get_supabase()

st.set_page_config(
    page_title="Warehouse Transfer",
    page_icon="🔁",
    layout="wide"
)

st.title("🔁 Enterprise Warehouse Transfer")

# ===========================
# LOAD DATA
# ===========================

try:
    warehouses = (
        supabase.table("warehouses")
        .select("*")
        .eq("is_active", True)
        .order("name")
        .execute()
        .data
        or []
    )

    products = (
        supabase.table("products")
        .select("*")
        .eq("is_active", True)
        .order("name")
        .execute()
        .data
        or []
    )

except Exception as e:
    st.error(e)
    st.stop()

if len(warehouses) < 2:
    st.error("Need at least 2 warehouses.")
    st.stop()

if not products:
    st.error("No products found.")
    st.stop()

warehouse_map = {w["name"]: w for w in warehouses}
product_map = {p["name"]: p for p in products}

# ===========================
# SESSION
# ===========================

if "transfer_success" not in st.session_state:
    st.session_state.transfer_success = False

# ===========================
# UI
# ===========================

left, right = st.columns(2)

with left:

    from_name = st.selectbox(
        "📤 From Warehouse",
        list(warehouse_map.keys())
    )

with right:

    to_options = [
        x
        for x in warehouse_map.keys()
        if x != from_name
    ]

    to_name = st.selectbox(
        "📥 To Warehouse",
        to_options
    )

product_name = st.selectbox(
    "📦 Product",
    list(product_map.keys())
)

product = product_map[product_name]

qty = st.number_input(
    "Transfer Qty",
    min_value=1,
    step=1,
    value=1
)

# ===========================
# SOURCE STOCK
# ===========================

source_stock = (
    supabase.table("warehouse_stock")
    .select("*")
    .eq(
        "warehouse_id",
        warehouse_map[from_name]["id"]
    )
    .eq(
        "product_id",
        product["id"]
    )
    .execute()
    .data
)

available = 0

if source_stock:

    stock = source_stock[0]

    available = stock.get(
        "available_qty",
        stock.get("qty", 0)
    )

st.info(f"Available Stock : {available}")

if qty > available:
    st.error("Not enough stock.")
    st.stop()
    # ===========================
# REMARKS
# ===========================

remarks = st.text_area(
    "Remarks",
    placeholder="Optional..."
)

# ===========================
# EXECUTE TRANSFER
# ===========================

if st.button("🚚 Execute Transfer", use_container_width=True):

    if qty <= 0:
        st.error("Invalid quantity.")
        st.stop()

    if available < qty:
        st.error("Insufficient stock.")
        st.stop()

    transfer_no = "TRF-" + datetime.now().strftime("%Y%m%d%H%M%S")

    try:

        # -------------------------
        # Reduce Source Stock
        # -------------------------

        new_source_qty = stock["qty"] - qty
        new_source_available = stock["available_qty"] - qty

        supabase.table("warehouse_stock").update({

            "qty": new_source_qty,
            "available_qty": new_source_available

        }).eq(
            "id",
            stock["id"]
        ).execute()

        # -------------------------
        # Destination Stock
        # -------------------------

        dest = (
            supabase.table("warehouse_stock")
            .select("*")
            .eq(
                "warehouse_id",
                warehouse_map[to_name]["id"]
            )
            .eq(
                "product_id",
                product["id"]
            )
            .execute()
            .data
        )

        if dest:

            d = dest[0]

            supabase.table("warehouse_stock").update({

                "qty": d["qty"] + qty,
                "available_qty": d["available_qty"] + qty

            }).eq(
                "id",
                d["id"]
            ).execute()

        else:

            supabase.table("warehouse_stock").insert({

                "warehouse_id": warehouse_map[to_name]["id"],
                "product_id": product["id"],
                "qty": qty,
                "reserved_qty": 0,
                "available_qty": qty,
                "minimum_stock": 0,
                "maximum_stock": 0,
                "reorder_level": 0

            }).execute()

        # -------------------------
        # Save History
        # -------------------------

        supabase.table("stock_transfers").insert({

            "transfer_no": transfer_no,
            "from_warehouse_id": warehouse_map[from_name]["id"],
            "to_warehouse_id": warehouse_map[to_name]["id"],
            "product_id": product["id"],
            "qty": qty,
            "status": "completed",
            "remarks": remarks

        }).execute()

        st.success(f"✅ Transfer Complete : {transfer_no}")

        st.balloons()

        st.rerun()

    except Exception as e:

        st.error(e)
        
