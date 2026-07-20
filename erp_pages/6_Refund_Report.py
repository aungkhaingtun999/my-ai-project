import streamlit as st
import pandas as pd
from datetime import date
import io
import plotly.express as px
from database import db
from auth import require_login
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from utils.ui import show_table

# ==========================
# AUTH
# ==========================
user = require_login()

st.set_page_config(page_title="Refund Report", layout="wide")
st.title("📊 Refund Report v3.1")

# ==========================
# DETAIL STATE
# ==========================
if "selected_refund_id" not in st.session_state:
    st.session_state.selected_refund_id = None

# ==========================
# LOAD DATA
# ==========================
@st.cache_data(ttl=60)
def get_refund_report():
    response = db().table("refund_report_view").select("*").order("refund_date", desc=True).execute()
    return pd.DataFrame(response.data)

df = get_refund_report()

if df.empty:
    st.info("No refund records found.")
    st.stop()

df["refund_date"] = pd.to_datetime(df["refund_date"])

# ==========================
# FILTER
# ==========================
st.sidebar.header("🔍 Report Filter")
invoice_search = st.sidebar.text_input("Invoice No")
cashier_filter = st.sidebar.multiselect("Cashier", df["cashier_name"].dropna().unique())
warehouse_filter = st.sidebar.multiselect("Warehouse", df["warehouse_name"].dropna().unique())
status_filter = st.sidebar.multiselect("Status", ["PENDING", "COMPLETED", "REJECTED"])
from_date = st.sidebar.date_input("From Date", df["refund_date"].min().date())
to_date = st.sidebar.date_input("To Date", date.today())

filtered = df.copy()
filtered = filtered[(filtered["refund_date"].dt.date >= from_date) & (filtered["refund_date"].dt.date <= to_date)]

if invoice_search:
    filtered = filtered[filtered["invoice_no"].str.contains(invoice_search, case=False, na=False)]
if cashier_filter:
    filtered = filtered[filtered["cashier_name"].isin(cashier_filter)]
if warehouse_filter:
    filtered = filtered[filtered["warehouse_name"].isin(warehouse_filter)]
if status_filter:
    filtered = filtered[filtered["status"].isin(status_filter)]

# ==========================
# KPI Calculation (Dynamic)
# ==========================
total_refunds = filtered["refund_id"].nunique()
pending = (filtered["status"] == "PENDING").sum()
completed = (filtered["status"] == "COMPLETED").sum()
rejected = (filtered["status"] == "REJECTED").sum()
total_amount = filtered["item_total"].sum()

c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.metric("Total Refunds", total_refunds)
with c2: st.metric("Pending", pending)
with c3: st.metric("Completed", completed)
with c4: st.metric("Rejected", rejected)
with c5: st.metric("Total Amount", f"{total_amount:,.0f} MMK")

# ==========================
# REFUND DETAIL DIALOG
# ==========================
def create_refund_pdf(header, items):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    content = [Paragraph("Refund Report", styles["Title"]), Spacer(1, 12)]
    content.append(Paragraph(f"Refund ID: {header['refund_id']}<br/>Invoice: {header['invoice_no']}<br/>Status: {header['status']}<br/>Cashier: {header['cashier_name']}<br/>Warehouse: {header['warehouse_name']}<br/>Reason: {header.get('reason','')}", styles["Normal"]))
    content.append(Spacer(1, 12))
    table_data = [["Product", "Qty", "Price", "Total"]]
    for item in items:
        table_data.append([item["product_name"], item["quantity"], item["unit_price"], item["item_total"]])
    table = Table(table_data)
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, None)]))
    content.append(table)
    doc.build(content)
    buffer.seek(0)
    return buffer

@st.dialog("Refund Detail")
def refund_detail_dialog(refund_id):
    header = db().table("refund_header_view").select("*").eq("refund_id", refund_id).single().execute().data
    if not header: return
    st.subheader(f"Refund ID : {header['refund_id']}")
    c1, c2 = st.columns(2)
    with c1: 
        st.write(f"Invoice : {header['invoice_no']}")
        st.write(f"Cashier : {header['cashier_name']}")
    with c2: 
        st.write(f"Status : {header['status']}")
        st.write(f"Date : {header['refund_date']}")
    
    st.write("### Remarks")
    st.write(header.get("remarks") or "-")
    
    items = db().table("refund_detail_view").select("*").eq("refund_id", refund_id).execute().data
    if items:
        item_df = pd.DataFrame(items)
        show_table(
            item_df[[
                "product_name",
                "quantity",
                "unit_price",
                "item_total"
            ]]
        )
        st.success(f"Total: {item_df['item_total'].sum():,.0f} MMK")
        
        pdf_file = create_refund_pdf(header, items)
        st.download_button("📄 PDF", pdf_file, f"refund_{refund_id}.pdf", "application/pdf")
        st.download_button("🖨️ HTML", f"<h2>Report</h2>{item_df.to_html()}", f"refund_{refund_id}.html", "text/html")

# ==========================
# REFUND LIST
# ==========================
st.divider()
st.subheader("Refund Details")

columns = [
    "refund_id",
    "invoice_no",
    "refund_date",
    "status",
    "product_name",
    "quantity",
    "item_total",
    "cashier_name",
    "processed_by",
    "warehouse_name",
    "reason"
]

for _, row in filtered.iterrows():
    c1, c2, c3, c4 = st.columns([1, 3, 2, 2])
    c1.write(row["refund_id"])
    c2.write(row["invoice_no"])
    c3.write(f"{row['item_total']:,.0f} MMK")
    if c4.button("👁️ View", key=f"view_{row['refund_id']}_{row.get('item_index', 0)}"):
        refund_detail_dialog(row["refund_id"])

# Also replacing standard dataframe views if any remain using columns
show_table(
    filtered[columns]
)

# ==========================
# ANALYTICS
# ==========================
st.divider()
st.subheader("📊 Refund Analytics")
if not filtered.empty:
    st.line_chart(filtered.groupby(filtered["refund_date"].dt.date)["item_total"].sum())
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 Top 10 Products")
        st.bar_chart(filtered.groupby("product_name")["quantity"].sum().sort_values(ascending=False).head(10))
    with col2:
        st.subheader("📊 Status")
        sd = filtered.groupby("status")["refund_id"].nunique()
        st.plotly_chart(px.pie(values=sd.values, names=sd.index), use_container_width=True)
    st.subheader("👤 Cashier Ranking (Top 5)")
    st.bar_chart(filtered.groupby("cashier_name")["item_total"].sum().sort_values(ascending=False).head(5))
else:
    st.warning("No data for analytics")

# ==========================
# EXPORT
# ==========================
st.divider()
st.subheader("📥 Export")
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    filtered.to_excel(writer, index=False)
st.download_button("📥 Excel", excel_buffer.getvalue(), "refund_report.xlsx")

