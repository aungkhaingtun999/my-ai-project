# ==============================================================================
# erp_core/services/receipt_service.py
# ERP ENTERPRISE RECEIPT SERVICE
# Business Logic Layer
# ==============================================================================

from typing import Any, Dict, List, Optional


from ..loaders import (
    get_receipt,
    get_sale_items,
    search_receipts
)



class ReceiptService:
    """
    Enterprise Receipt Service

    UI
      |
      v
    ReceiptService
      |
      v
    Loader
      |
      v
    Database
    """


    def __init__(
        self,
        client: Any = None
    ):

        self.client = client



    # ------------------------------------------------------------------
    # Get Receipt
    # ------------------------------------------------------------------

    def get_receipt(
        self,
        invoice_no: str
    ) -> Optional[Dict]:

        if not invoice_no:

            return None


        return get_receipt(
            invoice_no
        )



    # ------------------------------------------------------------------
    # Get Sale Items
    # ------------------------------------------------------------------

    def get_sale_items(
        self,
        sale_id: int
    ) -> List[Dict]:

        if not sale_id:

            return []


        return get_sale_items(
            sale_id
        )



    # ------------------------------------------------------------------
    # Search Receipts
    # ------------------------------------------------------------------

    def search_receipts(
        self,
        keyword: str = ""
    ) -> List[Dict]:


        return search_receipts(
            keyword
        )



    # ------------------------------------------------------------------
    # Full Receipt
    # ------------------------------------------------------------------

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



    # ------------------------------------------------------------------
    # Exists
    # ------------------------------------------------------------------

    def receipt_exists(
        self,
        invoice_no: str
    ) -> bool:


        return (
            self.get_receipt(invoice_no)
            is not None
        )
