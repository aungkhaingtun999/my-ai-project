# ==============================================================================
# pages/5_Refund.py
# ERP ENTERPRISE REFUND SYSTEM v4.6
# SALE ITEM SCHEMA COMPATIBLE
# ==============================================================================

import streamlit as st
from database import supabase


st.set_page_config(
    page_title="Refund System",
    layout="wide"
)


st.title("↩️ Refund System (ERP Mode)")


# ==========================================
# SESSION
# ==========================================

if "selected_sale" not in st.session_state:
    st.session_state.selected_sale = None

if "refund_cart" not in st.session_state:
    st.session_state.refund_cart = []


# ==========================================
# SEARCH SALE
# ==========================================

sale_id = st.text_input("🔍 Enter Sale ID")


if st.button("Search Sale"):

    if not sale_id:
        st.warning("Enter Sale ID")

    else:

        try:

            sale_resp = (
                supabase
                .table("sales")
                .select("*")
                .eq("id", sale_id)
                .single()
                .execute()
            )


            if sale_resp.data:

                sale = sale_resp.data


                items_resp = (
                    supabase
                    .table("sale_items")
                    .select("*")
                    .eq("sale_id", sale_id)
                    .execute()
                )


                sale["items"] = items_resp.data or []


                st.session_state.selected_sale = sale
                st.session_state.refund_cart = []


                st.success(
                    "Sale loaded successfully"
                )

                st.rerun()


            else:
                st.error("Sale not found")


        except Exception as e:

            st.error(
                f"Search Error: {e}"
            )



# ==========================================
# REFUND DISPLAY
# ==========================================

sale = st.session_state.selected_sale


if sale:


    st.subheader(
        f"Sale ID : {sale['id']}"
    )


    st.write(
        "Original Total:",
        f"{sale.get('total',0):,.0f} MMK"
    )


    st.divider()


    refund_total = 0


    for item in sale.get("items", []):


        qty_sold = int(
            item.get(
                "qty",
                item.get("quantity",0)
            )
        )


        price = float(
            item.get(
                "selling_price",
                item.get("unit_price",0)
            )
        )


        col1,col2,col3,col4 = st.columns(
            [3,2,2,3]
        )


        with col1:
            st.write(
                f"Product ID: {item.get('product_id')}"
            )


        with col2:
            st.write(
                f"Sold Qty: {qty_sold}"
            )


        with col3:
            st.write(
                f"Price: {price:,.0f}"
            )


        with col4:


            qty = st.number_input(

                f"Refund Qty {item['id']}",

                min_value=0,

                max_value=qty_sold,

                key=f"refund_{item['id']}"

            )


            existing = next(
                (
                    x for x in st.session_state.refund_cart
                    if x["sale_item_id"] == item["id"]
                ),
                None
            )


            if qty > 0:


                refund_amount = qty * price

                refund_total += refund_amount


                if existing:

                    existing["qty"] = int(qty)


                else:

                    st.session_state.refund_cart.append(
                        {
                            "sale_item_id":item["id"],
                            "qty":int(qty)
                        }
                    )


            elif existing:


                st.session_state.refund_cart.remove(
                    existing
                )



    st.divider()


    st.info(
        f"Refund Amount : {refund_total:,.0f} MMK"
    )



    reason = st.text_input(
        "Refund Reason"
    )


    cashier_id = st.session_state.get(
        "user_id"
    )



    if st.button(
        "Process Refund",
        type="primary"
    ):


        if not st.session_state.refund_cart:

            st.error(
                "No items selected"
            )


        else:

            try:

                result = (
                    supabase
                    .rpc(
                        "refund_sale_rpc",
                        {
                            "p_sale_id":int(sale["id"]),
                            "p_items":st.session_state.refund_cart,
                            "p_reason":reason,
                            "p_cashier_id":cashier_id
                        }
                    )
                    .execute()
                )


                data = result.data


                if (
                    isinstance(data,dict)
                    and data.get("success")
                ):

                    st.success(
                        "Refund Completed Successfully 🎉"
                    )

                    st.json(data)


                    st.session_state.refund_cart=[]
                    st.session_state.selected_sale=None


                else:

                    st.error(
                        f"Refund Failed: {data}"
                    )


            except Exception as e:

                st.error(
                    f"RPC Error: {e}"
                )
