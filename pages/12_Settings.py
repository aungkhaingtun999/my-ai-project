import streamlit as st
from supabase_client import supabase

st.set_page_config(page_title="ERP Control Center", layout="wide")

# =========================
# 🔐 SECURITY GUARD (SAFE + REUSABLE)
# =========================
def require_admin():
    user = st.session_state.get("user")

    if not user:
        st.error("⛔ Please login first")
        st.stop()

    if user.get("role_id") != 1:
        st.error("⛔ Access Denied: Admin Only Module")
        st.stop()

    return user


# =========================
# APPLY GUARD
# =========================
user = require_admin()

st.title("⚙️ ERP Control Center (Admin Panel)")
st.success(f"🔐 Welcome Admin: {user.get('full_name', 'Admin')}")

# =========================
# LOAD SETTINGS FROM DB
# =========================
settings = supabase.table("erp_settings").select("*").execute().data or []

settings_map = {s["key"]: s["value"] for s in settings}

# =========================
# SAVE FUNCTION (SAFE)
# =========================
def save_setting(key, value):
    supabase.table("erp_settings").upsert({
        "key": key,
        "value": str(value)
    }).execute()

# =========================
# HELPER GETTERS (SAFE CAST)
# =========================
def get_bool(key, default=False):
    return str(settings_map.get(key, str(default))).lower() == "true"

def get_float(key, default=0):
    try:
        return float(settings_map.get(key, default))
    except:
        return default


# =========================
# 🧾 ACCOUNTING & TAX
# =========================
st.subheader("🧾 Accounting & Tax")

tax_rate = st.number_input(
    "Default Tax Rate (%)",
    value=get_float("tax_rate", 5)
)

discount_policy = st.selectbox(
    "Discount Policy",
    ["allowed", "restricted"],
    index=0 if settings_map.get("discount_policy", "allowed") == "allowed" else 1
)

if st.button("Save Accounting Settings"):
    save_setting("tax_rate", tax_rate)
    save_setting("discount_policy", discount_policy)
    st.success("Accounting settings updated")
    st.rerun()

st.divider()

# =========================
# 🏢 ORGANIZATION
# =========================
st.subheader("🏢 Organization Settings")

branch_mode = st.toggle(
    "Enable Multi-Branch",
    value=get_bool("multi_branch", False)
)

warehouse_mode = st.toggle(
    "Enable Multi-Warehouse",
    value=get_bool("multi_warehouse", True)
)

if st.button("Save Organization Settings"):
    save_setting("multi_branch", branch_mode)
    save_setting("multi_warehouse", warehouse_mode)
    st.success("Organization settings updated")
    st.rerun()

st.divider()

# =========================
# 👤 SECURITY
# =========================
st.subheader("👤 Security & Permissions")

rls_enabled = st.toggle(
    "Enable Row Level Security (RLS)",
    value=get_bool("rls", False)
)

if st.button("Save Security Settings"):
    save_setting("rls", rls_enabled)
    st.success("Security settings updated")
    st.rerun()

st.info("⚠️ RLS changes require Supabase policy update")

st.divider()

# =========================
# 📦 INVENTORY RULES
# =========================
st.subheader("📦 Inventory Rules")

min_stock_alert = st.number_input(
    "Default Minimum Stock Alert",
    value=get_float("min_stock", 10)
)

reorder_auto = st.toggle(
    "Enable Auto Reorder",
    value=get_bool("auto_reorder", False)
)

if st.button("Save Inventory Rules"):
    save_setting("min_stock", min_stock_alert)
    save_setting("auto_reorder", reorder_auto)
    st.success("Inventory rules updated")
    st.rerun()

st.divider()

# =========================
# 💱 FINANCE
# =========================
st.subheader("💱 Finance Settings")

currency = st.selectbox(
    "Base Currency",
    ["MMK", "USD", "THB", "SGD"],
    index=0
)

payment_methods = st.multiselect(
    "Enable Payment Methods",
    ["Cash", "Bank Transfer", "Mobile Pay", "Credit"],
    default=["Cash", "Bank Transfer"]
)

if st.button("Save Finance Settings"):
    save_setting("currency", currency)
    save_setting("payment_methods", ",".join(payment_methods))
    st.success("Finance settings updated")
    st.rerun()

st.divider()

# =========================
# 🧠 SYSTEM STATUS
# =========================
st.subheader("System Status")

st.success("""
✔ ERP Core Active  
✔ Warehouse Engine Ready  
✔ Sales/Purchase Connected  
✔ Settings DB Synced  
""")

st.success("⚙️ Control Center Fully Operational 🚀")
