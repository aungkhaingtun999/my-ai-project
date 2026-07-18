# ==============================================================================
# pages/1_POS.py v4.6.8 - DEBUG ENABLED
# ==============================================================================
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from database import (
    get_products, checkout_sale_rpc, get_setting, get_default_warehouse_id
)
from auth import is_authenticated
# language.py စစ်ဆေးရန် import အလွှာ
try:
    from language import t, language_selector
except ImportError:
    st.error("❌ language.py not found or missing functions!")
    st.stop()

# --- Page Config ---
st.set_page_config(page_title="Enterprise POS", layout="wide")

# --- DEBUGGING STEPS ---
st.write("### 🔍 Debug Trace")
st.write("STEP 1: Page Config Loaded")

# 1. Language Check
try:
    language_selector()
    st.write("STEP 2: Language Selector Loaded")
except Exception as e:
    st.error(f"❌ Language Selector Error: {e}")
    st.stop()

# 2. Auth Check
if not is_authenticated():
    st.write("AUTH FAIL")
    st.stop()
st.write("STEP 3: Auth Passed")

# 3. Database Check
warehouse_id = get_default_warehouse_id()
st.write(f"Warehouse ID: {warehouse_id}")

products = get_products(warehouse_id=warehouse_id)
st.write(f"Product Count: {len(products)}")

if not products:
    st.error(t("app.no_product"))
    st.stop()
st.write("STEP 4: Database Data Loaded")

# --- POS UI ---
st.title(f"🛒 {t('app.pos_system')}")
# (ကျန်ရှိသော POS UI/Logic များ ဆက်ထည့်ပါ)
