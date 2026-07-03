import streamlit as st
from datetime import datetime

st.title("📦 Inventory Management System (ERP Ready)")

# =========================
# INIT SESSION STORAGE
# =========================
if "inventory" not in st.session_state:
    st.session_state.inventory = []

# =========================
# FORM INPUT
# =========================
st.subheader("➕ Add New Product")

col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Product Name")

with col2:
    price = st.number_input("Selling Price", min_value=0)

col3, col4 = st.columns(2)

with col3:
    purchase_price = st.number_input("Purchase Price", min_value=0)

with col4:
    stock = st.number_input("Stock Quantity", min_value=0, step=1)

# =========================
# ADD PRODUCT
# =========================
if st.button("➕ Add Product"):

    if not name:
        st.error("Product name is required")

    else:
        product = {
            "id": len(st.session_state.inventory) + 1,
            "name": name,
            "selling_price": price,
            "purchase_price": purchase_price,
            "stock": stock,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        st.session_state.inventory.append(product)
        st.success(f"{name} added successfully!")
        st.rerun()

# =========================
# INVENTORY LIST
# =========================
st.divider()
st.subheader("📋 Inventory List")

if not st.session_state.inventory:
    st.info("No products yet")

total_value = 0

for item in st.session_state.inventory:

    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])

    with col1:
        st.write(f"🛒 {item['name']}")

    with col2:
        st.write(f"Selling: {item['selling_price']}")

    with col3:
        st.write(f"Cost: {item['purchase_price']}")

    with col4:
        st.write(f"Stock: {item['stock']}")

    with col5:
        if st.button("❌", key=f"del_{item['id']}"):
            st.session_state.inventory = [
                i for i in st.session_state.inventory
                if i["id"] != item["id"]
            ]
            st.rerun()

    total_value += item["purchase_price"] * item["stock"]

# =========================
# INVENTORY SUMMARY
# =========================
st.divider()
st.subheader("📊 Summary")

st.metric("Total Products", len(st.session_state.inventory))
st.metric("Stock Value (Cost Price)", f"{total_value:,.0f} MMK")

# =========================
# EXPORT NOTE (READY FOR DB)
# =========================
st.info("💡 This structure is ready to connect with Supabase products table later.")