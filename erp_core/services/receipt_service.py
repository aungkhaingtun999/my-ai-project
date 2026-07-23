# ==============================================================================
# erp_core/services/receipt_service.py
# ERP ENTERPRISE RECEIPT SERVICE v1.0
# Business Logic Layer
# ==============================================================================


from typing import (
from typing import Any, Dict, List, Optional

from ..loaders import (
    get_receipt,
    get_sale_items,
    search_receipts
)


class ReceiptService:


    def __init__(
        self,
        client: Any = None
    ):
        self.client = client



    def get_receipt(
        self,
        invoice_no: str
    ) -> Optional[Dict]:

        if not invoice_no:
            return None

        return get_receipt(
            invoice_no
        )



    def get_sale_items(
        self,
        sale_id: int
    ) -> List[Dict]:

        if not sale_id:
            return []

        return get_sale_items(
            sale_id
        )



    def search_receipts(
        self,
        keyword: str = ""
    ) -> List[Dict]:

        return search_receipts(
            keyword
        )



    def load_receipt(
        self,
        invoice_no: str
    ) -> Optional[Dict]:

        receipt = self.get_receipt(
            invoice_no
        )


        if not receipt:
            return None


        return receipt
    # ==========================================================================
    # GET SINGLE RECEIPT
    # ==========================================================================

    def get_receipt(
        self,
        receipt_key: Any
    ) -> Optional[Dict[str, Any]]:


        return get_receipt(
            receipt_key
        )




    # ==========================================================================
    # GET SALE ITEMS
    # ==========================================================================

    def get_sale_items(
        self,
        sale_id: int
    ) -> List[Dict[str, Any]]:


        return get_sale_items(
            sale_id
        )




    # ==========================================================================
    # SEARCH
    # ==========================================================================

    def search(
        self,
        keyword: str = ""
    ) -> List[Dict[str, Any]]:


        return search_receipts(
            keyword
        )




    # ==========================================================================
    # RECENT RECEIPTS
    # ==========================================================================

    def recent(
        self,
        limit: int = 20
    ) -> List[Dict[str, Any]]:


        return get_recent_receipts(
            limit
        )




    # ==========================================================================
    # COMPLETE RECEIPT
    # ==========================================================================

    def load_receipt(
        self,
        receipt_key: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Return:

        {
            success: True,
            sale: {},
            items: []
        }

        """


        result = get_full_receipt(
            receipt_key
        )


        if not result.get(
            "success"
        ):

            return None



        return result




    # ==========================================================================
    # RECEIPT SUMMARY
    # ==========================================================================

    def build_summary(
        self,
        receipt_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare data for UI / PDF
        """


        sale = receipt_data.get(
            "sale",
            {}
        )


        items = receipt_data.get(
            "items",
            []
        )


        return {


            "invoice_no":
                sale.get(
                    "invoice_no",
                    "-"
                ),



            "date":
                sale.get(
                    "created_at"
                ),



            "subtotal":
                sale.get(
                    "subtotal",
                    0
                ),



            "discount":
                sale.get(
                    "discount",
                    0
                ),



            "tax":
                sale.get(
                    "tax",
                    0
                ),



            "total":
                sale.get(
                    "total",
                    sale.get(
                        "total_amount",
                        0
                    )
                ),



            "paid_amount":
                sale.get(
                    "paid_amount",
                    0
                ),



            "change_amount":
                sale.get(
                    "change_amount",
                    0
                ),



            "payment_method":
                sale.get(
                    "payment_method",
                    "-"
                ),



            "status":
                sale.get(
                    "status",
                    sale.get(
                        "sale_status",
                        "-"
                    )
                ),



            "items":
                items

        }




    # ==========================================================================
    # VALIDATION
    # ==========================================================================

    def exists(
        self,
        receipt_key: Any
    ) -> bool:


        return (
            self.get_receipt(
                receipt_key
            )
            is not None
        )




# ==============================================================================
# EXPORT
# ==============================================================================

__all__ = [

    "ReceiptService"

]


print(
    "RECEIPT SERVICE v1.0 READY"
)
