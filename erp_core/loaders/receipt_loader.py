# ==============================================================================
# erp_core/loaders/receipt_loader.py
# ERP ENTERPRISE RECEIPT LOADER
# ==============================================================================

from typing import Dict, Any, List
from ..base_repo import db, log_error


def get_sale_items(sale_id: int) -> List[Dict[str, Any]]:
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
        log_error(f"get_sale_items error: {e}")
        return []


def get_receipt(sale_id: int) -> Dict[str, Any]:
    """
    Load complete receipt data (Sale Header + Items)
    """
    try:
        client = db()

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
        items = get_sale_items(sale_id)

        return {
            "success": True,
            "sale": sale,
            "items": items
        }

    except Exception as e:
        log_error(f"get_receipt error: {e}")
        return {
            "success": False,
            "message": str(e),
            "sale": None,
            "items": []
        }


# ==============================================================================
# FULL RECEIPT (Fixed)
# ==============================================================================

def get_full_receipt(receipt_key: int) -> Dict[str, Any]:
    """
    Load complete receipt using receipt_key (sale_id)
    """
    try:
        # get_receipt က {"success": True, "sale": {...}, "items": [...]} ကို ပြန်ပေးတာပါ
        receipt_data = get_receipt(receipt_key)

        if not receipt_data.get("success") or not receipt_data.get("sale"):
            return {
                "success": False,
                "sale": None,
                "items": []
            }

        return receipt_data

    except Exception as e:
        log_error(f"get_full_receipt error: {e}")
        return {
            "success": False,
            "sale": None,
            "items": []
        }


# ==============================================================================
# RECEIPT SEARCH (Fixed)
# ==============================================================================

def search_receipts(keyword: str = "") -> List[Dict[str, Any]]:
    """
    Search sales receipts by ID or invoice_no
    """
    try:
        client = db()
        query = client.table("sales").select("*")

        if keyword:
            # keyword သည် ဂဏန်းဖြစ်မှသာ id ကိုပါ ရှာဖွေစေခြင်း (Error မတက်အောင် ကာကွယ်ရန်)
            if keyword.isdigit():
                query = query.or_(f"id.eq.{keyword},invoice_no.ilike.%{keyword}%")
            else:
                query = query.ilike("invoice_no", f"%{keyword}%")

        response = (
            query
            .order("created_at", desc=True)
            .execute()
        )

        return response.data or []

    except Exception as e:
        log_error(f"search_receipts error: {e}")
        return []
