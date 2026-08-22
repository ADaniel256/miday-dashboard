import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import time

CURRENCY = "UGX"
st.set_page_config(page_title="MiDAY Insights", layout="wide", initial_sidebar_state="collapsed", page_icon="☕")

# --- Dark mode state ---
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ====================================================
# COFFEE THEME CSS (same as before – kept concise)
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
    </style>
    """, unsafe_allow_html=True)

# ---- Shared CSS (glass, fonts, animations) ----
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
        color: #8B5A2B;
        background: rgba(139,90,43,0.10);
        padding: 4px 16px 4px 12px;
        border-radius: 30px;
        border: 1px solid rgba(139,90,43,0.15);
        backdrop-filter: blur(4px);
        margin-left: 12px;
    }
    .live-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #8B5A2B;
        animation: pulseDot 1.5s ease-in-out infinite;
        box-shadow: 0 0 12px rgba(139,90,43,0.3);
    }
    @keyframes pulseDot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.8); }
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
# DATA LOADER – Sales + Expenses
# ============================================================
CSV_URL_SALES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8D3xOvu7VXVuwSSydp7I5TsrUnHd2dlzDy1g3MWaW1y0ojhEi4Ftvoi1ev4ZkeQeX4glRCzQvklsj/pub?gid=2071886823&single=true&output=csv"      # <-- REPLACE
CSV_URL_EXPENSES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8D3xOvu7VXVuwSSydp7I5TsrUnHd2dlzDy1g3MWaW1y0ojhEi4Ftvoi1ev4ZkeQeX4glRCzQvklsj/pub?gid=1512430292&single=true&output=csv"      # <-- REPLACE

@st.cache_data(ttl=600)
def load_sales():
    df = pd.read_csv(CSV_URL_SALES)
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

@st.cache_data(ttl=600)
def load_expenses():
    df = pd.read_csv(CSV_URL_EXPENSES)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["Date"], how="all")
    df = df[df["Date"].notna()]
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    # Map columns – adjust if your sheet has different names
    # Typical columns: Date, Expense Type, Category, Description, Amount (UGX)
    # We'll rename if needed
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

sales_df = load_sales()
expenses_df = load_expenses()

if sales_df.empty:
    st.error("Sales data not loaded. Check your CSV URL.")
    st.stop()

# --- Merge sales and expenses by date for aggregated KPIs ---
# Compute total expenses per day to combine with sales
expenses_daily = expenses_df.groupby("Date")["Amount"].sum().reset_index()
expenses_daily.columns = ["Date", "Expenses"]

# Merge with sales data (left join)
merged = pd.merge(sales_df, expenses_daily, on="Date", how="left")
merged["Expenses"] = merged["Expenses"].fillna(0)

# Compute Net Profit (Revenue - COGS - Expenses)
merged["Net Profit"] = merged["Revenue"] - merged["COGS"] - merged["Expenses"]

# We'll use merged for the Overview KPIs and trends, but keep separate for detailed views.

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

# Filter sales
filtered_sales = sales_df[
    (sales_df["Date"] >= pd.to_datetime(date_range[0])) &
    (sales_df["Date"] <= pd.to_datetime(date_range[1])) &
    (sales_df["Category"].isin(categories)) &
    (sales_df["Payment Status"].isin(statuses)) &
    (sales_df["Product Name"].isin(products))
]

# Filter expenses to same date range
filtered_expenses = expenses_df[
    (expenses_df["Date"] >= pd.to_datetime(date_range[0])) &
    (expenses_df["Date"] <= pd.to_datetime(date_range[1]))
]

# --- Compute KPIs ---
total_revenue = filtered_sales["Revenue"].sum()
total_cogs = filtered_sales["COGS"].sum()
total_expenses = filtered_expenses["Amount"].sum()
gross_profit = total_revenue - total_cogs
net_profit = gross_profit - total_expenses
margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
net_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

# --- Tabs (now 5 tabs) ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Overview", "📊 Products", "📅 Trends", "🧾 Expenses", "📋 Raw"])

# ===== TAB 1: OVERVIEW =====
with tab1:
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Revenue", fmt_currency(total_revenue))
    col2.metric("Gross Profit", fmt_currency(gross_profit))
    col3.metric("Margin", f"{margin:.1f}%")
    col4.metric("Expenses", fmt_currency(total_expenses))
    col5.metric("Net Profit", fmt_currency(net_profit))
    col6.metric("Net Margin", f"{net_margin:.1f}%")

    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            # Revenue vs Expenses trend
            daily_rev = filtered_sales.groupby("Date")["Revenue"].sum().reset_index()
            daily_exp = filtered_expenses.groupby("Date")["Amount"].sum().reset_index()
            merged_daily = pd.merge(daily_rev, daily_exp, on="Date", how="outer").fillna(0)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=merged_daily["Date"], y=merged_daily["Revenue"], name="Revenue", marker_color="#8B5A2B"))
            fig.add_trace(go.Bar(x=merged_daily["Date"], y=merged_daily["Amount"], name="Expenses", marker_color="#D4A373"))
            fig.update_layout(barmode="group", title="Revenue vs Expenses", height=350,
                              plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", transition_duration=500)
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor="rgba(139,90,43,0.06)")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            # Expense breakdown by category
            exp_cat = filtered_expenses.groupby("Expense Category")["Amount"].sum().reset_index()
            if not exp_cat.empty:
                fig = px.pie(exp_cat, names="Expense Category", values="Amount", hole=0.4,
                             title="Expense Breakdown", color_discrete_sequence=px.colors.qualitative.Set2)
                fig.update_layout(height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", transition_duration=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No expense data for this period.")
            st.markdown('</div>', unsafe_allow_html=True)

# ===== TAB 2: PRODUCTS (unchanged from before) =====
with tab2:
    st.subheader("📦 Product Performance")
    prod = filtered_sales.groupby("Product Name").agg({"Revenue": "sum", "Profit": "sum", "Quantity": "sum"}).reset_index()
    prod["Margin %"] = (prod["Profit"] / prod["Revenue"] * 100).round(1).fillna(0)
    prod = prod.sort_values("Revenue", ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=prod["Product Name"], y=prod["Revenue"], name="Revenue", marker_color="#8B5A2B"))
    fig.add_trace(go.Bar(x=prod["Product Name"], y=prod["Profit"], name="Gross Profit", marker_color="#D4A373"))
    fig.add_trace(go.Scatter(x=prod["Product Name"], y=prod["Margin %"], name="Margin %", mode="lines+markers",
                             yaxis="y2", line=dict(color="#F1C40F", width=3), marker=dict(size=10)))
    fig.update_layout(
        yaxis=dict(title=f"{CURRENCY}", side="left"),
        yaxis2=dict(overlaying="y", side="right", title="Margin %"),
        barmode="group",
        height=450,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        transition_duration=500
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(139,90,43,0.06)")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📋 Detailed Product Data"):
        st.dataframe(prod.style.format({
            "Revenue": fmt_currency,
            "Profit": fmt_currency,
            "Quantity": "{:,}",
            "Margin %": "{:.1f}%"
        }), use_container_width=True)

    st.download_button("⬇️ Download Product Report (CSV)", prod.to_csv(index=False), file_name="product_performance.csv")

# ===== TAB 3: TRENDS (Sales) =====
with tab3:
    st.subheader("📅 Sales Trends and Breakdowns")
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
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        transition_duration=500
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(139,90,43,0.06)")
    st.plotly_chart(fig, use_container_width=True)

    # Animated bar race (sales)
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
            exp_trend = filtered_expenses.groupby("Date")["Amount"].sum().reset_index()
            if not exp_trend.empty:
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
            exp_cat = filtered_expenses.groupby("Expense Category")["Amount"].sum().reset_index().sort_values("Amount", ascending=False)
            if not exp_cat.empty:
                fig = px.bar(exp_cat, x="Expense Category", y="Amount", title="Expense by Category",
                             color_discrete_sequence=["#8B5A2B"])
                fig.update_layout(yaxis_title=CURRENCY, height=350,
                                  plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", transition_duration=500)
                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(showgrid=True, gridcolor="rgba(139,90,43,0.06)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No expense data.")
            st.markdown('</div>', unsafe_allow_html=True)

    # Detailed expense table
    with st.expander("📋 Detailed Expense Transactions"):
        if not filtered_expenses.empty:
            st.dataframe(filtered_expenses[["Date", "Expense Category", "Expense Type", "Description", "Amount", "Status"]]
                         .style.format({"Amount": fmt_currency}), use_container_width=True)
        else:
            st.info("No expenses in this period.")

    # Download expenses
    st.download_button("⬇️ Download Expenses CSV", filtered_expenses.to_csv(index=False), file_name="expenses.csv")

# ===== TAB 5: RAW DATA (Sales) =====
with tab5:
    st.subheader("📋 Sales Transaction Details")
    st.dataframe(
        filtered_sales[["Date", "Product Name", "Category", "Quantity", "Unit Price",
                        "Revenue", "COGS", "Profit", "Margin %", "Payment Status", "Notes"]]
        .style.format({
            "Unit Price": fmt_currency,
            "Revenue": fmt_currency,
            "COGS": fmt_currency,
            "Profit": fmt_currency,
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
