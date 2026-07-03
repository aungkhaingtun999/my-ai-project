import streamlit as st
from database import get_supabase

supabase = get_supabase()

st.set_page_config(page_title="Refund System", layout="wide")

st.title("🔄 Refund Management System (ERP Level)")
st.caption("Handle returns safely with audit tracking")

# =========================
# SEARCH SALE
# =========================
st.subheader("🔍 Find Sale for Refund")

sale_id = st.text_input("Enter Sale ID / Invoice ID")

sale_data = None
items_data = []

if sale_id:
    sale_resp = supabase.table("sales").select("*").eq("id", sale_id).execute()
    sale_data = sale_resp.data[0] if sale_resp.data else None

    items_resp = supabase.table("sale_items").select("*").eq("sale_id", sale_id).execute()
    items_data = items_resp.data or []

# =========================
# SHOW SALE INFO
# =========================
if sale_data:

    st.success(f"Sale Found: {sale_id}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Amount", sale_data.get("total_amount", 0))
    col2.metric("Paid Amount", sale_data.get("paid_amount", 0))
    col3.metric("Status", sale_data.get("status", "completed"))

    st.divider()

    st.subheader("🧾 Items in Sale")

    refund_items = []

    for item in items_data:

        col1, col2, col3 = st.columns([4, 2, 2])

        with col1:
            st.write(f"📦 Product ID: {item['product_id']}")

        with col2:
            st.write(f"Qty: {item['quantity']}")

        with col3:
            refund_qty = st.number_input(
                "Refund Qty",
                min_value=0,
                max_value=int(item["quantity"]),
                value=0,
                key=f"refund_{item['id']}"
            )

        if refund_qty > 0:
            refund_items.append({
                "sale_item_id": item["id"],
                "product_id": item["product_id"],
                "qty": refund_qty,
                "price": item.get("price", 0)
            })

    st.divider()

    # =========================
    # REFUND SUMMARY
    # =========================
    st.subheader("💰 Refund Summary")

    refund_total = sum(i["qty"] * i["price"] for i in refund_items)

    st.write(f"Total Refund Amount: **{refund_total} MMK**")

    reason = st.text_area("Reason for Refund")

    # =========================
    # PROCESS REFUND
    # =========================
    if st.button("✅ Process Refund"):

        if not refund_items:
            st.warning("No items selected for refund")

        elif not reason:
            st.error("Please provide refund reason")

        else:
            result = supabase.table("refunds").insert({
                "sale_id": sale_id,
                "reason": reason,
                "total_refund": refund_total
            }).execute()

            if result.data:

                refund_id = result.data[0]["id"]

                # insert refund items
                for r in refund_items:
                    supabase.table("refund_items").insert({
                        "refund_id": refund_id,
                        "product_id": r["product_id"],
                        "quantity": r["qty"],
                        "price": r["price"]
                    }).execute()

                # OPTIONAL: update sale status
                supabase.table("sales").update({
                    "status": "refunded"
                }).eq("id", sale_id).execute()

                st.success("Refund processed successfully")
                st.info(f"Refund ID: {refund_id}")

                st.rerun()

else:
    if sale_id:
        st.error("Sale not found")

# =========================
# REFUND HISTORY
# =========================
st.divider()
st.subheader("📜 Refund History")

refunds = supabase.table("refunds").select("*").execute().data or []

if refunds:

    for r in refunds:

        col1, col2, col3 = st.columns([3, 3, 3])

        with col1:
            st.write(f"Refund ID: {r['id']}")

        with col2:
            st.write(f"Sale ID: {r['sale_id']}")

        with col3:
            st.write(f"Amount: {r['total_refund']} MMK")

else:
    st.info("No refund records found")