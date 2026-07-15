import streamlit as st
from supabase_client import supabase

# 🔐 MUST BE FIRST LOGIC BLOCK
if not st.session_state.get("user"):
    st.warning("⛔ Please login first")
    st.stop()

st.title("🧾 Receipt Viewer (ERP Level)")

# =========================
# INPUT
# =========================
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
    # 🔍 FETCH LATEST 50 SALES (Database ပေါ်မှာ မဟုတ်ဘဲ Python ဘက်မှာ ရှာမယ်)
    # limit(50) ထည့်ထားခြင်းဖြင့် App မလေးအောင် လုပ်ထားပါသည်
    response = supabase.table("sales") \
        .select("*") \
        .order("id", desc=True) \
        .limit(50) \
        .execute()

    if not response.data:
        st.error("No receipts found.")
        st.stop()

    # Python ဘက်မှ အပိုင်းအစကို ရှာဖွေခြင်း (String သို့မဟုတ် Integer မရွေး ရှာနိုင်အောင်)
    query_str = str(search_query).lower()
    matches = [s for s in response.data if query_str in str(s.get("receipt_no", "")).lower()]

    if not matches:
        st.error(f"No receipts found matching '{search_query}'.")
        st.stop()

    # ရလာတဲ့ Receipt များထဲမှ ရွေးချယ်စေခြင်း
    selected_sale = None
    if len(matches) > 1:
        options = {f"{s['receipt_no']}": s for s in matches}
        selected_key = st.selectbox("Select a receipt:", list(options.keys()))
        selected_sale = options[selected_key]
    else:
        selected_sale = matches[0]
        st.success(f"Found: **{selected_sale['receipt_no']}**")

    # =========================
    # DISPLAY DATA
    # =========================
    if selected_sale:
        sale = selected_sale
        
        # 🔍 FETCH ITEMS
        items_res = supabase.table("sale_items") \
            .select("*") \
            .eq("sale_id", sale["id"]) \
            .execute()
        
        items = items_res.data or []

        # HEADER
        st.subheader(f"🧾 Receipt: {sale['receipt_no']}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total", f"{safe_float(sale.get('total')):,.2f}")
        col2.metric("Paid", f"{safe_float(sale.get('paid_amount')):,.2f}")
        col3.metric("Change", f"{safe_float(sale.get('paid_amount',0)) - safe_float(sale.get('total',0)):,.2f}")

        st.divider()

        # ITEMS TABLE
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

        st.divider()
        calculated_total = sum(safe_float(i.get("quantity")) * safe_float(i.get("unit_price")) for i in items)
        st.info(f"Calculated Total: {calculated_total:,.2f}")
        
