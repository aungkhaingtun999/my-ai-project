import streamlit as st
from database import db
from auth import require_login

def run():
    # 2. Authentication (Config အပြီးမှ ခေါ်ယူပါ)
    user = require_login()

    st.title("↩️ Refund System (ERP Mode)")

    # ==========================================
    # SESSION INITIALIZATION
    # ==========================================
    if "selected_sale" not in st.session_state:
        st.session_state.selected_sale = None
    if "refund_cart" not in st.session_state:
        st.session_state.refund_cart = []

    # ==========================================
    # SEARCH SALE
    # ==========================================
    input_id = st.text_input("🔍 Enter Sale ID", key="refund_sale_input")

    if st.button("Search Sale"):
        if not input_id or not input_id.isdigit():
            st.warning("Please enter a valid numeric Sale ID.")
        else:
            with st.spinner("Fetching data from ERP..."):
                try:
                    response = db().table("sales").select("*").eq("id", int(input_id)).execute()
                    
                    if not response or not hasattr(response, 'data') or not response.data:
                        st.error(f"Sale ID {input_id} not found.")
                    else:
                        sale = response.data[0]
                        
                        # Fetch Items
                        items_resp = db().table("sale_items").select("*").eq("sale_id", int(input_id)).execute()
                        sale["items"] = items_resp.data if items_resp and hasattr(items_resp, 'data') else []

                        st.session_state.selected_sale = sale
                        st.session_state.refund_cart = []
                        st.rerun()
                except Exception as e:
                    st.error(f"Database Query Error: {e}")

    # ==========================================
    # REFUND DISPLAY
    # ==========================================
    sale = st.session_state.selected_sale

    if sale:
        st.divider()
        st.subheader(f"Sale ID: {sale.get('id')}")
        st.write(f"**Original Total:** {sale.get('total', 0):,.0f} MMK")
        st.divider()

        refund_total = 0
        new_cart = []
        
        for item in sale.get("items", []):
            item_id = item.get("id")
            qty_sold = int(item.get("qty", item.get("quantity", 0)))
            price = float(item.get("selling_price", item.get("unit_price", 0)))
            
            col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
            with col1: st.write(f"Product ID: {item.get('product_id')}")
            with col2: st.write(f"Sold: {qty_sold}")
            with col3: st.write(f"Price: {price:,.0f}")
            
            with col4:
                qty = st.number_input(
                    f"Refund Qty", 
                    min_value=0, 
                    max_value=qty_sold, 
                    value=0, 
                    key=f"ref_{item_id}"
                )
                
                if qty > 0:
                    refund_total += (qty * price)
                    new_cart.append({"sale_item_id": item_id, "qty": int(qty)})

        st.session_state.refund_cart = new_cart

        st.divider()
        st.info(f"### Total Refund Amount: {refund_total:,.0f} MMK")

        reason = st.text_input("Reason for Refund")

        if st.button("Process Refund", type="primary"):
            if not st.session_state.refund_cart:
                st.error("No items selected for refund.")
            else:
                try:
                    # RPC call using authenticated user ID
                    result = db().rpc("refund_sale_rpc", {
                        "p_sale_id": int(sale["id"]),
                        "p_items": st.session_state.refund_cart,
                        "p_reason": reason,
                        "p_cashier_id": user["id"]
                    }).execute()
                    
                    res_data = result.data
                    
                    if res_data is True or (isinstance(res_data, dict) and res_data.get("success")):
                        refund_id = res_data.get("refund_id") if isinstance(res_data, dict) else None
                        st.success("✅ Refund Request Created")
                        st.info(f"Refund ID: {refund_id}\n\nStatus: PENDING\n\nWaiting for Manager Approval")
                        st.session_state.refund_cart = []
                        st.session_state.selected_sale = None
                    else:
                        st.error(f"Refund failed: {res_data}")
                except Exception as e:
                    st.error(f"RPC Error: {e}")

if __name__ == "__main__":
    # 1. Page Config ကို အပေါ်ဆုံးမှာ ထားပါ
    st.set_page_config(
        page_title="Refund System",
        layout="wide"
    )
    run()

