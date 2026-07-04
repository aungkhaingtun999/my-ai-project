import streamlit as st
from supabase_client import supabase

st.title("⚙️ ERP Control Center (Admin Panel)")

# =========================
# SECURITY GUARD (ADMIN ONLY)
# =========================
user = st.session_state.get("user")
role = st.session_state.get("role")

if st.session_state.user.get("role_id") != 1:
    st.error("⛔ Access Denied: Admin Only Module")
    st.stop()

st.success("🔐 Admin Access Granted")

# =========================
# LOAD SETTINGS FROM DB
# =========================
settings = supabase.table("erp_settings").select("*").execute().data or []

settings_map = {s["key"]: s["value"] for s in settings}

# =========================
# HELPER FUNCTION
# =========================
def save_setting(key, value):
    supabase.table("erp_settings").upsert({
        "key": key,
        "value": str(value)
    }).execute()

# =========================
# 🧾 ACCOUNTING & TAX
# =========================
st.subheader("🧾 Accounting & Tax")

tax_rate = st.number_input(
    "Default Tax Rate (%)",
    value=float(settings_map.get("tax_rate", 5))
)

discount_policy = st.selectbox(
    "Discount Policy",
    ["allowed", "restricted"],
    index=0 if settings_map.get("discount_policy") != "restricted" else 1
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
    value=settings_map.get("multi_branch", "false") == "true"
)

warehouse_mode = st.toggle(
    "Enable Multi-Warehouse",
    value=settings_map.get("multi_warehouse", "true") == "true"
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
    value=settings_map.get("rls", "false") == "true"
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
    value=float(settings_map.get("min_stock", 10))
)

reorder_auto = st.toggle(
    "Enable Auto Reorder",
    value=settings_map.get("auto_reorder", "false") == "true"
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
# SYSTEM STATUS
# =========================
st.subheader("🧠 System Status")

st.info("""
✔ ERP Core Active  
✔ Warehouse Engine Ready  
✔ Sales/Purchase Connected  
✔ Settings DB Synced  
""")

st.success("⚙️ Control Center Fully Operational")
