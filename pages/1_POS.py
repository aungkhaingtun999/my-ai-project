# =========================
# 3. CART DISPLAY & CALCULATION (UPGRADED)
# =========================
st.divider()
st.subheader("🧾 Cart")

def safe_float(v):
    try:
        return float(v or 0)
    except:
        return 0.0


if st.session_state.cart:

    total_tax = 0
    subtotal = 0
    total_discount = 0
    grand_total = 0

    for i, item in enumerate(st.session_state.cart):

        col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns([3, 1, 1, 1, 1])

        name = item["name"]
        price = safe_float(item.get("selling_price", 0))
        qty = item.get("qty", 1)

        tax_rate = safe_float(item.get("tax_rate", 0))
        discount_allowed = item.get("discount_allowed", False)

        # =========================
        # CALCULATION ENGINE
        # =========================
        line_base = price * qty

        tax_amount = line_base * (tax_rate / 100)

        # discount rule
        if discount_allowed:
            discount_rate = item.get("discount", 0)
        else:
            discount_rate = 0

        discount_amount = line_base * (safe_float(discount_rate) / 100)

        line_total = line_base + tax_amount - discount_amount

        # =========================
        # UI ROW
        # =========================
        col_c1.write(name)

        item["qty"] = col_c2.number_input(
            "Qty",
            1,
            999,
            value=int(qty),
            key=f"qty_{i}"
        )

        col_c3.write(f"Tax: {tax_rate}%")

        if discount_allowed:
            col_c4.write(f"Disc: {safe_float(discount_rate)}%")
        else:
            col_c4.write("❌ No Disc")

        col_c5.write(f"{line_total:,.0f} MMK")

        # =========================
        # DELETE ITEM
        # =========================
        if st.button("🗑", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

        # =========================
        # TOTALS
        # =========================
        subtotal += line_base
        total_tax += tax_amount
        total_discount += discount_amount
        grand_total += line_total


    # =========================
    # SUMMARY SECTION
    # =========================
    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    c1.metric("Subtotal", f"{subtotal:,.0f} MMK")
    c2.metric("Tax", f"{total_tax:,.0f} MMK")
    c3.metric("Discount", f"{total_discount:,.0f} MMK")

    st.markdown(f"""
    ## 💰 Grand Total: {grand_total:,.0f} MMK
    """)

else:
    st.info("🧾 Cart is empty")
