import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

st.set_page_config(page_title="MiDAY Insights", layout="wide")
st.title("☕ MiDAY System – Live Dashboard")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8D3xOvu7VXVuwSSydp7I5TsrUnHd2dlzDy1g3MWaW1y0ojhEi4Ftvoi1ev4ZkeQeX4glRCzQvklsj/pub?gid=2071886823&single=true&output=csv"  # <-- REPLACE

@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["Date"], how="all")
    df = df[df["Date"].notna()]
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    for col in ["Unit Price", "Revenue", "COGS"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    if "Quantity" in df.columns:
        df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0).astype(int)
    else:
        df["Quantity"] = 0
    df["Category"] = df.get("Category", "Uncategorized").fillna("Uncategorized")
    df["Payment Status"] = df.get("Payment Status", "Unknown").fillna("Unknown")
    df["Profit"] = df["Revenue"] - df["COGS"]
    df["Margin %"] = (df["Profit"] / df["Revenue"] * 100).round(1).fillna(0)
    return df

df = load_data()
if df.empty:
    st.stop()

def fmt_currency(value):
    return f"UGX {value:,.0f}"

# --- Sidebar ---
st.sidebar.title("Filters")
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date])
categories = st.sidebar.multiselect("Category", sorted(df["Category"].unique()), default=sorted(df["Category"].unique()))
statuses = st.sidebar.multiselect("Payment Status", sorted(df["Payment Status"].unique()), default=sorted(df["Payment Status"].unique()))

fdf = df[
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1])) &
    (df["Category"].isin(categories)) &
    (df["Payment Status"].isin(statuses))
]

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Products", "Trends", "Raw"])

with tab1:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Revenue", fmt_currency(fdf["Revenue"].sum()))
    col2.metric("Profit", fmt_currency(fdf["Profit"].sum()))
    margin = (fdf["Profit"].sum() / fdf["Revenue"].sum() * 100) if fdf["Revenue"].sum() > 0 else 0
    col3.metric("Margin", f"{margin:.1f}%")
    col4.metric("Orders", len(fdf))
    col5.metric("Units", fdf["Quantity"].sum())

    col1, col2 = st.columns(2)
    with col1:
        daily = fdf.groupby("Date")["Revenue"].sum().reset_index()
        fig = px.line(daily, x="Date", y="Revenue", title="Revenue Trend")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        cat_sum = fdf.groupby("Category")["Revenue"].sum().reset_index()
        fig = px.pie(cat_sum, names="Category", values="Revenue", title="Revenue by Category")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Product Performance")
    prod = fdf.groupby("Product Name")["Revenue"].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(prod, x="Product Name", y="Revenue", title="Revenue by Product")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(prod)

with tab3:
    st.subheader("Trends")
    gran = st.radio("Granularity", ["Daily", "Weekly", "Monthly"], horizontal=True)
    if gran == "Daily":
        fdf["Period"] = fdf["Date"].dt.date
    elif gran == "Weekly":
        fdf["Period"] = fdf["Date"].dt.to_period("W").apply(lambda r: r.start_time.date())
    else:
        fdf["Period"] = fdf["Date"].dt.to_period("M").apply(lambda r: r.start_time.date())
    agg = fdf.groupby("Period")["Revenue"].sum().reset_index()
    fig = px.bar(agg, x="Period", y="Revenue", title=f"Revenue ({gran})")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.dataframe(fdf[["Date", "Product Name", "Category", "Quantity", "Unit Price", "Revenue", "Payment Status"]], use_container_width=True)

st.sidebar.caption("Data refreshed: " + datetime.now().strftime("%H:%M:%S"))
