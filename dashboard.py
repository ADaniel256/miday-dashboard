import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

CURRENCY = "UGX"
st.set_page_config(page_title="MiDAY Insights", layout="wide", initial_sidebar_state="collapsed")

# --- Coffee theme CSS (safe, stripped) ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #F5EBE0 0%, #E8D5C4 40%, #D7CCC8 100%);
    }
    .metric-card {
        background: rgba(255,248,240,0.5);
        backdrop-filter: blur(8px);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(139,90,43,0.1);
        box-shadow: 0 8px 24px rgba(0,0,0,0.04);
        margin: 6px 0;
        transition: 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(139,90,43,0.3);
        box-shadow: 0 12px 32px rgba(0,0,0,0.06);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2C1810;
        font-family: 'Inter', sans-serif;
    }
    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        color: #5D4037;
        letter-spacing: 0.05em;
        opacity: 0.7;
    }
    .fancy-header {
        font-size: 3.5rem;
        font-weight: 700;
        color: #2C1810;
        font-family: 'Inter', sans-serif;
    }
    .fancy-sub {
        color: #5D4037;
        font-size: 1rem;
        letter-spacing: 0.1em;
    }
    .fancy-divider {
        height: 2px;
        background: linear-gradient(90deg, #8B5A2B, #D4A373);
        margin: 12px 0 24px 0;
        border-radius: 4px;
        opacity: 0.4;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(255,248,240,0.3);
        border-radius: 16px;
        padding: 4px;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(255,248,240,0.5) !important;
        border-radius: 12px;
        font-weight: 600;
    }
    .chart-container {
        background: rgba(255,248,240,0.3);
        border-radius: 20px;
        padding: 16px;
        border: 1px solid rgba(139,90,43,0.06);
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# --- Data Loader ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8D3xOvu7VXVuwSSydp7I5TsrUnHd2dlzDy1g3MWaW1y0ojhEi4Ftvoi1ev4ZkeQeX4glRCzQvklsj/pub?gid=2071886823&single=true&output=csv"  # <-- REPLACE

@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["Date"])
    df["Date"] = pd.to_datetime(df["Date"])
    for col in ["Unit Price", "Revenue", "COGS"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["Quantity"] = pd.to_numeric(df.get("Quantity", 0), errors="coerce").fillna(0).astype(int)
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

# --- Header ---
st.markdown("<div class='fancy-header'>☕ MiDAY System</div>", unsafe_allow_html=True)
st.markdown("<div class='fancy-sub'>Live Business Intelligence</div>", unsafe_allow_html=True)
st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("🔍 Filters")
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

# --- Metrics ---
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Revenue", fmt_currency(fdf["Revenue"].sum()))
c2.metric("Profit", fmt_currency(fdf["Profit"].sum()))
margin = (fdf["Profit"].sum() / fdf["Revenue"].sum() * 100) if fdf["Revenue"].sum() > 0 else 0
c3.metric("Margin", f"{margin:.1f}%")
c4.metric("Orders", len(fdf))
c5.metric("Units", fdf["Quantity"].sum())

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Products", "Trends", "Raw"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            daily = fdf.groupby("Date")["Revenue"].sum().reset_index()
            fig = px.line(daily, x="Date", y="Revenue", title="Revenue Trend", markers=True,
                          color_discrete_sequence=["#8B5A2B"])
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            cat_sum = fdf.groupby("Category")["Revenue"].sum().reset_index()
            fig = px.pie(cat_sum, names="Category", values="Revenue", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("Product Performance")
    prod = fdf.groupby("Product Name")["Revenue"].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(prod, x="Product Name", y="Revenue", title="Revenue by Product", color_discrete_sequence=["#8B5A2B"])
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
    fig = px.bar(agg, x="Period", y="Revenue", title=f"Revenue ({gran})", color_discrete_sequence=["#8B5A2B"])
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.dataframe(fdf[["Date", "Product Name", "Category", "Quantity", "Unit Price", "Revenue", "Payment Status"]], use_container_width=True)

st.sidebar.caption("Data refreshed: " + datetime.now().strftime("%H:%M:%S"))
