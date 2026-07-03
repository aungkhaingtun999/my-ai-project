import streamlit as st
from supabase_client import supabase

st.set_page_config(page_title="Refund System", layout="wide")

st.title("↩️ Refund System (ERP Mode)")

# =========================
# SESSION INIT
# =========================
if "selected_sale" not in st.session_state:
    st.session_state.selected_sale = None

if "refund_cart" not in st.session_state:
    st.session_state.refund_cart = []

# =========================
# SEARCH SALE
# =========================
sale_id = st.text_input("🔍 Enter Sale ID")

if st.button("Search Sale"):

    if not sale_id:
        st.warning("Please enter sale ID")
    else:
        sale = supabase.table("sales") \
            .select("*") \
            .eq("id", sale_id) \
            .single() \
            .execute()

        if sale.data:
            st.session_state.selected_sale = sale.data

            items = supabase.table("sale_items") \
                .select("*") \
                .eq("sale_id", sale_id) \
                .execute()

            st.session_state.selected_sale["items"] = items.data or []

            st.success("Sale loaded successfully")
        else:
            st.error("Sale not found")

# =========================
# DISPLAY SALE
# =========================
sale = st.session_state.selected_sale

if sale:

    st.subheader(f"Sale ID: {sale['id']}")

    st.write("Total:", sale["total"])

    st.divider()

    st.subheader("Items")

    # reset refund cart
    if st.button("Reset Selection"):
        st.session_state.refund_cart = []

    for item in sale["items"]:

        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

        with col1:
            st.write(f"Product ID: {item['product_id']}")

        with col2:
            st.write(f"Qty: {item['quantity']}")

        with col3:
            st.write(f"Price: {item['unit_price']}")

        with col4:
            qty = st.number_input(
                f"Refund Qty {item['id']}",
                min_value=0,
                max_value=item["quantity"],
                key=f"qty_{item['id']}"
            )

            if qty > 0:
                st.session_state.refund_cart.append({
                    "sale_item_id": item["id"],
                    "qty": int(qty)
                })

        st.markdown("---")

    # =========================
    # REFUND SECTION
    # =========================
    st.divider()

    reason = st.text_input("Refund Reason (optional)")

    cashier_id = st.text_input("Cashier ID (optional)")

    if st.button("Process Refund"):

        if not st.session_state.refund_cart:
            st.error("No items selected for refund")

        else:
            result = supabase.rpc(
                "refund_sale_rpc",
                {
                    "p_sale_id": int(sale["id"]),
                    "p_items": st.session_state.refund_cart,
                    "p_reason": reason,
                    "p_cashier_id": int(cashier_id) if cashier_id else None
                }
            ).execute()

            if result.data and result.data.get("success"):
                st.success("Refund Completed Successfully 🎉")

                st.json(result.data)

                # reset
                st.session_state.refund_cart = []
                st.session_state.selected_sale = None

            else:
                st.error(result.data.get("error", "Refund failed"))
