# ==============================================================================
# erp_core/loaders/receipt_loader.py
# ERP ENTERPRISE RECEIPT LOADER v1.0
# ==============================================================================


from typing import Dict, Any, List

from ..base_repo import (
    db,
    log_error
)



# ==============================================================================
# SALE ITEMS
# ==============================================================================

def get_sale_items(sale_id:int):

    try:

        response = (
            db()
            .table("sale_items")
            .select("""
                id,
                sale_id,
                product_id,
                product_name,
                quantity,
                unit_price,
                discount,
                total
            """)
            .eq(
                "sale_id",
                sale_id
            )
            .execute()
        )


        items = response.data or []

        for item in items:
            item["name"] = item.get("product_name", "")

            # receipt compatibility

            item["product_name"] = (
                item.get("product_name")
                or
                f"Product #{item.get('product_id')}"
            )

            item["qty"] = item.get(
                "quantity",
                0
            )


        return items


    except Exception as e:

        log_error(
            f"get_sale_items error : {e}"
        )

        return []

# ==============================================================================
# GET RECEIPT
# ==============================================================================

def get_receipt(
    invoice_no:str
)->Dict[str,Any]:


    try:

        response = (

            db()
            .table("sales")
            .select("*")
            .eq(
                "invoice_no",
                invoice_no
            )
            .single()
            .execute()

        )


        return response.data or {}


    except Exception as e:


        log_error(
            f"get_receipt error : {e}"
        )


        return {}





# ==============================================================================
# FULL RECEIPT
# ==============================================================================

def get_full_receipt(
    invoice_no:str
)->Dict[str,Any]:


    try:


        sale = get_receipt(
            invoice_no
        )


        if not sale:

            return {

                "success":False,

                "sale":None,

                "items":[]

            }



        items = get_sale_items(
            sale["id"]
        )


        return {


            "success":True,

            "sale":sale,

            "items":items


        }


    except Exception as e:


        log_error(
            f"get_full_receipt error : {e}"
        )


        return {

            "success":False,

            "sale":None,

            "items":[]

        }





# ==============================================================================
# SEARCH RECEIPTS
# ==============================================================================

def search_receipts(
    keyword:str=""
)->List[Dict[str,Any]]:


    try:


        query = (

            db()
            .table("sales")
            .select("*")

        )


        if keyword:


            query = (

                query
                .ilike(
                    "invoice_no",
                    f"%{keyword}%"
                )

            )


        response=(

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
            f"search_receipts error : {e}"
        )


        return []
