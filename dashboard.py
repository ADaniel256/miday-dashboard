import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import time

CURRENCY = "UGX"
st.set_page_config(page_title="MiDAY Insights", layout="wide", initial_sidebar_state="collapsed")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8D3xOvu7VXVuwSSydp7I5TsrUnHd2dlzDy1g3MWaW1y0ojhEi4Ftvoi1ev4ZkeQeX4glRCzQvklsj/pub?gid=2071886823&single=true&output=csv"  # <-- REPLACE THIS

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

def fmt_currency(v):
    return f"{CURRENCY} {v:,.0f}"

st.sidebar.title("🔍 Filters")
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh every 30s")
animation_speed = st.sidebar.slider("🏁 Bar Race Speed (ms per frame)", 300, 5000, 1500, 100)

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date])
categories = st.sidebar.multiselect("Category", sorted(df["Category"].unique()), default=sorted(df["Category"].unique()))
statuses = st.sidebar.multiselect("Payment Status", sorted(df["Payment Status"].unique()), default=sorted(df["Payment Status"].unique()))
products = st.sidebar.multiselect("Product (optional)", sorted(df["Product Name"].unique()), default=sorted(df["Product Name"].unique()))

fdf = df[
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1])) &
    (df["Category"].isin(categories)) &
    (df["Payment Status"].isin(statuses)) &
    (df["Product Name"].isin(products))
]

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Products", "Trends", "Raw"])

with tab1:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Revenue", fmt_currency(fdf["Revenue"].sum()))
    c2.metric("Profit", fmt_currency(fdf["Profit"].sum()))
    margin = (fdf["Profit"].sum() / fdf["Revenue"].sum() * 100) if fdf["Revenue"].sum() > 0 else 0
    c3.metric("Margin", f"{margin:.1f}%")
    c4.metric("Orders", len(fdf))
    c5.metric("Units", fdf["Quantity"].sum())

    col1, col2 = st.columns(2)
    with col1:
        daily = fdf.groupby("Date")["Revenue"].sum().reset_index()
        fig = px.line(daily, x="Date", y="Revenue", title="Revenue Trend", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        cat_sum = fdf.groupby("Category")["Revenue"].sum().reset_index()
        fig = px.pie(cat_sum, names="Category", values="Revenue", title="Revenue by Category", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Product Performance")
    prod = fdf.groupby("Product Name").agg({"Revenue": "sum", "Profit": "sum"}).reset_index()
    prod["Margin %"] = (prod["Profit"] / prod["Revenue"] * 100).round(1).fillna(0)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=prod["Product Name"], y=prod["Revenue"], name="Revenue"))
    fig.add_trace(go.Scatter(x=prod["Product Name"], y=prod["Margin %"], name="Margin %", yaxis="y2"))
    fig.update_layout(yaxis2=dict(overlaying="y", side="right"), barmode="group")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(prod)

with tab3:
    st.subheader("Trends")
    gran = st.radio("Granularity", ["Daily", "Weekly", "Monthly"], horizontal=True)
    fdf_copy = fdf.copy()
    if gran == "Daily":
        fdf_copy["Period"] = fdf_copy["Date"].dt.date
    elif gran == "Weekly":
        fdf_copy["Period"] = fdf_copy["Date"].dt.to_period("W").apply(lambda r: r.start_time.date())
    else:
        fdf_copy["Period"] = fdf_copy["Date"].dt.to_period("M").apply(lambda r: r.start_time.date())
    agg = fdf_copy.groupby("Period")["Revenue"].sum().reset_index()
    fig = px.bar(agg, x="Period", y="Revenue", title=f"Revenue ({gran})")
    st.plotly_chart(fig, use_container_width=True)

    # Animated bar race
    fdf_month = fdf.copy()
    fdf_month["Month"] = fdf_month["Date"].dt.to_period("M").astype(str)
    race = fdf_month.groupby(["Month", "Product Name"])["Revenue"].sum().reset_index()
    if len(race["Month"].unique()) > 1:
        fig_race = px.bar(race, x="Revenue", y="Product Name", color="Product Name",
                          animation_frame="Month", orientation="h",
                          range_x=[0, race["Revenue"].max()*1.1],
                          title="Product Revenue Over Time")
        fig_race.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = animation_speed
        fig_race.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = int(animation_speed*0.6)
        st.plotly_chart(fig_race, use_container_width=True)

with tab4:
    st.dataframe(fdf[["Date", "Product Name", "Category", "Quantity", "Unit Price", "Revenue", "Payment Status"]], use_container_width=True)
    st.download_button("Download CSV", fdf.to_csv(index=False), file_name="sales.csv")

if auto_refresh:
    time.sleep(30)
    st.rerun()
