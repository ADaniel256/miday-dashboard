import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="MiDAY Live", layout="wide")
st.title("☕ MiDAY System - Live Dashboard")

FILE_ID = "15_pQ_xaSupdBiMghX5tlkyjciKuGk34J-sRgOdJl9_M"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{FILE_ID}/export?format=csv"

@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df = df.dropna(subset=["Date"], how="all")
    df = df[df["Date"].notna()]
    for col in ["Unit Price", "Revenue", "COGS"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", "").str.replace("#N/A", "")
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0).astype(int)
    df["Category"] = df["Category"].fillna("Uncategorized")
    df["Payment Status"] = df["Payment Status"].fillna("Unknown")
    return df

df = load_data()
if df.empty:
    st.stop()

st.sidebar.header("🔍 Filters")
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

min_d, max_d = df["Date"].min().date(), df["Date"].max().date()
dr = st.sidebar.date_input("Date Range", [min_d, max_d], min_value=min_d, max_value=max_d)
cat = st.sidebar.selectbox("Category", ["All"] + sorted(df["Category"].unique().tolist()))
stat = st.sidebar.selectbox("Payment", ["All"] + sorted(df["Payment Status"].unique().tolist()))

fdf = df.copy()
if len(dr) == 2:
    fdf = fdf[(fdf["Date"] >= pd.to_datetime(dr[0])) & (fdf["Date"] <= pd.to_datetime(dr[1]))]
if cat != "All": fdf = fdf[fdf["Category"] == cat]
if stat != "All": fdf = fdf[fdf["Payment Status"] == stat]

c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Revenue", f"${fdf['Revenue'].sum():,.0f}")
c2.metric("📦 Units", f"{fdf['Quantity'].sum():,}")
c3.metric("🧾 Orders", f"{len(fdf):,}")
avg = fdf['Revenue'].sum() / len(fdf) if len(fdf) > 0 else 0
c4.metric("📈 Avg Order", f"${avg:,.0f}")

col1, col2 = st.columns(2)
with col1:
    daily = fdf.groupby("Date")["Revenue"].sum().reset_index()
    fig = px.bar(daily, x="Date", y="Revenue", title="Revenue Over Time", color_discrete_sequence=["#FF6B6B"])
    st.plotly_chart(fig, use_container_width=True)
with col2:
    cat_sum = fdf.groupby("Category")["Revenue"].sum().sort_values(ascending=False).reset_index()
    fig = px.pie(cat_sum, names="Category", values="Revenue", title="Revenue by Category", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    top = fdf.groupby("Product Name")["Revenue"].sum().sort_values(ascending=False).head(8).reset_index()
    fig = px.bar(top, y="Product Name", x="Revenue", title="Top 8 Products", orientation="h", color="Revenue")
    st.plotly_chart(fig, use_container_width=True)
with col4:
    pay = fdf.groupby("Payment Status")["Revenue"].sum().reset_index()
    fig = px.pie(pay, names="Payment Status", values="Revenue", title="Revenue by Status", 
                 color_discrete_sequence=["#2ECC71", "#F1C40F", "#E74C3C"])
    st.plotly_chart(fig, use_container_width=True)

with st.expander("📋 View Raw Data"):
    st.dataframe(fdf[["Date", "Product Name", "Category", "Quantity", "Unit Price", "Revenue", "Payment Status", "Notes"]],
                 use_container_width=True, height=400)
