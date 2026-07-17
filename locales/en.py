# ==========================================
# language.py
# ERP ENTERPRISE i18n ENGINE v2.0
# Centralized Multi Language System
# ==========================================

import streamlit as st


# ==========================================
# LANGUAGE DATABASE
# ==========================================

TEXT = {

    "English": {

        "app": {
            "pos_system": "Enterprise POS System",
            "products": "Products",
            "cart": "Shopping Cart",
            "checkout": "Checkout",
            "dashboard": "Admin Dashboard",
            "no_product": "No products available"
        },

        "auth": {
            "login_required": "Please login first"
        },

        "search": {
            "product_name": "Product Name",
            "barcode": "Barcode / SKU",
            "choose": "Choose Product"
        },

        "cart": {
            "title": "Shopping Cart",
            "qty": "Quantity",
            "qty_short": "Qty",
            "add": "Add To Cart"
        },

        "payment": {

            "tax_rate": "Tax %",
            "discount": "Discount",
            "total": "Total",

            "method": "Payment Method",

            "cash": "Cash",
            "card": "Card",
            "mobile": "Mobile Banking",
            "credit": "Credit",

            "received": "Received Amount",
            "change": "Change",

            "confirm": "Confirm Sale"
        },

        "error": {
            "insufficient": "Payment is insufficient",
            "checkout_failed": "Checkout Failed"
        },

        "receipt": {

            "success": "Sale Completed",

            "no": "Receipt No",

            "print": "Print Receipt",

            "pdf": "Download PDF",

            "new_sale": "New Sale"
        },

        "stock": {
            "not_enough": "Not enough stock",
            "available": "Available"
        }
    },


    # ======================================
    # MYANMAR LANGUAGE
    # ======================================

    "မြန်မာ": {

        "app": {

            "pos_system": "Enterprise POS အရောင်းစနစ်",

            "products": "ကုန်ပစ္စည်းများ",

            "cart": "စျေးခြင်းတောင်း",

            "checkout": "ငွေရှင်းခြင်း",

            "dashboard": "စီမံခန့်ခွဲမှု Dashboard",

            "no_product": "ကုန်ပစ္စည်း မရှိပါ"
        },


        "auth": {

            "login_required":
            "ကျေးဇူးပြု၍ Login ဝင်ပါ"
        },


        "search": {

            "product_name":
            "ကုန်ပစ္စည်းအမည်",

            "barcode":
            "Barcode / SKU",

            "choose":
            "ကုန်ပစ္စည်းရွေးပါ"
        },


        "cart": {

            "title":
            "စျေးခြင်းတောင်း",

            "qty":
            "အရေအတွက်",

            "qty_short":
            "Qty",

            "add":
            "ထည့်မည်"
        },


        "payment": {

            "tax_rate":
            "အခွန် %",

            "discount":
            "လျှော့ငွေ",

            "total":
            "စုစုပေါင်း",

            "method":
            "ငွေပေးချေမှု",

            "cash":
            "ငွေသား",

            "card":
            "ကတ်",

            "mobile":
            "Mobile Banking",

            "credit":
            "အကြွေး",

            "received":
            "လက်ခံရရှိငွေ",

            "change":
            "ပြန်အမ်းငွေ",

            "confirm":
            "ရောင်းချမှု အတည်ပြု"
        },


        "error": {

            "insufficient":
            "ပေးချေငွေ မလုံလောက်ပါ",

            "checkout_failed":
            "ရောင်းချမှု မအောင်မြင်ပါ"
        },


        "receipt": {

            "success":
            "ရောင်းချမှု အောင်မြင်ပါသည်",

            "no":
            "ဘောက်ချာနံပါတ်",

            "print":
            "ဘောက်ချာထုတ်မည်",

            "pdf":
            "PDF Download",

            "new_sale":
            "အသစ်ပြန်ရောင်းမည်"
        },


        "stock": {

            "not_enough":
            "လက်ကျန် မလုံလောက်ပါ",

            "available":
            "လက်ကျန်"
        }

    }
}



# ==========================================
# INIT LANGUAGE
# ==========================================

def init_language():

    if "language" not in st.session_state:

        st.session_state.language = "မြန်မာ"



# ==========================================
# GET CURRENT LANGUAGE
# ==========================================

def get_language():

    init_language()

    return st.session_state.language



# ==========================================
# CHANGE LANGUAGE
# ==========================================

def set_language(lang):

    if lang in TEXT:

        st.session_state.language = lang



# ==========================================
# TRANSLATION FUNCTION
# ==========================================

def t(key):

    init_language()

    lang = st.session_state.language


    data = TEXT.get(
        lang,
        TEXT["English"]
    )


    for part in key.split("."):

        if isinstance(data, dict):

            data = data.get(part)

        else:

            data = None


        if data is None:

            # fallback English

            data = TEXT["English"]

            for p in key.split("."):

                if isinstance(data, dict):

                    data = data.get(p)

                else:

                    data = None
                    break


            return data if data else key


    return data



# ==========================================
# LANGUAGE SELECTOR
# ==========================================

def language_selector():

    init_language()


    current = st.session_state.language


    choice = st.sidebar.selectbox(

        "🌐 Language",

        list(TEXT.keys()),

        index=list(TEXT.keys()).index(current)

    )


    if choice != current:

        st.session_state.language = choice

        st.rerun()



# ==========================================
# AVAILABLE LANGUAGES
# ==========================================

def get_languages():

    return list(TEXT.keys())
