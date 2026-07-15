import streamlit as st
from supabase_client import supabase

# 🔐 MUST BE FIRST LOGIC BLOCK
if not st.session_state.get("user"):
    st.warning("⛔ Please login first")
    st.stop()

st.title("🧾 Receipt Viewer (ERP Level)")

# =========================
# INPUT (Partial Search)
# =========================
# text_input ဖြင့် အပိုင်းအစ ရိုက်နိုင်အောင် ပြင်ထားသည်
search_query = st.text_input("🔍 Search Receipt No (e.g. RCP or 123)")

# =========================
# LOAD DATA
# =========================
def safe_float(v):
    try:
        return float(v)
    except:
        return 0.0

if search_query:
    # 🔍 FETCH SALES MATCHING QUERY (Using ilike for partial matching)
    # ilike သည် case-insensitive အပိုင်းအစကို ရှာပေးသည်
    sales = supabase.table("sales") \
        .select("*") \
        .ilike("receipt_no", f"%{search_query}%") \
        .limit(10) \
        .execute()

    if not sales.data:
        st.error("No receipts found matching your search.")
        st.stop()

    # ရလာတဲ့ Receipt များထဲမှ ရွေးချယ်စေခြင်း
    selected_sale = None
    if len(sales.data) > 1:
        # များနေရင် ရွေးခိုင်းမယ်
        options = {s['receipt_no']: s for s in sales.data}
        selected_key = st.selectbox("Select a receipt:", list(options.keys()))
        selected_sale = options[selected_key]
    else:
        # တစ်ခုပဲရှိရင် အလိုလိုပြမယ်
        selected_sale = sales.data[0]
        st.write(f"Showing result for: **{selected_sale['receipt_no']}**")

    if selected_sale:
        sale = selected_sale
        
        # 🔍 FETCH ITEMS
        items_res = supabase.table("sale_items") \
            .select("*") \
            .eq("sale_id", sale["id"]) \
            .execute()
        
        items = items_res.data or []

        # =========================
        # HEADER
        # =========================
        st.subheader(f"🧾 Receipt: {sale['receipt_no']}")

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

