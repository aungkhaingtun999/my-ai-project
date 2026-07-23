# ==============================================================================
# erp_core/loaders/receipt_loader.py
# ERP ENTERPRISE RECEIPT LOADER
# ==============================================================================


from typing import Dict, Any

from ..base_repo import db, log_error



def get_receipt(
    sale_id: int
) -> Dict[str, Any]:

    """
    Load complete receipt data

    Returns:
        {
            "success": True,
            "sale": {},
            "items": []
        }
    """

    try:

        client = db()
        # ==============================================================================
# SALE ITEMS LOADER
# ==============================================================================


def get_sale_items(
    sale_id: int
):

    """
    Load items belonging to a sale
    """

    try:

        client = db()


        response = (
            client
            .table("sale_items")
            .select("*")
            .eq("sale_id", sale_id)
            .execute()
        )


        return response.data or []


    except Exception as e:

        log_error(
            f"get_sale_items error: {e}"
        )

        return []


        # ------------------------------------------
        # SALE HEADER
        # ------------------------------------------

        sale_response = (
            client
            .table("sales")
            .select("*")
            .eq("id", sale_id)
            .single()
            .execute()
        )


        sale = sale_response.data



        # ------------------------------------------
        # SALE ITEMS
        # ------------------------------------------

        items_response = (
            client
            .table("sale_items")
            .select("*")
            .eq("sale_id", sale_id)
            .execute()
        )


        items = items_response.data or []



        return {

            "success": True,

            "sale": sale,

            "items": items

        }



    except Exception as e:

        log_error(
            f"get_receipt error: {e}"
        )


        return {

            "success": False,

            "message": str(e),

            "sale": None,

            "items": []

        }
