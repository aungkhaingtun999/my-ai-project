# =========================
# LANGUAGE STORE (i18n)
# =========================

LANG = "en"

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

    # Myanmar Language (example)
    "mm": {
        "app": {
            "pos_system": "POS စနစ်",
            "products": "ကုန်ပစ္စည်းများ",
            "cart": "စျေးခြင်းတောင်း",
            "checkout": "ငွေချေခြင်း",
            "dashboard": "အုပ်ချုပ်သူ Dashboard"
        },
        "payment": {
            "paid_amount": "ပေးချေငွေ",
            "pay": "ပေးချေမည်",
            "total": "စုစုပေါင်း"
        },
        "inventory": {
            "stock": "လက်ကျန်",
            "low_stock": "ကုန်ပစ္စည်းနည်းသတိပေးချက်"
        },
        "actions": {
            "add": "ထည့်ရန်",
            "remove": "ဖယ်ရှားရန်"
        }
    }
}

# =========================
# GET TEXT FUNCTION
# =========================
def t(key: str, lang: str = LANG):
    """
    Usage: t("app.pos_system")
    """

    keys = key.split(".")

    value = TEXT.get(lang, TEXT["en"])

    for k in keys:
        value = value.get(k)

        if value is None:
            # fallback to English
            value = TEXT["en"]
            for k in keys:
                value = value.get(k, key)
            return value

    return value