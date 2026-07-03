from escpos.printer import Usb

# ⚠️ Replace with your printer IDs
# (find via device manager or printer docs)

PRINTER_VENDOR_ID = 0x04b8
PRINTER_PRODUCT_ID = 0x0e15

def get_printer():
    return Usb(PRINTER_VENDOR_ID, PRINTER_PRODUCT_ID)