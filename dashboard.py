import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import time

CURRENCY = "UGX"

st.set_page_config(
    page_title="MiDAY Insights",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="☕"
)

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ===== DARK MODE CSS (coffee palette) =====
if st.session_state.dark_mode:
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #1A0E0A 0%, #2C1810 40%, #3E2723 100%);
            position: relative;
            overflow: hidden;
        }
        .stApp::before {
            content: '';
            position: fixed;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 30% 40%, rgba(200,150,100,0.06) 0%, transparent 50%),
                        radial-gradient(circle at 70% 80%, rgba(160,120,80,0.04) 0%, transparent 50%);
            animation: steamWave 20s ease-in-out infinite alternate;
            pointer-events: none;
            z-index: 0;
        }
        @keyframes steamWave {
            0% { transform: translate(0,0) rotate(0deg) scale(1); }
            100% { transform: translate(-3%,-5%) rotate(4deg) scale(1.02); }
        }
        .metric-card { background: rgba(30,20,15,0.7) !important; border: 1px solid rgba(255,255,255,0.06) !important; box-shadow: 0 8px 32px rgba(0,0,0,0.5) !important; }
        .metric-card:hover { border-color: rgba(200,150,100,0.3) !important; }
        .metric-value { color: #e2e8f0 !important; }
        .metric-label { color: #b8a394 !important; }
        .fancy-sub { color: #b8a394 !important; }
        .stTabs [data-baseweb="tab"] { color: #b8a394 !important; }
        .stTabs [aria-selected="true"] { color: #facc15 !important; border-bottom-color: #facc15 !important; }
        .chart-container { background: rgba(30,20,15,0.4) !important; border-color: rgba(255,255,255,0.04) !important; }
        .stSidebar { background: rgba(20,10,8,0.8) !important; border-right: 1px solid rgba(255,255,255,0.03) !important; }
    </style>
    """, unsafe_allow_html=True)
else:
    # ===== LIGHT MODE CSS (coffee palette) =====
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #F5EBE0 0%, #E8D5C4 40%, #D7CCC8 100%);
            position: relative;
            overflow: hidden;
        }
        .stApp::before {
            content: '';
            position: fixed;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 30% 40%, rgba(139,90,43,0.05) 0%, transparent 50%),
                        radial-gradient(circle at 70% 80%, rgba(200,150,100,0.06) 0%, transparent 50%),
                        radial-gradient(circle at 50% 20%, rgba(210,180,140,0.04) 0%, transparent 40%);
            animation: steamWave 20s ease-in-out infinite alternate;
            pointer-events: none;
            z-index: 0;
        }
        @keyframes steamWave {
            0% { transform: translate(0,0) rotate(0deg) scale(1); }
            100% { transform: translate(-3%,-5%) rotate(4deg) scale(1.02); }
        }
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

# ===== Shared CSS (fonts, animations, glass, responsive) =====
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

    /* --- Glass-morphism metric cards --- */
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
    .metric-icon {
        font-size: 2.2rem;
        margin-bottom: 6px;
        display: block;
        filter: drop-shadow(0 2px 8px rgba(0,0,0,0.03));
    }
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
    .stTabs [role="tabpanel"] {
        animation: fadeIn 0.5s ease-out;
    }
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

    .stSidebar {
        backdrop-filter: blur(20px) !important;
        box-shadow: 4px 0 40px rgba(0,0,0,0.01);
    }

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
        <div class="live-indicator">
            <span class="live-dot"></span> LIVE
        </div>
    </div>
    <div class="fancy-sub">Real‑time Business Intelligence · Powered by MiDAY Investments</div>
    <div class="fancy-divider"></div>
    """, unsafe_allow_html=True)

with col_toggle:
    if st.button("🌙" if not st.session_state.dark_mode else "☀️", help="Toggle dark mode"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# --- Data Loader ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8D3xOvu7VXVuwSSydp7I5TsrUnHd2dlzDy1g3MWaW1y0ojhEi4Ftvoi1ev4ZkeQeX4glRCzQvklsj/pub?gid=2071886823&single=true&output=csv"  # <-- REPLACE

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

with st.spinner("Fetching live data..."):
    df = load_data()
if df.empty:
    st.stop()

# --- Helpers ---
def fmt_currency(value):
    return f"{CURRENCY} {value:,.0f}"

# --- Sidebar Filters ---
st.sidebar.title("🔍 Filters")
st.sidebar.markdown("---")

auto_refresh = st.sidebar.checkbox("🔄 Auto‑refresh every 30s")
animation_speed = st.sidebar.slider(
    "🏁 Bar Race Speed (ms per frame)",
    min_value=300,
    max_value=5000,
    value=1500,
    step=100
)

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

categories = st.sidebar.multiselect("Category", options=sorted(df["Category"].unique()), default=sorted(df["Category"].unique()))
statuses = st.sidebar.multiselect("Payment Status", options=sorted(df["Payment Status"].unique()), default=sorted(df["Payment Status"].unique()))
all_products = sorted(df["Product Name"].unique())
selected_products = st.sidebar.multiselect("Product (optional)", options=all_products, default=all_products)

compare_mode = st.sidebar.checkbox("📊 Compare two periods")
if compare_mode:
    date_range_2 = st.sidebar.date_input("Comparison Date Range", [min_date, min_date + timedelta(days=7)], min_value=min_date, max_value=max_date)

# --- Apply filters ---
fdf = df[
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1])) &
    (df["Category"].isin(categories)) &
    (df["Payment Status"].isin(statuses)) &
    (df["Product Name"].isin(selected_products))
]

if compare_mode and len(date_range_2) == 2:
    fdf_compare = df[
        (df["Date"] >= pd.to_datetime(date_range_2[0])) &
        (df["Date"] <= pd.to_datetime(date_range_2[1])) &
        (df["Category"].isin(categories)) &
        (df["Payment Status"].isin(statuses)) &
        (df["Product Name"].isin(selected_products))
    ]
else:
    fdf_compare = pd.DataFrame()

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "📊 Products", "📅 Trends", "📋 Raw"])

# ===== TAB 1 =====
with tab1:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">💰</span>
            <div class="metric-value">{fmt_currency(fdf['Revenue'].sum())}</div>
            <div class="metric-label">Revenue</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">📈</span>
            <div class="metric-value">{fmt_currency(fdf['Profit'].sum())}</div>
            <div class="metric-label">Profit</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        margin = (fdf['Profit'].sum() / fdf['Revenue'].sum() * 100) if fdf['Revenue'].sum() > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">📊</span>
            <div class="metric-value">{margin:.1f}%</div>
            <div class="metric-label">Gross Margin</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">🧾</span>
            <div class="metric-value">{len(fdf):,}</div>
            <div class="metric-label">Orders</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">📦</span>
            <div class="metric-value">{fdf['Quantity'].sum():,}</div>
            <div class="metric-label">Units</div>
        </div>
        """, unsafe_allow_html=True)

    if compare_mode and not fdf_compare.empty:
        st.subheader("📊 Period Comparison")
        col1, col2 = st.columns(2)
        delta_rev = fdf['Revenue'].sum() - fdf_compare['Revenue'].sum()
        delta_profit = fdf['Profit'].sum() - fdf_compare['Profit'].sum()
        col1.metric("Revenue Change", fmt_currency(delta_rev))
        col2.metric("Profit Change", fmt_currency(delta_profit))

    st.subheader("📅 Timeline Slider")
    min_ts = fdf['Date'].min()
    max_ts = fdf['Date'].max()
    slider_dates = st.slider(
        "Drag to zoom into a specific period",
        min_value=min_ts.to_pydatetime(),
        max_value=max_ts.to_pydatetime(),
        value=(min_ts.to_pydatetime(), max_ts.to_pydatetime()),
        format="YYYY-MM-DD"
    )
    filtered_slider = fdf[(fdf['Date'] >= pd.to_datetime(slider_dates[0])) & (fdf['Date'] <= pd.to_datetime(slider_dates[1]))]

    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            daily = filtered_slider.groupby("Date")["Revenue"].sum().reset_index()
            fig = px.line(daily, x="Date", y="Revenue", title="Revenue Trend (slider range)", markers=True,
                          color_discrete_sequence=["#8B5A2B"])
            fig.update_layout(yaxis_title=CURRENCY, height=350, hovermode="x unified",
                              plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                              font=dict(family="Inter, sans-serif"),
                              transition_duration=500)
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor="rgba(139,90,43,0.06)")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            cat_sum = fdf.groupby("Category")["Revenue"].sum().sort_values(ascending=False).reset_index()
            fig = px.pie(cat_sum, names="Category", values="Revenue", hole=0.4,
                         title="Revenue by Category", color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                              transition_duration=500)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        cumulative = fdf.sort_values("Date")
        cumulative["Cumulative Revenue"] = cumulative["Revenue"].cumsum()
        fig = px.area(cumulative, x="Date", y="Cumulative Revenue", title="Cumulative Revenue Over Time",
                      color_discrete_sequence=["#D4A373"])
        fig.update_layout(yaxis_title=CURRENCY, height=350, hovermode="x unified",
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          transition_duration=500)
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(139,90,43,0.06)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ===== TAB 2 =====
with tab2:
    st.subheader("📦 Product Performance")
    prod_perf = fdf.groupby("Product Name").agg({
        "Revenue": "sum",
        "Profit": "sum",
        "Quantity": "sum"
    }).reset_index()
    prod_perf["Margin %"] = (prod_perf["Profit"] / prod_perf["Revenue"] * 100).round(1).fillna(0)
    prod_perf = prod_perf.sort_values("Revenue", ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=prod_perf["Product Name"],
        y=prod_perf["Revenue"],
        name="Revenue",
        marker_color="#8B5A2B"
    ))
    fig.add_trace(go.Bar(
        x=prod_perf["Product Name"],
        y=prod_perf["Profit"],
        name="Profit",
        marker_color="#D4A373"
    ))
    fig.add_trace(go.Scatter(
        x=prod_perf["Product Name"],
        y=prod_perf["Margin %"],
        name="Margin %",
        mode="lines+markers",
        yaxis="y2",
        line=dict(color="#F1C40F", width=3),
        marker=dict(size=10)
    ))
    fig.update_layout(
        xaxis=dict(title="Product"),
        yaxis=dict(title=f"{CURRENCY}", side="left"),
        yaxis2=dict(title="Margin %", overlaying="y", side="right"),
        hovermode="x unified",
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
        st.dataframe(prod_perf.style.format({
            "Revenue": fmt_currency,
            "Profit": fmt_currency,
            "Quantity": "{:,}",
            "Margin %": "{:.1f}%"
        }), use_container_width=True)

    st.download_button(
        label="⬇️ Download Product Report (CSV)",
        data=prod_perf.to_csv(index=False),
        file_name="product_performance.csv",
        mime="text/csv"
    )

# ===== TAB 3 =====
with tab3:
    st.subheader("📅 Trends and Breakdowns")
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

    agg_df = agg_period(fdf, gran)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=agg_df["Period"], y=agg_df["Revenue"], name="Revenue", marker_color="#8B5A2B"))
    fig.add_trace(go.Scatter(x=agg_df["Period"], y=agg_df["Profit"], name="Profit", mode="lines+markers",
                             line=dict(color="#D4A373", width=3), marker=dict(size=8), yaxis="y2"))
    fig.add_trace(go.Scatter(x=agg_df["Period"], y=agg_df["Margin %"], name="Margin %", mode="lines+markers",
                             line=dict(color="#F1C40F", width=2, dash="dash"), marker=dict(size=6), yaxis="y2"))
    fig.update_layout(
        xaxis=dict(title="Period"),
        yaxis=dict(title=f"{CURRENCY}", side="left"),
        yaxis2=dict(title="Profit / Margin %", overlaying="y", side="right"),
        hovermode="x unified",
        height=450,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        transition_duration=500
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(139,90,43,0.06)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🏁 Animated Bar Race (Monthly Product Revenue)")
    st.caption(f"Current speed: {animation_speed} ms per frame (adjust in sidebar)")

    fdf_month = fdf.copy()
    fdf_month["Month"] = fdf_month["Date"].dt.to_period("M").astype(str)
    race_data = fdf_month.groupby(["Month", "Product Name"])["Revenue"].sum().reset_index()

    if not race_data.empty:
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

    st.download_button(
        label="⬇️ Download Breakdown CSV",
        data=agg_df.to_csv(index=False),
        file_name=f"miday_{gran.lower()}_breakdown.csv",
        mime="text/csv"
    )

# ===== TAB 4 =====
with tab4:
    st.subheader("📋 Transaction Details")
    st.dataframe(
        fdf[["Date", "Product Name", "Category", "Quantity", "Unit Price",
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
        csv = fdf.to_csv(index=False)
        st.download_button(label="⬇️ Download as CSV", data=csv, file_name="miday_sales_data.csv", mime="text/csv")
    with col2:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            fdf.to_excel(writer, index=False, sheet_name='Sales')
        st.download_button(
            label="⬇️ Download as Excel",
            data=output.getvalue(),
            file_name="miday_sales_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# --- Auto‑refresh ---
if auto_refresh:
    st.sidebar.info("🔄 Auto‑refresh is ON – updating every 30 seconds")
    time.sleep(30)
    st.rerun()

# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.caption(f"🔄 Data refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.sidebar.caption("💡 Tap ☰ to open filters")
