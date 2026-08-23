import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import time
import requests

CURRENCY = "UGX"
st.set_page_config(page_title="MiDAY Insights", layout="wide", initial_sidebar_state="collapsed", page_icon="☕")

# --- Dark mode state ---
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ====================================================
# COFFEE THEME CSS (with green LIVE indicator)
# ====================================================
if st.session_state.dark_mode:
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #1A0E0A 0%, #2C1810 50%, #3E2723 100%); }
        .metric-card { background: rgba(30,20,15,0.7) !important; border: 1px solid rgba(255,255,255,0.06) !important; box-shadow: 0 8px 32px rgba(0,0,0,0.5) !important; }
        .metric-card:hover { border-color: rgba(200,150,100,0.3) !important; }
        .metric-value { color: #e2e8f0 !important; }
        .metric-label { color: #b8a394 !important; }
        .fancy-sub { color: #b8a394 !important; }
        .stTabs [data-baseweb="tab"] { color: #b8a394 !important; }
        .stTabs [aria-selected="true"] { color: #facc15 !important; border-bottom-color: #facc15 !important; }
        .chart-container { background: rgba(30,20,15,0.4) !important; border-color: rgba(255,255,255,0.04) !important; }
        .stSidebar { background: rgba(20,10,8,0.8) !important; border-right: 1px solid rgba(255,255,255,0.03) !important; }
        .stApp { color: #e2e8f0 !important; }
        .inventory-alert { background: rgba(200,50,50,0.2) !important; border-left: 4px solid #ff6b6b !important; padding: 10px !important; border-radius: 8px !important; }
        .inventory-ok { background: rgba(50,200,50,0.1) !important; border-left: 4px solid #51cf66 !important; padding: 10px !important; border-radius: 8px !important; }
        .inventory-warning { background: rgba(200,200,50,0.15) !important; border-left: 4px solid #fcc419 !important; padding: 10px !important; border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #F5EBE0 0%, #E8D5C4 50%, #D7CCC8 100%); }
        .metric-card { background: rgba(255,248,240,0.5); box-shadow: 0 8px 32px rgba(0,0,0,0.04); }
        .metric-card:hover { border-color: rgba(139,90,43,0.3); }
        .metric-value { color: #2C1810; }
        .metric-label { color: #5D4037; }
        .fancy-sub { color: #5D4037; }
        .stTabs [data-baseweb="tab"] { color: #5D4037; }
        .stTabs [aria-selected="true"] { color: #2C1810; border-bottom-color: #8B5A2B; }
        .chart-container { background: rgba(255,248,240,0.3); border-color: rgba(139,90,43,0.10); }
        .stSidebar { background: rgba(255,248,240,0.5) !important; border-right: 1px solid rgba(139,90,43,0.05) !important; }
        .inventory-alert { background: rgba(255,200,200,0.3) !important; border-left: 4px solid #ff6b6b !important; padding: 10px !important; border-radius: 8px !important; }
        .inventory-ok { background: rgba(200,255,200,0.2) !important; border-left: 4px solid #51cf66 !important; padding: 10px !important; border-radius: 8px !important; }
        .inventory-warning { background: rgba(255,255,200,0.25) !important; border-left: 4px solid #fcc419 !important; padding: 10px !important; border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# ---- Shared CSS ----
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Space+Grotesk:wght@400;600;700&display=swap');

    .fancy-header {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 4rem;
        background: linear-gradient(135deg, #2C1810 0%, #8B5A2B 40%, #D4A373 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 6s ease-in-out infinite alternate;
        letter-spacing: -0.02em;
        line-height: 1.1;
        margin-bottom: -4px;
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        100% { background-position: 100% 50%; }
    }
    .fancy-sub {
        font-family: 'Inter', sans-serif;
        font-weight: 300;
        font-size: 1.1rem;
        color: #5D4037;
        letter-spacing: 0.2em;
        margin-top: 4px;
    }
    .fancy-divider {
        height: 3px;
        background: linear-gradient(90deg, #8B5A2B, #D4A373, #F5EBE0);
        border-radius: 10px;
        margin-top: 8px;
        margin-bottom: 28px;
        width: 100%;
        opacity: 0.5;
        animation: dividerPulse 3s ease-in-out infinite;
    }
    @keyframes dividerPulse {
        0%, 100% { opacity: 0.4; transform: scaleX(1); }
        50% { opacity: 0.8; transform: scaleX(1.01); }
    }

    .live-indicator {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        font-weight: 600;
        color: #10b981;
        background: rgba(16, 185, 129, 0.1);
        padding: 4px 16px 4px 12px;
        border-radius: 30px;
        border: 1px solid rgba(16, 185, 129, 0.2);
        backdrop-filter: blur(4px);
        margin-left: 12px;
    }
    .live-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10b981;
        animation: pulseDot 1s ease-in-out infinite;
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
    }
    @keyframes pulseDot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.3; transform: scale(0.7); }
    }

    .metric-card {
        border-radius: 24px;
        padding: 24px 16px;
        text-align: center;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(139,90,43,0.10);
        transition: all 0.4s cubic-bezier(0.4,0,0.2,1);
        margin: 8px 0;
        position: relative;
        overflow: hidden;
        transform: translateY(0);
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: -100%;
        left: -100%;
        width: 300%;
        height: 300%;
        background: radial-gradient(circle at 30% 40%, rgba(255,255,255,0.15) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.6s;
        pointer-events: none;
    }
    .metric-card:hover::before {
        opacity: 1;
        animation: shimmer 0.6s ease-out;
    }
    @keyframes shimmer {
        0% { transform: translate(-30%, -30%) scale(0.5); opacity: 0; }
        50% { opacity: 0.5; }
        100% { transform: translate(30%, 30%) scale(1.2); opacity: 0; }
    }
    .metric-card:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 16px 64px rgba(0,0,0,0.06);
    }
    .metric-icon { font-size: 2.2rem; margin-bottom: 6px; display: block; }
    .metric-value {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 2.4rem;
        letter-spacing: -0.02em;
        line-height: 1.2;
        transition: color 0.3s;
        animation: fadeInUp 0.6s ease-out;
    }
    .metric-label {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 6px;
        opacity: 0.7;
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(255,248,240,0.2);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 6px;
        border: 1px solid rgba(139,90,43,0.08);
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 0.9rem;
        padding: 10px 24px;
        border-radius: 14px;
        transition: all 0.3s;
        background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(255,248,240,0.4) !important;
        font-weight: 600;
        box-shadow: 0 4px 16px rgba(0,0,0,0.02);
        backdrop-filter: blur(8px);
    }
    .stTabs [role="tabpanel"] { animation: fadeIn 0.5s ease-out; }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .chart-container {
        backdrop-filter: blur(8px);
        border-radius: 24px;
        padding: 20px;
        border: 1px solid rgba(139,90,43,0.06);
        margin-bottom: 20px;
        transition: all 0.3s;
        box-shadow: 0 4px 20px rgba(0,0,0,0.01);
    }
    .chart-container:hover {
        border-color: rgba(139,90,43,0.15);
        box-shadow: 0 8px 40px rgba(139,90,43,0.03);
    }
    .stSidebar { backdrop-filter: blur(20px) !important; box-shadow: 4px 0 40px rgba(0,0,0,0.01); }

    .status-badge {
        display: inline-block;
        padding: 2px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-in-stock { background: #51cf66; color: white; }
    .status-low-stock { background: #fcc419; color: #2C1810; }
    .status-out-of-stock { background: #ff6b6b; color: white; }

    @media (max-width: 600px) {
        .fancy-header { font-size: 2.6rem !important; }
        .fancy-sub { font-size: 0.8rem !important; }
        .metric-value { font-size: 1.6rem !important; }
        .metric-label { font-size: 0.65rem !important; }
        .metric-card { padding: 14px 10px !important; }
        .row-widget.stColumns { flex-wrap: wrap !important; }
        .row-widget.stColumns > div { flex: 1 1 45% !important; min-width: 130px !important; }
        .js-plotly-plot .plotly .main-svg { height: 350px !important; }
        .live-indicator { font-size: 0.7rem; padding: 2px 12px; }
    }
</style>
""", unsafe_allow_html=True)

# --- Header with dark toggle ---
col_title, col_toggle = st.columns([4, 1])
with col_title:
    st.markdown("""
    <div style="display: flex; align-items: center; flex-wrap: wrap;">
        <div class="fancy-header">☕ MiDAY System</div>
        <div class="live-indicator"><span class="live-dot"></span> LIVE</div>
    </div>
    <div class="fancy-sub">Real‑time Business Intelligence · Powered by Google Sheets</div>
    <div class="fancy-divider"></div>
    """, unsafe_allow_html=True)

with col_toggle:
    if st.button("🌙" if not st.session_state.dark_mode else "☀️", help="Toggle dark mode"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ============================================================
# DATA LOADERS
# ============================================================
CSV_URL_SALES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8D3xOvu7VXVuwSSydp7I5TsrUnHd2dlzDy1g3MWaW1y0ojhEi4Ftvoi1ev4ZkeQeX4glRCzQvklsj/pub?gid=2071886823&single=true&output=csv"
CSV_URL_EXPENSES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8D3xOvu7VXVuwSSydp7I5TsrUnHd2dlzDy1g3MWaW1y0ojhEi4Ftvoi1ev4ZkeQeX4glRCzQvklsj/pub?gid=1512430292&single=true&output=csv"
CSV_URL_INVENTORY = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8D3xOvu7VXVuwSSydp7I5TsrUnHd2dlzDy1g3MWaW1y0ojhEi4Ftvoi1ev4ZkeQeX4glRCzQvklsj/pub?gid=1059614497&single=true&output=csv"

def load_csv_with_fallback(url):
    """Load CSV from URL with fallback using requests if pandas fails."""
    try:
        return pd.read_csv(url)
    except Exception as e:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            from io import StringIO
            return pd.read_csv(StringIO(response.text))
        except Exception as e2:
            st.error(f"Error loading CSV: {e2}")
            return pd.DataFrame()

@st.cache_data(ttl=600)
def load_sales():
    df = load_csv_with_fallback(CSV_URL_SALES)
    if df.empty:
        return df
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
    df["Agent"] = df.get("Agent", "").fillna("")  # Keep Agent column
    df["Profit"] = df["Revenue"] - df["COGS"]
    df["Profit per Unit"] = (df["Profit"] / df["Quantity"]).fillna(0).round(0)
    df["Margin %"] = (df["Profit"] / df["Revenue"] * 100).round(1).fillna(0)
    return df

@st.cache_data(ttl=600)
def load_expenses():
    df = load_csv_with_fallback(CSV_URL_EXPENSES)
    if df.empty:
        return df
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["Date"], how="all")
    df = df[df["Date"].notna()]
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    if "Amount (UGX)" in df.columns:
        df["Amount"] = pd.to_numeric(df["Amount (UGX)"], errors="coerce").fillna(0)
    elif "Amount" in df.columns:
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    else:
        df["Amount"] = 0
    df["Expense Category"] = df.get("Category", "Uncategorized").fillna("Uncategorized")
    df["Expense Type"] = df.get("Expense Type", "Other").fillna("Other")
    df["Status"] = df.get("Status", "Unknown").fillna("Unknown")
    return df

@st.cache_data(ttl=600)
def load_inventory():
    """Loads inventory and returns both raw data and latest-per-item aggregated data."""
    df = load_csv_with_fallback(CSV_URL_INVENTORY)
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["Item Name"], how="all")
    df = df[df["Item Name"].notna()]
    
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
    else:
        df["Date"] = pd.Timestamp.now()
    
    for col in ["Quantity Received", "Unit Cost (UGX)", "Total Cost (UGX)", "Quantity Used", "Remaining Stock", "Reorder Level"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            df[col] = 0
    
    df["Current Stock"] = df["Remaining Stock"]
    
    if df["Total Cost (UGX)"].sum() != 0:
        df["Total Value"] = df["Total Cost (UGX)"]
    else:
        df["Total Value"] = df["Current Stock"] * df["Unit Cost (UGX)"]
    
    def get_status(row):
        stock = row.get("Current Stock", 0)
        reorder = row.get("Reorder Level", 0)
        if stock <= 0:
            return "Out of Stock"
        elif reorder > 0 and stock <= reorder:
            return "Low Stock"
        else:
            return "In Stock"
    df["Status"] = df.apply(get_status, axis=1)
    df["Item Category"] = df.get("Item Category", "Uncategorized").fillna("Uncategorized")
    
    latest = df.sort_values("Date", ascending=False).drop_duplicates(subset=["Item Name"], keep="first").copy()
    return df, latest

sales_df = load_sales()
expenses_df = load_expenses()
inventory_raw, inventory_latest = load_inventory()

if sales_df.empty:
    st.error("Sales data not loaded. Check your CSV URL.")
    st.stop()

def fmt_currency(v):
    return f"{CURRENCY} {v:,.0f}"

# --- Sidebar Filters ---
st.sidebar.title("🔍 Filters")
st.sidebar.markdown("---")

auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh every 30s")
animation_speed = st.sidebar.slider("🏁 Bar Race Speed (ms per frame)", 300, 5000, 1500, 100)

min_date = sales_df["Date"].min().date()
max_date = sales_df["Date"].max().date()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date])

categories = st.sidebar.multiselect("Category", sorted(sales_df["Category"].unique()), default=sorted(sales_df["Category"].unique()))
statuses = st.sidebar.multiselect("Payment Status", sorted(sales_df["Payment Status"].unique()), default=sorted(sales_df["Payment Status"].unique()))
products = st.sidebar.multiselect("Product (optional)", sorted(sales_df["Product Name"].unique()), default=sorted(sales_df["Product Name"].unique()))

# Agent filter (NEW)
all_agents = sorted([a for a in sales_df["Agent"].unique() if a and str(a).strip() != ""])
agent_filter = st.sidebar.multiselect("Agent (optional)", options=all_agents, default=all_agents) if all_agents else []

expense_types = st.sidebar.multiselect(
    "Expense Type",
    options=sorted(expenses_df["Expense Type"].unique()) if not expenses_df.empty else [],
    default=sorted(expenses_df["Expense Type"].unique()) if not expenses_df.empty else []
)

inventory_categories = st.sidebar.multiselect(
    "Inventory Category",
    options=sorted(inventory_latest["Item Category"].unique()) if not inventory_latest.empty else [],
    default=sorted(inventory_latest["Item Category"].unique()) if not inventory_latest.empty else []
)

# Filter sales
filtered_sales = sales_df[
    (sales_df["Date"] >= pd.to_datetime(date_range[0])) &
    (sales_df["Date"] <= pd.to_datetime(date_range[1])) &
    (sales_df["Category"].isin(categories)) &
    (sales_df["Payment Status"].isin(statuses)) &
    (sales_df["Product Name"].isin(products))
]
if agent_filter:
    filtered_sales = filtered_sales[filtered_sales["Agent"].isin(agent_filter)]

filtered_expenses = expenses_df[
    (expenses_df["Date"] >= pd.to_datetime(date_range[0])) &
    (expenses_df["Date"] <= pd.to_datetime(date_range[1])) &
    (expenses_df["Expense Type"].isin(expense_types))
] if not expenses_df.empty else pd.DataFrame()

if not inventory_latest.empty:
    filtered_inventory_latest = inventory_latest[inventory_latest["Item Category"].isin(inventory_categories)]
    filtered_inventory_raw = inventory_raw[inventory_raw["Item Category"].isin(inventory_categories)]
else:
    filtered_inventory_latest = pd.DataFrame()
    filtered_inventory_raw = pd.DataFrame()

# --- Compute KPIs ---
total_revenue = filtered_sales["Revenue"].sum()
total_cogs = filtered_sales["COGS"].sum()
total_expenses = filtered_expenses["Amount"].sum() if not filtered_expenses.empty else 0
gross_profit = total_revenue - total_cogs
net_profit = gross_profit - total_expenses
margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
net_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

# Inventory KPIs
total_inventory_value = filtered_inventory_latest["Total Value"].sum() if not filtered_inventory_latest.empty else 0
total_items = len(filtered_inventory_latest) if not filtered_inventory_latest.empty else 0
low_stock_items = len(filtered_inventory_latest[filtered_inventory_latest["Status"] == "Low Stock"]) if not filtered_inventory_latest.empty else 0
out_of_stock_items = len(filtered_inventory_latest[filtered_inventory_latest["Status"] == "Out of Stock"]) if not filtered_inventory_latest.empty else 0

# --- Tabs (7 tabs now) ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📈 Overview", "📊 Products", "📅 Trends", "🧾 Expenses", "📦 Inventory", "👥 Agents", "📋 Raw"])

# ===== TAB 1: OVERVIEW (with Daily Cash Flow) =====
with tab1:
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Revenue", fmt_currency(total_revenue))
    col2.metric("Gross Profit", fmt_currency(gross_profit))
    col3.metric("Margin", f"{margin:.1f}%")
    col4.metric("Expenses", fmt_currency(total_expenses))
    col5.metric("Net Profit", fmt_currency(net_profit))
    col6.metric("Net Margin", f"{net_margin:.1f}%")

    # ---- Daily Cash Flow ----
    with st.container():
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("💰 Daily Cash Flow (Revenue – Expenses)")
        daily_rev = filtered_sales.groupby("Date")["Revenue"].sum().reset_index()
        daily_exp = filtered_expenses.groupby("Date")["Amount"].sum().reset_index() if not filtered_expenses.empty else pd.DataFrame(columns=["Date", "Amount"])
        merged_daily = pd.merge(daily_rev, daily_exp, on="Date", how="outer").fillna(0)
        merged_daily["Net Cash Flow"] = merged_daily["Revenue"] - merged_daily["Amount"]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=merged_daily["Date"], y=merged_daily["Revenue"], name="Revenue", marker_color="#8B5A2B"))
        fig.add_trace(go.Bar(x=merged_daily["Date"], y=merged_daily["Amount"], name="Expenses", marker_color="#D4A373"))
        fig.add_trace(go.Scatter(x=merged_daily["Date"], y=merged_daily["Net Cash Flow"], name="Net Cash Flow",
                                 mode="lines+markers", line=dict(color="#10b981", width=3), marker=dict(size=8), yaxis="y2"))
        fig.update_layout(
            barmode="group",
            title="Daily Revenue vs Expenses with Net Cash Flow",
            height=400,
            yaxis=dict(title=f"{CURRENCY}", side="left"),
            yaxis2=dict(title=f"Net {CURRENCY}", overlaying="y", side="right"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", transition_duration=500
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(139,90,43,0.06)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            daily_rev_2 = filtered_sales.groupby("Date")["Revenue"].sum().reset_index()
            fig = px.line(daily_rev_2, x="Date", y="Revenue", title="Revenue Trend", markers=True,
                          color_discrete_sequence=["#8B5A2B"])
            fig.update_layout(yaxis_title=CURRENCY, height=350,
                              plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", transition_duration=500)
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor="rgba(139,90,43,0.06)")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            breakdown_type = st.radio(
                "Breakdown expenses by:",
                ["Category", "Expense Type"],
                horizontal=True,
                key="expense_breakdown_overview"
            )
            if not filtered_expenses.empty:
                if breakdown_type == "Category":
                    exp_group = filtered_expenses.groupby("Expense Category")["Amount"].sum().reset_index()
                    x_col = "Expense Category"
                else:
                    exp_group = filtered_expenses.groupby("Expense Type")["Amount"].sum().reset_index()
                    x_col = "Expense Type"
                if not exp_group.empty:
                    fig = px.pie(exp_group, names=x_col, values="Amount", hole=0.4,
                                 title=f"Expenses by {breakdown_type}",
                                 color_discrete_sequence=px.colors.qualitative.Set2)
                    fig.update_layout(height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", transition_duration=500)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No expense data for this period.")
            else:
                st.info("No expense data available.")
            st.markdown('</div>', unsafe_allow_html=True)

# ===== TAB 2: PRODUCTS (with Profit per Unit) =====
with tab2:
    st.subheader("📦 Product Performance")
    prod = filtered_sales.groupby("Product Name").agg({
        "Revenue": "sum",
        "Profit": "sum",
        "Quantity": "sum",
        "Profit per Unit": "mean"  # average profit per unit
    }).reset_index()
    prod["Margin %"] = (prod["Profit"] / prod["Revenue"] * 100).round(1).fillna(0)
    prod["Revenue per Unit"] = (prod["Revenue"] / prod["Quantity"]).fillna(0).round(0)
    prod = prod.sort_values("Revenue", ascending=False)

    # Chart: Revenue vs Profit per Unit
    fig = go.Figure()
    fig.add_trace(go.Bar(x=prod["Product Name"], y=prod["Revenue"], name="Revenue", marker_color="#8B5A2B"))
    fig.add_trace(go.Scatter(x=prod["Product Name"], y=prod["Profit per Unit"], name="Profit per Unit",
                             mode="lines+markers", yaxis="y2",
                             line=dict(color="#10b981", width=3), marker=dict(size=10)))
    fig.update_layout(
        yaxis=dict(title=f"{CURRENCY} (Revenue)", side="left"),
        yaxis2=dict(title=f"{CURRENCY} (Profit per Unit)", overlaying="y", side="right"),
        barmode="group",
        height=450,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", transition_duration=500
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(139,90,43,0.06)")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📋 Detailed Product Data"):
        st.dataframe(prod.style.format({
            "Revenue": fmt_currency,
            "Profit": fmt_currency,
            "Quantity": "{:,}",
            "Profit per Unit": fmt_currency,
            "Revenue per Unit": fmt_currency,
            "Margin %": "{:.1f}%"
        }), use_container_width=True)

    st.download_button("⬇️ Download Product Report (CSV)", prod.to_csv(index=False), file_name="product_performance.csv")

# ===== TAB 3: TRENDS (with Day-of-Week) =====
with tab3:
    st.subheader("📅 Sales Trends and Breakdowns")

    # ---- Day-of-Week Sales ----
    with st.container():
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📆 Sales by Day of Week")
        dow = filtered_sales.copy()
        dow["Day of Week"] = dow["Date"].dt.day_name()
        dow_agg = dow.groupby("Day of Week")["Revenue"].sum().reset_index()
        # Order days correctly
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow_agg["Day of Week"] = pd.Categorical(dow_agg["Day of Week"], categories=days_order, ordered=True)
        dow_agg = dow_agg.sort_values("Day of Week")
        fig = px.bar(dow_agg, x="Day of Week", y="Revenue", title="Revenue by Day of Week",
                     color_discrete_sequence=["#8B5A2B"])
        fig.update_layout(height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", transition_duration=500)
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(139,90,43,0.06)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    gran = st.radio("Granularity", ["Daily", "Weekly", "Monthly"], horizontal=True)

    def agg_period(df, period):
        df_copy = df.copy()
        if period == "Daily":
            df_copy["Period"] = df_copy["Date"].dt.date
        elif period == "Weekly":
            df_copy["Period"] = df_copy["Date"].dt.to_period("W").apply(lambda r: r.start_time.date())
        else:
            df_copy["Period"] = df_copy["Date"].dt.to_period("M").apply(lambda r: r.start_time.date())
        agg = df_copy.groupby("Period").agg({
            "Revenue": "sum",
            "Profit": "sum",
            "Quantity": "sum",
            "Date": "count"
        }).rename(columns={"Date": "Orders"}).reset_index()
        agg["Margin %"] = (agg["Profit"] / agg["Revenue"] * 100).round(1).fillna(0)
        return agg

    agg_df = agg_period(filtered_sales, gran)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=agg_df["Period"], y=agg_df["Revenue"], name="Revenue", marker_color="#8B5A2B"))
    fig.add_trace(go.Scatter(x=agg_df["Period"], y=agg_df["Profit"], name="Gross Profit", mode="lines+markers",
                             line=dict(color="#D4A373", width=3), marker=dict(size=8), yaxis="y2"))
    fig.add_trace(go.Scatter(x=agg_df["Period"], y=agg_df["Margin %"], name="Margin %", mode="lines+markers",
                             line=dict(color="#F1C40F", width=2, dash="dash"), marker=dict(size=6), yaxis="y2"))
    fig.update_layout(
        yaxis=dict(title=f"{CURRENCY}", side="left"),
        yaxis2=dict(overlaying="y", side="right", title="Profit / Margin %"),
        height=450,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", transition_duration=500
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(139,90,43,0.06)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🏁 Animated Bar Race (Monthly Product Revenue)")
    st.caption(f"Current speed: {animation_speed} ms per frame (adjust in sidebar)")

    fdf_month = filtered_sales.copy()
    fdf_month["Month"] = fdf_month["Date"].dt.to_period("M").astype(str)
    race_data = fdf_month.groupby(["Month", "Product Name"])["Revenue"].sum().reset_index()

    if not race_data.empty and len(race_data["Month"].unique()) > 1:
        months_sorted = sorted(race_data["Month"].unique())
        race_data["Month"] = pd.Categorical(race_data["Month"], categories=months_sorted, ordered=True)
        race_data = race_data.sort_values("Month")
        fig_race = px.bar(
            race_data,
            x="Revenue",
            y="Product Name",
            color="Product Name",
            orientation="h",
            animation_frame="Month",
            range_x=[0, race_data["Revenue"].max() * 1.2],
            title="Products ranked by Revenue over time",
            labels={"Revenue": f"{CURRENCY}", "Product Name": "Product"}
        )
        fig_race.update_layout(
            showlegend=False,
            height=500,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            transition_duration=700
        )
        fig_race.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = animation_speed
        fig_race.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = int(animation_speed * 0.6)
        st.plotly_chart(fig_race, use_container_width=True)
    else:
        st.info("Not enough data for the animated race (need multiple months and products).")

    st.subheader("📋 Period Breakdown")
    display = agg_df.copy()
    display["Period"] = display["Period"].astype(str)
    display["Revenue"] = display["Revenue"].apply(fmt_currency)
    display["Profit"] = display["Profit"].apply(fmt_currency)
    display["Margin %"] = display["Margin %"].apply(lambda x: f"{x:.1f}%")
    st.dataframe(display, use_container_width=True)
    st.download_button("⬇️ Download Breakdown CSV", agg_df.to_csv(index=False), file_name=f"miday_{gran.lower()}_breakdown.csv")

# ===== TAB 4: EXPENSES =====
with tab4:
    st.subheader("🧾 Expense Analysis")
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if not filtered_expenses.empty:
                exp_trend = filtered_expenses.groupby("Date")["Amount"].sum().reset_index()
                fig = px.line(exp_trend, x="Date", y="Amount", title="Expense Trend", markers=True,
                              color_discrete_sequence=["#D4A373"])
                fig.update_layout(yaxis_title=CURRENCY, height=350,
                                  plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", transition_duration=500)
                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(showgrid=True, gridcolor="rgba(139,90,43,0.06)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No expense data for this period.")
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            exp_breakdown_tab = st.radio(
                "Breakdown by:",
                ["Category", "Expense Type"],
                horizontal=True,
                key="expense_breakdown_tab"
            )
            if not filtered_expenses.empty:
                if exp_breakdown_tab == "Category":
                    exp_group_tab = filtered_expenses.groupby("Expense Category")["Amount"].sum().reset_index().sort_values("Amount", ascending=False)
                    x_col_tab = "Expense Category"
                else:
                    exp_group_tab = filtered_expenses.groupby("Expense Type")["Amount"].sum().reset_index().sort_values("Amount", ascending=False)
                    x_col_tab = "Expense Type"

                if not exp_group_tab.empty:
                    fig = px.bar(exp_group_tab, x=x_col_tab, y="Amount", title=f"Expenses by {exp_breakdown_tab}",
                                 color_discrete_sequence=["#8B5A2B"])
                    fig.update_layout(yaxis_title=CURRENCY, height=350,
                                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", transition_duration=500)
                    fig.update_xaxes(showgrid=False)
                    fig.update_yaxes(showgrid=True, gridcolor="rgba(139,90,43,0.06)")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No expense data.")
            else:
                st.info("No expense data available.")
            st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("📋 Detailed Expense Transactions"):
        if not filtered_expenses.empty:
            st.dataframe(filtered_expenses[["Date", "Expense Category", "Expense Type", "Description", "Amount", "Status"]]
                         .style.format({"Amount": fmt_currency}), use_container_width=True)
        else:
            st.info("No expenses in this period.")

    st.download_button("⬇️ Download Expenses CSV", filtered_expenses.to_csv(index=False), file_name="expenses.csv")

# ===== TAB 5: INVENTORY =====
with tab5:
    st.subheader("📦 Inventory Management")

    if inventory_raw.empty:
        st.warning("No inventory data loaded. Please check your Inventory CSV URL.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Inventory Value", fmt_currency(total_inventory_value))
        col2.metric("Total Items", total_items)
        col3.metric("Low Stock Items", low_stock_items, delta="⚠️ Needs attention" if low_stock_items > 0 else None)
        col4.metric("Out of Stock", out_of_stock_items, delta="🚫 Reorder needed" if out_of_stock_items > 0 else None)

        inv_view = st.radio(
            "View table:",
            ["All Items", "Raw Materials Only", "Finished Goods Only"],
            horizontal=True
        )

        if inv_view == "Raw Materials Only":
            display_inv_raw = filtered_inventory_raw[filtered_inventory_raw["Item Category"].str.lower().str.contains("raw")]
        elif inv_view == "Finished Goods Only":
            display_inv_raw = filtered_inventory_raw[filtered_inventory_raw["Item Category"].str.lower().str.contains("finished")]
        else:
            display_inv_raw = filtered_inventory_raw

        col1, col2 = st.columns(2)
        with col1:
            with st.container():
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                if not filtered_inventory_latest.empty:
                    inv_value_by_cat = filtered_inventory_latest.groupby("Item Category")["Total Value"].sum().reset_index()
                    fig = px.pie(inv_value_by_cat, names="Item Category", values="Total Value", hole=0.4,
                                 title="Inventory Value by Category (Current)",
                                 color_discrete_sequence=px.colors.qualitative.Set2)
                    fig.update_layout(height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", transition_duration=500)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No inventory data for charts.")
                st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            with st.container():
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                if not filtered_inventory_latest.empty:
                    status_counts = filtered_inventory_latest["Status"].value_counts().reset_index()
                    status_counts.columns = ["Status", "Count"]
                    color_map = {"In Stock": "#51cf66", "Low Stock": "#fcc419", "Out of Stock": "#ff6b6b"}
                    fig = px.bar(status_counts, x="Status", y="Count", title="Stock Status Distribution (Current)",
                                 color="Status", color_discrete_map=color_map)
                    fig.update_layout(height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", transition_duration=500)
                    fig.update_xaxes(showgrid=False)
                    fig.update_yaxes(showgrid=True, gridcolor="rgba(139,90,43,0.06)")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No inventory data for charts.")
                st.markdown('</div>', unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if not filtered_inventory_latest.empty:
                stock_sorted = filtered_inventory_latest.sort_values("Current Stock", ascending=False).head(20)
                fig = px.bar(stock_sorted, x="Item Name", y="Current Stock", title="Stock Levels by Item (Current)",
                             color="Status", color_discrete_map={"In Stock": "#51cf66", "Low Stock": "#fcc419", "Out of Stock": "#ff6b6b"})
                fig.update_layout(height=400, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", transition_duration=500)
                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(showgrid=True, gridcolor="rgba(139,90,43,0.06)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No inventory data for chart.")
            st.markdown('</div>', unsafe_allow_html=True)

        low_stock_items_df = filtered_inventory_latest[filtered_inventory_latest["Status"].isin(["Low Stock", "Out of Stock"])]
        if not low_stock_items_df.empty:
            st.subheader("⚠️ Items Needing Attention (Current)")
            for _, row in low_stock_items_df.iterrows():
                status_class = "inventory-alert" if row["Status"] == "Out of Stock" else "inventory-warning"
                st.markdown(f"""
                <div class="{status_class}">
                    <strong>{row['Item Name']}</strong> – {row['Status']} (Current: {row['Current Stock']:.0f}, Reorder Level: {row.get('Reorder Level', 0):.0f})
                </div>
                """, unsafe_allow_html=True)

        with st.expander("📋 Complete Inventory History (All Rows)"):
            if not display_inv_raw.empty:
                table_cols = ["Date", "Item Name", "Item Category", "Current Stock", "Unit Cost (UGX)", "Total Value", "Reorder Level", "Status"]
                available_table_cols = [col for col in table_cols if col in display_inv_raw.columns]
                st.dataframe(
                    display_inv_raw[available_table_cols].style.format({
                        "Unit Cost (UGX)": fmt_currency,
                        "Total Value": fmt_currency,
                        "Current Stock": "{:.0f}",
                        "Reorder Level": "{:.0f}"
                    }),
                    use_container_width=True
                )
            else:
                st.info("No inventory rows match the selected view.")

        st.download_button(
            "⬇️ Download Inventory CSV (All Rows)",
            display_inv_raw.to_csv(index=False) if not display_inv_raw.empty else "",
            file_name="inventory_history.csv"
        )

# ===== TAB 6: AGENTS (NEW) =====
with tab6:
    st.subheader("👥 Agent Performance")

    # Filter out empty agent values
    agent_data = filtered_sales[filtered_sales["Agent"].notna() & (filtered_sales["Agent"] != "")]

    if agent_data.empty:
        st.info("No agent data available. Please add agent names to your sales records.")
    else:
        # KPIs for agents
        total_agents = agent_data["Agent"].nunique()
        total_agent_revenue = agent_data["Revenue"].sum()
        total_agent_orders = len(agent_data)
        avg_order_value = total_agent_revenue / total_agent_orders if total_agent_orders > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Agents", total_agents)
        col2.metric("Agent Revenue", fmt_currency(total_agent_revenue))
        col3.metric("Total Orders", total_agent_orders)
        col4.metric("Avg Order Value", fmt_currency(avg_order_value))

        # Agent performance table
        agent_perf = agent_data.groupby("Agent").agg({
            "Revenue": "sum",
            "Profit": "sum",
            "Quantity": "sum",
            "Date": "count"
        }).rename(columns={"Date": "Orders"}).reset_index()
        agent_perf["Avg Order Value"] = (agent_perf["Revenue"] / agent_perf["Orders"]).fillna(0).round(0)
        agent_perf["Profit per Order"] = (agent_perf["Profit"] / agent_perf["Orders"]).fillna(0).round(0)
        agent_perf["Margin %"] = (agent_perf["Profit"] / agent_perf["Revenue"] * 100).round(1).fillna(0)
        agent_perf = agent_perf.sort_values("Revenue", ascending=False)

        # Chart: Agent Revenue
        fig = go.Figure()
        fig.add_trace(go.Bar(x=agent_perf["Agent"], y=agent_perf["Revenue"], name="Revenue", marker_color="#8B5A2B"))
        fig.add_trace(go.Scatter(x=agent_perf["Agent"], y=agent_perf["Avg Order Value"], name="Avg Order Value",
                                 mode="lines+markers", yaxis="y2",
                                 line=dict(color="#10b981", width=3), marker=dict(size=10)))
        fig.update_layout(
            yaxis=dict(title=f"{CURRENCY} (Revenue)", side="left"),
            yaxis2=dict(title=f"{CURRENCY} (Avg Order)", overlaying="y", side="right"),
            barmode="group",
            height=450,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", transition_duration=500
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(139,90,43,0.06)")
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 Detailed Agent Performance"):
            st.dataframe(agent_perf.style.format({
                "Revenue": fmt_currency,
                "Profit": fmt_currency,
                "Avg Order Value": fmt_currency,
                "Profit per Order": fmt_currency,
                "Orders": "{:,}",
                "Quantity": "{:,}",
                "Margin %": "{:.1f}%"
            }), use_container_width=True)

        st.download_button("⬇️ Download Agent Report (CSV)", agent_perf.to_csv(index=False), file_name="agent_performance.csv")

# ===== TAB 7: RAW DATA =====
with tab7:
    st.subheader("📋 Sales Transaction Details")
    st.dataframe(
        filtered_sales[["Date", "Product Name", "Category", "Quantity", "Unit Price",
                        "Revenue", "COGS", "Profit", "Profit per Unit", "Margin %", "Payment Status", "Agent", "Notes"]]
        .style.format({
            "Unit Price": fmt_currency,
            "Revenue": fmt_currency,
            "COGS": fmt_currency,
            "Profit": fmt_currency,
            "Profit per Unit": fmt_currency,
            "Margin %": "{:.1f}%",
            "Quantity": "{:,}"
        }),
        use_container_width=True,
        height=500
    )

    col1, col2 = st.columns(2)
    with col1:
        csv = filtered_sales.to_csv(index=False)
        st.download_button("⬇️ Download Sales CSV", data=csv, file_name="miday_sales_data.csv", mime="text/csv")
    with col2:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            filtered_sales.to_excel(writer, index=False, sheet_name='Sales')
        st.download_button(
            label="⬇️ Download Sales Excel",
            data=output.getvalue(),
            file_name="miday_sales_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# --- Auto-refresh ---
if auto_refresh:
    st.sidebar.info("🔄 Auto-refresh is ON – updating every 30 seconds")
    time.sleep(30)
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption(f"🔄 Data refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.sidebar.caption("💡 Tap ☰ to open filters")
