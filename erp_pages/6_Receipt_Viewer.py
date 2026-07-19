import streamlit as st
from supabase_client import supabase

def run():
    # 🔐 MUST BE THE FIRST LOGIC BLOCK
    if not st.session_state.get("user"):
        st.warning("⛔ Please log in first.")
        st.stop()

    st.title("🧾 Receipt Viewer (ERP)")

    # =========================
    # INPUT
    # =========================
    search_query = st.text_input("🔍 Search Receipt Number (e.g., RCP or 123)")

    # =========================
    # LOAD DATA
    # =========================
    def safe_float(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    if search_query:
        # 🔍 Fetch the latest 50 sales
        response = supabase.table("sales") \
            .select("*") \
            .order("id", desc=True) \
            .limit(50) \
            .execute()

        if not response.data:
            st.error("No receipts found.")
            st.stop()

        # Search logic
        query_str = str(search_query).lower()
        matches = [s for s in response.data if query_str in str(s.get("receipt_no", "")).lower()]

        if not matches:
            st.error(f"No receipts found matching '{search_query}'.")
            st.stop()

        # Allow user to select if multiple matches are found
        selected_sale = None
        if len(matches) > 1:
            options = {f"{s['receipt_no']}": s for s in matches}
            selected_key = st.selectbox("Multiple receipts found. Please select one:", list(options.keys()))
            selected_sale = options[selected_key]
        else:
            selected_sale = matches[0]
            st.success(f"Found receipt: **{selected_sale['receipt_no']}**")

        # =========================
        # DISPLAY DATA
        # =========================
        if selected_sale:
            sale = selected_sale
            
            # 🔍 Fetch individual items for the selected sale
            items_res = supabase.table("sale_items") \
                .select("*") \
                .eq("sale_id", sale["id"]) \
                .execute()
            
            items = items_res.data or []

            # HEADER METRICS
            st.subheader(f"🧾 Receipt: {sale['receipt_no']}")
            col1, col2, col3 = st.columns(3)
            total = safe_float(sale.get('total'))
            paid = safe_float(sale.get('paid_amount'))
            
            col1.metric("Total", f"{total:,.2f}")
            col2.metric("Paid", f"{paid:,.2f}")
            col3.metric("Change", f"{paid - total:,.2f}")

            st.divider()

            # ITEMS TABLE
            st.subheader("📦 Items")
            table = []
            for i in items:
                qty = safe_float(i.get("quantity"))
                price = safe_float(i.get("unit_price"))
                table.append({
                    "Product ID": i.get("product_id"),
                    "Qty": qty,
                    "Price": f"{price:,.2f}",
                    "Line Total": f"{qty * price:,.2f}"
                })
            st.dataframe(table, use_container_width=True)

            st.divider()
            calculated_total = sum(safe_float(i.get("quantity")) * safe_float(i.get("unit_price")) for i in items)
            st.info(f"Calculated Items Total: {calculated_total:,.2f}")

if __name__ == "__main__":
    run()
    
