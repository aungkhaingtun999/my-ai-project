# =========================
# INTERNATIONALIZATION SYSTEM
# =========================

LANG = "mm"   # default language

TEXT = {
    "en": {
        "app": {
            "pos_system": "POS System",
            "products": "Products",
            "cart": "Cart",
            "checkout": "Checkout",
            "dashboard": "Admin Dashboard"
        },
        "payment": {
            "paid_amount": "Paid Amount",
            "pay": "Pay",
            "total": "Total"
        },
        "inventory": {
            "stock": "Stock",
            "low_stock": "Low Stock Alerts"
        },
        "actions": {
            "add": "Add",
            "remove": "Remove"
        }
    },

    "mm": {
        "app": {
            "pos_system": "အရောင်းစနစ်",
            "products": "ကုန်ပစ္စည်းများ",
            "cart": "စျေးဝယ်ခြင်း",
            "checkout": "ငွေရှင်းရန်",
            "dashboard": "စီမံခန့်ခွဲမှု Dashboard"
        },
        "payment": {
            "paid_amount": "ပေးချေသောငွေပမာဏ",
            "pay": "ငွေရှင်းမည်",
            "total": "စုစုပေါင်း"
        },
        "inventory": {
            "stock": "လက်ကျန်",
            "low_stock": "လက်ကျန်နည်း သတိပေးချက်"
        },
        "actions": {
            "add": "ထည့်မည်",
            "remove": "ဖျက်မည်"
        }
    }
}

# =========================
# TRANSLATION FUNCTION
# =========================
def t(key: str, lang: str = LANG):
    """
    Usage:
        t("app.pos_system")
        t("payment.total")
    """

    keys = key.split(".")

    # get language pack
    value = TEXT.get(lang, TEXT["en"])

    # traverse nested keys
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            value = None

        if value is None:
            # fallback to English
            fallback = TEXT["en"]
            for k in keys:
                fallback = fallback.get(k, key)
            return fallback

    return value