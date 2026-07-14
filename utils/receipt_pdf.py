# utils/receipt_pdf.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import io

def generate_pdf(data):
    """
    Streamlit တွင် download ရနိုင်ရန် bytes object အနေဖြင့် return ပြန်ပေးသည်။
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    receipt = data
    items = data.get("cart", [])

    # HEADER
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, 800, "MY POS SYSTEM")
    c.setFont("Helvetica", 10)
    c.drawString(50, 770, f"Receipt No: {receipt.get('receipt_no', '')}")
    c.drawString(50, 755, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.drawString(50, 740, "-" * 90)

    # TABLE HEADER
    y = 720
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Item"); c.drawString(250, y, "Qty")
    c.drawString(320, y, "Price"); c.drawString(420, y, "Total")
    y -= 20
    c.setFont("Helvetica", 10)

    # ITEMS LIST
    for item in items:
        name = item.get("name", "Item")
        qty = item.get("qty", 0)
        price = float(item.get("selling_price", 0))
        total = qty * price

        if y < 100:
            c.showPage()
            y = 800

        c.drawString(50, y, str(name)[:25])
        c.drawString(250, y, str(qty))
        c.drawString(320, y, f"{price:,.0f}")
        c.drawString(420, y, f"{total:,.0f}")
        y -= 20

    # TOTAL SECTION
    y -= 20
    c.drawString(50, y, "-" * 90)
    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(320, y, f"TOTAL: {receipt.get('total', 0):,.0f}")
    
    c.save()
    
    # PDF data ကို buffer မှ ပြန်ထုတ်ခြင်း
    pdf_out = buffer.getvalue()
    buffer.close()
    return pdf_out
