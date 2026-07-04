if res and res.get("success"):
            # 1. Receipt Rows များကို စုစည်းခြင်း
            receipt_rows = ""
            for i in st.session_state.cart:
                u_price = float(i["selling_price"])
                line_total = u_price * i["qty"]
                # HTML တည်ဆောက်ပုံကို ပိုမိုသေချာစေရန်
                receipt_rows += f'<div class="receipt-grid"><span>{i["name"][:12]}</span><span>x{i["qty"]}</span><span>{u_price:,.0f}</span><span style="text-align:right">{line_total:,.0f}</span></div>'
            
            # 2. HTML တစ်ခုလုံးကို Variable တစ်ခုထဲ ထည့်ခြင်း
            receipt_html = f"""
            <div class="receipt-container">
                <div class="receipt-header">AURORA LUXE RETAIL<br>Tachileik Branch</div>
                <div class="receipt-divider"></div>
                <div class="receipt-grid" style="font-weight:bold"><span>ITEM</span><span>QTY</span><span>PRICE</span><span style="text-align:right">TOTAL</span></div>
                <div class="receipt-divider"></div>
                {receipt_rows}
                <div class="receipt-divider"></div>
                <div class="receipt-total-row"><span>SUBTOTAL</span><span>{subtotal:,.0f}</span></div>
                <div class="receipt-total-row"><span>DISCOUNT</span><span>-{disc:,.0f}</span></div>
                <div class="receipt-total-row"><span>TAX</span><span>{tax_amount:,.0f}</span></div>
                <div class="receipt-total-row" style="font-size: 1.2em;"><span>GRAND TOTAL</span><span>{final_total:,.0f}</span></div>
            </div>
            """
            
            # 3. Streamlit မှာ အပြင်မှာမှ ခေါ်ယူခြင်း
            st.markdown(receipt_html, unsafe_allow_html=True)
            
            # New Sale button
            st.button("New Sale", on_click=clear_cart)
