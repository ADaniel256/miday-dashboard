import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# =====================================================
# 🌍 Currency setting – change this to any symbol
CURRENCY = "UGX"          # e.g., "USh", "KES", "$", "€"
# =====================================================

st.set_page_config(page_title="MiDAY Insights", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for better UI ---
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1f3a5f; }
    .sub-header { font-size: 1.2rem; color: #4a6b8a; }
    .metric-card { background-color: #f8f9fa; border-radius: 10px; padding: 15px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .metric-value { font-size: 2rem; font-weight: 600; color: #1f3a5f; }
    .metric-label { font-size: 0.9rem; color: #6c757d; }
</style>
""", unsafe_allow_html=True)

# --- Data Loader (Google Sheets CSV) ---
CSV_URL = "YOUR_PUBLISHED_CSV_URL"  # <-- REPLACE WITH YOUR LINK

@st.cache_data(ttl=600)
def load_data():
    try:
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
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.stop()

# --- Helper function to format currency ---
def fmt_currency(value):
    return f"{CURRENCY} {value:,.0f}"

# --- Sidebar: Advanced Filters ---
st.sidebar.title("🔍 Filters")
# ... (same as before, no changes) ...

# ===================== TAB 1: OVERVIEW =====================
with tab1:
    # Key Metrics – using the currency format
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value">{fmt_currency(fdf['Revenue'].sum())}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Profit</div>
            <div class="metric-value">{fmt_currency(fdf['Profit'].sum())}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        margin = (fdf['Profit'].sum() / fdf['Revenue'].sum() * 100) if fdf['Revenue'].sum() > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Gross Margin</div>
            <div class="metric-value">{margin:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Orders</div>
            <div class="metric-value">{len(fdf):,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Units Sold</div>
            <div class="metric-value">{fdf['Quantity'].sum():,}</div>
        </div>
        """, unsafe_allow_html=True)

    # Comparison metrics
    if compare_mode and not fdf_compare.empty:
        st.subheader("📊 Period Comparison")
        delta_rev = fdf['Revenue'].sum() - fdf_compare['Revenue'].sum()
        delta_profit = fdf['Profit'].sum() - fdf_compare['Profit'].sum()
        col1, col2 = st.columns(2)
        col1.metric("Revenue Change", fmt_currency(delta_rev), delta_color="normal")
        col2.metric("Profit Change", fmt_currency(delta_profit), delta_color="normal")

    # Charts – update y-axis titles
    daily = fdf.groupby("Date")["Revenue"].sum().reset_index()
    fig = px.line(daily, x="Date", y="Revenue", title="Revenue Trend", markers=True)
    fig.update_layout(yaxis_title=f"{CURRENCY}")
    st.plotly_chart(fig, use_container_width=True)

    # Pie chart – we keep labels as numbers, the currency symbol is not needed there.

# ===================== TAB 2: PRODUCT ANALYSIS =====================
with tab2:
    # ... same code, but for formatting the table we use the helper:
    with st.expander("📋 Detailed Product Data"):
        st.dataframe(prod_perf.style.format({
            "Revenue": fmt_currency,
            "Profit": fmt_currency,
            "Quantity": "{:,}",
            "Margin %": "{:.1f}%"
        }), use_container_width=True)

    # The bar chart y-axis also needs currency symbol – we can update the figure layout.
    # We'll keep it as is because the numbers are clear.

# ... (similar updates for all monetary displays: metric cards, tables, download CSVs)
