import streamlit as st
from supabase_client import supabase


def run():

    # ==========================================
    # AUTH CHECK
    # ==========================================

    if not st.session_state.get("user"):
        st.warning("⛔ Please log in first.")
        st.stop()


    st.title(
        "🧾 Receipt Viewer (ERP)"
    )


    # ==========================================
    # SAFE NUMBER
    # ==========================================

    def safe_float(v):

        try:
            return float(v or 0)

        except Exception:
            return 0.0



    # ==========================================
    # SEARCH
    # ==========================================

    search_query = st.text_input(
        "🔍 Search Invoice No (Example: INV-20260723)"
    )



    if search_query:


        # ======================================
        # LOAD SALES
        # ======================================

        response = (
            supabase
            .table("sales")
            .select("*")
            .ilike(
                "invoice_no",
                f"%{search_query}%"
            )
            .order(
                "id",
                desc=True
            )
            .limit(50)
            .execute()
        )


        matches = response.data or []



        if not matches:

            st.error(
                f"No invoice found: {search_query}"
            )

            st.stop()



        # ======================================
        # SELECT RECEIPT
        # ======================================


        if len(matches) > 1:


            options = {

                f"{s.get('invoice_no','-')} "
                f"(ID:{s.get('id')})":
                s

                for s in matches

            }


            selected_key = st.selectbox(

                "Select Invoice",

                list(options.keys())

            )


            sale = options[selected_key]


        else:

            sale = matches[0]

            st.success(
                f"Found: {sale.get('invoice_no')}"
            )



        # ======================================
        # LOAD ITEMS
        # ======================================


        items_response = (

            supabase
            .table("sale_items")
            .select("*")
            .eq(
                "sale_id",
                sale["id"]
            )
            .execute()

        )


        items = items_response.data or []



        # ======================================
        # SUMMARY
        # ======================================


        st.subheader(
            f"🧾 Invoice: {sale.get('invoice_no')}"
        )


        col1, col2, col3 = st.columns(3)


        total = safe_float(
            sale.get("total")
        )


        paid = safe_float(
            sale.get("paid_amount")
        )


        change = paid - total



        col1.metric(
            "Total",
            f"{total:,.0f} MMK"
        )


        col2.metric(
            "Paid",
            f"{paid:,.0f} MMK"
        )


        col3.metric(
            "Change",
            f"{change:,.0f} MMK"
        )



        st.divider()



        # ======================================
        # ITEMS
        # ======================================


        st.subheader(
            "🛒 Sale Items"
        )


        rows = []


        for item in items:


            qty = safe_float(
                item.get("quantity")
            )


            price = safe_float(
                item.get("unit_price")
            )


            amount = safe_float(
                item.get("total")
            )


            if amount == 0:

                amount = qty * price



            rows.append(

                {

                    "Product ID":
                        item.get(
                            "product_id"
                        ),


                    "Qty":
                        qty,


                    "Unit Price":
                        f"{price:,.0f}",


                    "Amount":
                        f"{amount:,.0f}"

                }

            )



        if rows:

            st.dataframe(

                rows,

                use_container_width=True,

                hide_index=True

            )


        else:

            st.warning(
                "No items found"
            )



        st.divider()



        calculated_total = sum(

            safe_float(i.get("quantity"))
            *
            safe_float(i.get("unit_price"))

            for i in items

        )


        st.info(

            f"Calculated Items Total: "
            f"{calculated_total:,.0f} MMK"

        )



if __name__ == "__main__":

    run()
