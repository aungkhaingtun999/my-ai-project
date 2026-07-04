import streamlit as st

st.title("⚙️ ERP Control Center")

st.subheader("System Configuration Hub")

st.markdown("""
### 🧾 Accounting & Tax
- Tax rules configuration
- Discount policies

### 🏢 Organization
- Branch management
- Warehouse control

### 👤 Security
- Roles & Permissions
- Row Level Security (RLS)

### 📦 Inventory Rules
- Minimum stock alerts
- Reorder automation
- Stock valuation method

### 💱 Finance
- Currency settings
- Payment methods
""")

st.warning("⚠️ Admin-only module (future RBAC enforcement required)")
