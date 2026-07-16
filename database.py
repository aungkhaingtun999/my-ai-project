# ==========================================
# RECEIPT SEARCH (PARTIAL)
# ==========================================

def get_receipts_search(
    keyword: str
):

    try:

        if not keyword:

            return []


        return (

            supabase
            .table("sales")
            .select(
                """
                id,
                invoice_no,
                total,
                paid_amount,
                change_amount,
                payment_method,
                sale_status,
                status,
                created_at
                """
            )
            .ilike(
                "invoice_no",
                f"%{keyword.strip()}%"
            )
            .order(
                "created_at",
                desc=True
            )
            .limit(50)
            .execute()
            .data

            or []

        )


    except Exception as e:

        log_error(e)

        return []
