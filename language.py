# ==========================================
# language.py
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

def t(key: str):
    init_language()

    lang = st.session_state.language

    return LANGUAGES.get(lang, EN).get(key, key)


# ==========================================
# AVAILABLE LANGUAGES
# ==========================================

def get_languages():
    return list(LANGUAGES.keys())