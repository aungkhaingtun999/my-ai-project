import streamlit as st

st.title("⚙️ Settings")

st.subheader("ERP Configuration Panel")

st.write("Future Modules to Control:")

st.markdown("""
- 🧾 Tax Settings
- 🏢 Branch Management
- 👤 User Roles & Permissions
- 🔐 Row Level Security (RLS)
- 📦 Inventory Rules
- 💱 Currency Settings
""")

st.info("ဒီ page က ERP control center ဖြစ်လာမယ် (Admin only)")