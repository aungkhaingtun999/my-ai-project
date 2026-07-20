# ==============================================================================
# utils/ui.py
# ERP ENTERPRISE UI LIBRARY v2.1.1
# CORE UI FRAMEWORK
# Streamlit 1.50+
# ==============================================================================

from datetime import date
import io
import math
import pandas as pd
import streamlit as st

UI_VERSION = "2.1.1 Enterprise ERP"


# ==============================================================================
# PAGE COMPONENTS
# ==============================================================================


def page_title(title, icon="📦"):
    st.title(f"{icon} {title}")


def page_header(title, subtitle=""):
    st.subheader(title)
    if subtitle:
        st.caption(subtitle)
    st.divider()


def section(title):
    st.markdown(f"### {title}")


def divider():
    st.divider()


# ==============================================================================
# MESSAGE COMPONENTS
# ==============================================================================


def success(message):
    st.success(message)


def error(message):
    st.error(message)


def warning(message):
    st.warning(message)


def info(message):
    st.info(message)


def empty_data(message="No data available"):
    st.info(message)


# ==============================================================================
# TABLE ENGINE
# ==============================================================================


def add_serial(df):
    if df is None:
        return df

    df = df.copy()

    if "No." not in df.columns:
        df.insert(0, "No.", range(1, len(df) + 1))

    return df


def show_table(df, serial=True, hide_index=True, width="stretch"):
    if df is None:
        empty_data()
        return

    if isinstance(df, list):
        df = pd.DataFrame(df)

    if len(df) == 0:
        empty_data()
        return

    if serial:
        df = add_serial(df)

    st.dataframe(df, hide_index=hide_index, width=width)


def table_panel(df, title="Records"):
    section(title)
    show_table(df)

    if df is None:
        count = 0
    else:
        count = len(df)

    st.caption(f"Total Records : {count}")


# ==============================================================================
# KPI / METRIC
# ==============================================================================


def metric_card(label, value, delta=None):
    st.metric(label, value, delta)


def metric_row(items):
    cols = st.columns(len(items))

    for col, item in zip(cols, items):
        if len(item) == 2:
            label, value = item
            delta = None
        else:
            label, value, delta = item

        col.metric(label, value, delta)


# ==============================================================================
# SEARCH
# ==============================================================================


def search_box(label="🔍 Search", key=None, placeholder="Search..."):
    return st.text_input(label, key=key, placeholder=placeholder)


def search_filter(search_label="🔍 Search", categories=None):
    c1, c2 = st.columns([3, 2])

    with c1:
        search = st.text_input(search_label)

    selected = None
    with c2:
        if categories:
            selected = st.selectbox("Category", categories)

    return search, selected


# ==============================================================================
# TOOLBAR / FILTER / ACTION COMPONENTS
# ==============================================================================


def toolbar(columns=4):
    return st.columns(columns)


def date_filter():
    c1, c2 = st.columns(2)

    with c1:
        start = st.date_input("From", value=date.today())

    with c2:
        end = st.date_input("To", value=date.today())

    return start, end


def status_filter(statuses, label="Status"):
    return st.selectbox(label, statuses)


def refresh_button():
    if st.button("🔄 Refresh", width="stretch"):
        st.rerun()


def action_buttons(add=True, edit=True, delete=False, export=False):
    cols = st.columns(4)
    result = {}

    if add:
        with cols[0]:
            result["add"] = st.button("➕ Add", width="stretch")

    if edit:
        with cols[1]:
            result["edit"] = st.button("✏️ Edit", width="stretch")

    if delete:
        with cols[2]:
            result["delete"] = st.button("🗑 Delete", width="stretch")

    if export:
        with cols[3]:
            result["export"] = st.button("📄 Export", width="stretch")

    return result


def primary_button(text, key=None, icon=None):
    if icon:
        text = f"{icon} {text}"

    return st.button(text, key=key, width="stretch")


# ==============================================================================
# STATUS BADGE & COLOR UTILS
# ==============================================================================


def status_badge(status):
    status = str(status).lower()

    if status in ["active", "completed", "success", "paid"]:
        st.success(status.title())
    elif status in ["pending", "waiting"]:
        st.warning(status.title())
    elif status in ["cancelled", "inactive", "failed"]:
        st.error(status.title())
    else:
        st.info(status.title())


def status_color(status):
    status = str(status).lower()

    if status in ["active", "completed", "success", "paid"]:
        return "green"

    if status in ["pending", "waiting"]:
        return "orange"

    if status in ["cancelled", "inactive", "failed"]:
        return "red"

    return "blue"


# ==============================================================================
# PAGINATION
# ==============================================================================


def paginate(data, page=1, page_size=20):
    if data is None:
        return []

    start = (page - 1) * page_size
    end = start + page_size

    return (
        data.iloc[start:end]
        if isinstance(data, pd.DataFrame)
        else data[start:end]
    )


def page_selector(total_rows, page_size=20):
    pages = max(1, math.ceil(total_rows / page_size))
    return st.number_input("Page", min_value=1, max_value=pages, value=1, step=1)


# ==============================================================================
# EXPORT ENGINE
# ==============================================================================


def download_csv(df, filename="report.csv"):
    if df is None:
        return

    if isinstance(df, list):
        df = pd.DataFrame(df)

    csv = df.to_csv(index=False)
    st.download_button(
        "⬇️ Download CSV", csv, file_name=filename, mime="text/csv"
    )


def download_excel(df, filename="report.xlsx"):
    if df is None:
        return

    if isinstance(df, list):
        df = pd.DataFrame(df)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    st.download_button(
        "⬇️ Download Excel",
        output.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def export_bar(df, filename="report"):
    c1, c2 = st.columns(2)
    with c1:
        download_csv(df, filename + ".csv")
    with c2:
        download_excel(df, filename + ".xlsx")


# ==============================================================================
# ADVANCED ERP COMPONENTS
# ==============================================================================


def loading(text="Loading..."):
    return st.spinner(text)


def panel(title, expanded=True):
    return st.expander(title, expanded=expanded)


def quick_stats(items):
    """Example:

    quick_stats([
        ("Products", 100),
        ("Stock", 500),
        ("Sales", "2M")
    ])
    """
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        col.metric(item[0], item[1])


def low_stock(df, qty_column="qty", minimum_column="minimum_stock"):
    if df is None:
        return pd.DataFrame()

    if isinstance(df, list):
        df = pd.DataFrame(df)

    if qty_column not in df.columns:
        return df

    if minimum_column not in df.columns:
        return df

    return df[df[qty_column] <= df[minimum_column]]


def table_summary(df):
    if df is None:
        return

    count = len(df)
    st.caption(f"Total Records : {count}")


def info_card(title, value):
    st.metric(title, value)


def form_columns(number=2):
    return st.columns(number)


def confirm_box(message):
    st.warning(message)


def box(title):
    with st.container():
        st.markdown(f"### {title}")
        st.divider()
        return st.container()


def footer():
    st.caption(f"ERP Enterprise UI Library {UI_VERSION}")


# ==============================================================================
# END OF FILE
# ==============================================================================
