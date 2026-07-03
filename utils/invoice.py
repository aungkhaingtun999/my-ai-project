from datetime import datetime
from database import supabase

def generate_invoice_no():
    today = datetime.now().strftime("%Y%m%d")

    # count today's invoices
    result = supabase.table("invoices") \
        .select("id") \
        .ilike("invoice_no", f"INV-{today}-%") \
        .execute()

    count = len(result.data or []) + 1

    return f"INV-{today}-{str(count).zfill(4)}"