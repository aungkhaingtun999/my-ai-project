# ==============================================================================
# erp_core/loaders/receipt_loader.py
# ERP ENTERPRISE RECEIPT LOADER
# PRODUCTION VERSION
# ==============================================================================


from typing import (
    Dict,
    Any,
    List
)


from ..base_repo import (
    db,
    log_error
)



# ==============================================================================
# SALE ITEMS
# ==============================================================================


def get_sale_items(
    sale_id: int
) -> List[Dict[str, Any]]:

    """
    Load sale_items by sale_id
    """

    try:

        client = db()


        response = (
            client
            .table("sale_items")
            .select("*")
            .eq(
                "sale_id",
                sale_id
            )
            .execute()
        )


        return response.data or []


    except Exception as e:

        log_error(
            f"get_sale_items error: {e}"
        )

        return []





# ==============================================================================
# SINGLE RECEIPT
# ==============================================================================


def get_receipt(
    sale_id: int
) -> Dict[str, Any]:

    """
    Load sales header only

    Return:

    {
        id,
        invoice_no,
        total,
        paid_amount,
        ...
    }

    """

    try:

        client = db()


        response = (
            client
            .table("sales")
            .select("*")
            .eq(
                "id",
                sale_id
            )
            .single()
            .execute()
        )


        return response.data or {}


    except Exception as e:

        log_error(
            f"get_receipt error: {e}"
        )

        return {}





# ==============================================================================
# FULL RECEIPT
# ==============================================================================


def get_full_receipt(
    receipt_key: int
) -> Dict[str, Any]:

    """
    Load receipt header + items
    """

    try:

        sale = get_receipt(
            receipt_key
        )


        if not sale:

            return {

                "success": False,

                "sale": None,

                "items": []

            }



        items = get_sale_items(
            sale.get("id")
        )


        return {

            "success": True,

            "sale": sale,

            "items": items

        }


    except Exception as e:

        log_error(
            f"get_full_receipt error: {e}"
        )


        return {

            "success": False,

            "sale": None,

            "items": []

        }





# ==============================================================================
# SEARCH RECEIPTS
# ==============================================================================


def search_receipts(
    keyword: str = ""
) -> List[Dict[str, Any]]:

    """
    Search by invoice_no
    """

    try:

        client = db()


        query = (
            client
            .table("sales")
            .select("*")
        )


        if keyword:

            if keyword.isdigit():

                query = query.or_(
                    f"id.eq.{keyword},"
                    f"invoice_no.ilike.%{keyword}%"
                )

            else:

                query = query.ilike(
                    "invoice_no",
                    f"%{keyword}%"
                )



        response = (
            query
            .order(
                "created_at",
                desc=True
            )
            .execute()
        )


        return response.data or []



    except Exception as e:


        log_error(
            f"search_receipts error: {e}"
        )


        return []
