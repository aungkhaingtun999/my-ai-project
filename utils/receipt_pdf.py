# utils/receipt_pdf.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
import json
import os

def get_shop_info():
    # လက်ရှိ utils ဖိုင်ရှိရာ folder မှ အပြင်သို့ထွက် ('..')
    # ထို့နောက် 'pages' ဖိုဒါထဲရှိ 'config.json' ကို ရှာဖွေခြင်း
    config_path = os.path.join(os.path.dirname(__file__), '..', 'pages', 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        # ဖိုင်ရှာမတွေ့ပါက Default တန်ဖိုးကို ပြန်ပေးခြင်း
        return {
            "shop_name": "MY POS SYSTEM",
            "address": "Tachileik, Shan State, Myanmar",
            "phone": "09-XXXXXXXXXX",
            "footer_msg": "Thank you for shopping with us!"
        }

def generate_pdf(data):
    """
    Receipt PDF Generator with Tax, Discount, Subtotal and Cashier Info.
    """
    shop = get_shop_info()
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    receipt = data
    items = data.get("cart", [])
    timestamp = receipt.get("timestamp", "N/A")

    # HEADER
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, 800, shop.get('shop_name', 'MY POS SYSTEM'))
    
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, 785, shop.get('address', ''))
    c.drawCentredString(width / 2, 770, f"Tel: {shop.get('phone', '')}")
    
    c.drawString(50, 745, f"Receipt No: {receipt.get('receipt_no', '')}")
    c.drawString(50, 730, f"Date: {timestamp}")
    c.drawString(50, 715, f"Cashier: {receipt.get('cashier_name', 'Admin')}")
    c.drawString(50, 700, "-" * 90)

    # TABLE HEADER
    y = 680
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Item")
    c.drawString(250, y, "Qty")
    c.drawString(320, y, "Price")
    c.drawString(420, y, "Total")
    
    y -= 20
    c.setFont("Helvetica", 10)

    # ITEMS LIST
    for item in items:
        name = item.get("name", "Item")
        qty = item.get("qty", 0)
        price = float(item.get("selling_price", 0))
        total = qty * price

        if y < 150: # Page break if running out of space
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
    
    # Financial Details
    y -= 30
    c.setFont("Helvetica", 11)
    c.drawString(320, y, f"Subtotal: {receipt.get('subtotal', 0):,.0f}")
    y -= 20
    c.drawString(320, y, f"Discount: {receipt.get('discount', 0):,.0f}")
    y -= 20
    c.drawString(320, y, f"Tax: {receipt.get('tax', 0):,.0f}")
    
    # Grand Total
    y -= 20
    c.setFont("Helvetica-Bold", 13)
    c.drawString(320, y, f"GRAND TOTAL: {receipt.get('total', 0):,.0f}")
    
    # FOOTER
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width / 2, 50, shop.get('footer_msg', 'Thank you for shopping with us!'))
    
    c.save()
    
    pdf_out = buffer.getvalue()
    buffer.close()
    return pdf_out

