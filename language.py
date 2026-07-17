# ==========================================
# language.py
# ERP ENTERPRISE i18n ENGINE v2
# Production Ready Multi-Language System
# ==========================================


import streamlit as st


from config import DEFAULT_LANGUAGE

from locales.en import TEXT as EN

from locales.my import TEXT as MY



# ==========================================
# LANGUAGE MAP
# ==========================================

LANGUAGES = {

    "English": EN,

    "မြန်မာ": MY

}



# ==========================================
# INIT LANGUAGE
# ==========================================

def init_language():

    if "language" not in st.session_state:

        st.session_state.language = DEFAULT_LANGUAGE



# ==========================================
# SET LANGUAGE
# ==========================================

def set_language(lang: str):

    if lang in LANGUAGES:

        st.session_state.language = lang



# ==========================================
# GET CURRENT LANGUAGE
# ==========================================

def get_language():

    init_language()

    return st.session_state.language



# ==========================================
# TRANSLATION FUNCTION
# ==========================================
# Usage:
#
# t("app.pos_system")
# t("payment.total")
#
# ==========================================

def t(key: str):

    init_language()


    lang = st.session_state.language


    data = LANGUAGES.get(
        lang,
        EN
    )


    keys = key.split(".")


    try:

        for k in keys:

            data = data[k]


        return data


    except Exception:


        # ==============================
        # FALLBACK TO ENGLISH
        # ==============================

        data = EN


        try:

            for k in keys:

                data = data[k]


            return data


        except Exception:

            return key



# ==========================================
# AVAILABLE LANGUAGES
# ==========================================

def get_languages():

    return list(
        LANGUAGES.keys()
    )



# ==========================================
# LANGUAGE DISPLAY HELPER
# ==========================================

def language_selector():

    init_language()


    current = st.session_state.language


    selected = st.sidebar.selectbox(

        "🌐 Language",

        get_languages(),

        index=
        get_languages().index(current)
        if current in get_languages()
        else 0

    )


    if selected != current:

        set_language(selected)

        st.rerun()
