import streamlit as st
from supabase_client import supabase

# 🔐 MUST BE FIRST LOGIC BLOCK (IMPORTANT)
if not st.session_state.get("user"):
    st.warning("⛔ Please login first")
    st.stop()

st.title("🧾 Receipt Viewer (ERP Level)")

# =========================
# INPUT
# =========================
receipt_no = st.text_input("Enter Receipt No (e.g. RCP-1)")

# =========================
# LOAD DATA
# =========================
def safe_float(v):
    try:
        return float(v)
    except:
        return 0.0

if receipt_no:

    # 🔍 FETCH SALE HEADER
    sale = supabase.table("sales") \
        .select("*") \
        .eq("receipt_no", receipt_no) \
        .single() \
        .execute()

    if not sale.data:
        st.error("Receipt not found")
        st.stop()

    sale = sale.data

    # 🔍 FETCH ITEMS
    items = supabase.table("sale_items") \
        .select("*") \
        .eq("sale_id", sale["id"]) \
        .execute().data or []

    # =========================
    # HEADER
    # =========================
    st.subheader(f"🧾 Receipt: {receipt_no}")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total", f"{safe_float(sale.get('total')):,.2f}")
    col2.metric("Paid", f"{safe_float(sale.get('paid_amount')):,.2f}")
    col3.metric("Change", f"{safe_float(sale.get('paid_amount',0)) - safe_float(sale.get('total',0)):,.2f}")

    st.divider()

    # =========================
    # ITEMS TABLE
    # =========================
    st.subheader("📦 Items")

    table = []

    for i in items:
        qty = safe_float(i.get("quantity"))
        price = safe_float(i.get("unit_price"))
        total = qty * price

        table.append({
            "Product ID": i.get("product_id"),
            "Qty": float(qty),
            "Price": f"{price:,.2f}",
            "Line Total": f"{total:,.2f}"
        })

    st.dataframe(table, use_container_width=True)

    # =========================
    # GRAND TOTAL CHECK
    # =========================
    st.divider()

    calculated_total = sum(safe_float(i.get("quantity")) * safe_float(i.get("unit_price")) for i in items)

    st.info(f"Calculated Total: {calculated_total:,.2f}")