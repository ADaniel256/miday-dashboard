import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# =====================================================
# 🌍 Currency setting
CURRENCY = "UGX"
# =====================================================

st.set_page_config(
    page_title="MiDAY Insights",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="☕"
)

# --- Silicon Valley Grade CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Space+Grotesk:wght@400;600;700&display=swap');

    * { margin: 0; padding: 0; box-sizing: border-box; }

    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e9edf5 100%);
        transition: background 0.3s ease;
    }

    .dark-mode .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    .dark-mode .metric-card {
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3) !important;
    }
    .dark-mode .metric-value { color: #e2e8f0 !important; }
    .dark-mode .metric-label { color: #94a3b8 !important; }
    .dark-mode .fancy-sub { color: #94a3b8 !important; }
    .dark-mode .stTabs [data-baseweb="tab"] { color: #94a3b8 !important; }
    .dark-mode .stTabs [aria-selected="true"] {
        color: #facc15 !important;
        border-bottom-color: #facc15 !important;
    }
    .dark-mode .chart-container {
        background: rgba(30, 41, 59, 0.3) !important;
        border-color: rgba(255,255,255,0.05) !important;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 20px;
        padding: 20px 12px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin: 6px 0;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.6s;
        pointer-events: none;
    }
    .metric-card:hover::before { opacity: 1; }
    .metric-card:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.12);
        border-color: rgba(255, 255, 255, 0.6);
    }
    .metric-icon { font-size: 2rem; margin-bottom: 4px; display: block; }
    .metric-value {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 2.2rem;
        color: #0f172a;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    .metric-label {
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        font-size: 0.85rem;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }

    .fancy-header {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 3.8rem;
        background: linear-gradient(135deg, #0f172a 0%, #3b82f6 40%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
        line-height: 1.1;
        text-shadow: 0 4px 24px rgba(59, 130, 246, 0.15);
        margin-bottom: -4px;
    }
    .fancy-sub {
        font-family: 'Inter', sans-serif;
        font-weight: 300;
        font-size: 1.1rem;
        color: #64748b;
        letter-spacing: 0.15em;
        margin-top: 4px;
    }
    .fancy-divider {
        height: 3px;
        background: linear-gradient(90deg, #3b82f6, #10b981, #facc15);
        border-radius: 10px;
        margin-top: 8px;
        margin-bottom: 24px;
        width: 100%;
        opacity: 0.6;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(255,255,255,0.3);
        backdrop-filter: blur(8px);
        border-radius: 16px;
        padding: 6px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 0.9rem;
        padding: 8px 20px;
        border-radius: 12px;
        color: #475569;
        transition: all 0.2s;
        background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(255,255,255,0.6) !important;
        color: #0f172a !important;
        font-weight: 600;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        backdrop-filter: blur(4px);
    }
    .dark-mode .stTabs [data-baseweb="tab-list"] {
        background: rgba(30, 41, 59, 0.4);
        border-color: rgba(255,255,255,0.05);
    }
    .dark-mode .stTabs [aria-selected="true"] {
        background: rgba(255,255,255,0.08) !important;
        color: #facc15 !important;
    }

    .chart-container {
        background: rgba(255,255,255,0.4);
        backdrop-filter: blur(8px);
        border-radius: 20px;
        padding: 16px;
        border: 1px solid rgba(255,255,255,0.2);
        margin-bottom: 16px;
        transition: all 0.3s;
    }
    .chart-container:hover {
        border-color: rgba(59, 130, 246, 0.3);
        box-shadow: 0 8px 30px rgba(0,0,0,0.04);
    }

    @media (max-width: 600px) {
        .fancy-header { font-size: 2.4rem !important; }
        .fancy-sub { font-size: 0.85rem !important; }
        .metric-value { font-size: 1.5rem !important; }
        .metric-label { font-size: 0.7rem !important; }
        .metric-card { padding: 12px 8px !important; }
        .row-widget.stColumns { flex-wrap: wrap !important; }
        .row-widget.stColumns > div { flex: 1 1 45% !important; min-width: 130px !important; }
        .js-plotly-plot .plotly .main-svg { height: 350px !important; }
    }
</style>
""", unsafe_allow_html=True)

# --- Dark mode toggle ---
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

col_title, col_toggle = st.columns([4, 1])
with col_title:
    st.markdown("""
    <div class="fancy-header">☕ MiDAY System</div>
    <div class="fancy-sub">Live Business Intelligence · Powered by MiDAY</div>
    <div class="fancy-divider"></div>
    """, unsafe_allow_html=True)

with col_toggle:
    if st.button("🌙" if not st.session_state.dark_mode else "☀️", help="Toggle dark mode"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

if st.session_state.dark_mode:
    st.markdown('<body class="dark-mode">', unsafe_allow_html=True)

# --- Data Loader ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8D3xOvu7VXVuwSSydp7I5TsrUnHd2dlzDy1g3MWaW1y0ojhEi4Ftvoi1ev4ZkeQeX4glRCzQvklsj/pub?gid=2071886823&single=true&output=csv"  # <-- REPLACE WITH YOUR LINK

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

# --- Sidebar ---
st.sidebar.title("🔍 Filters")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()
date_range = st.sidebar.date_input(
    "Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

categories = st.sidebar.multiselect(
    "Category",
    options=sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique())
)

statuses = st.sidebar.multiselect(
    "Payment Status",
    options=sorted(df["Payment Status"].unique()),
    default=sorted(df["Payment Status"].unique())
)

all_products = sorted(df["Product Name"].unique())
selected_products = st.sidebar.multiselect(
    "Product (optional)",
    options=all_products,
    default=all_products
)

compare_mode = st.sidebar.checkbox("📊 Compare two periods")
if compare_mode:
    date_range_2 = st.sidebar.date_input(
        "Comparison Date Range",
        [min_date, min_date + timedelta(days=7)],
        min_value=min_date,
        max_value=max_date
    )

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

# ============================================================
# TAB 1: OVERVIEW
# ============================================================
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

    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            daily = fdf.groupby("Date")["Revenue"].sum().reset_index()
            fig = px.line(daily, x="Date", y="Revenue", title="Revenue Trend", markers=True,
                          color_discrete_sequence=["#3b82f6"])
            fig.update_layout(yaxis_title=CURRENCY, height=350, hovermode="x unified",
                              plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            cat_sum = fdf.groupby("Category")["Revenue"].sum().sort_values(ascending=False).reset_index()
            fig = px.pie(cat_sum, names="Category", values="Revenue", hole=0.4,
                         title="Revenue by Category", color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        cumulative = fdf.sort_values("Date")
        cumulative["Cumulative Revenue"] = cumulative["Revenue"].cumsum()
        fig = px.area(cumulative, x="Date", y="Cumulative Revenue", title="Cumulative Revenue Over Time",
                      color_discrete_sequence=["#10b981"])
        fig.update_layout(yaxis_title=CURRENCY, height=350, hovermode="x unified",
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# TAB 2: PRODUCTS
# ============================================================
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
        marker_color="#FF6B6B"
    ))
    fig.add_trace(go.Bar(
        x=prod_perf["Product Name"],
        y=prod_perf["Profit"],
        name="Profit",
        marker_color="#2ECC71"
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
        paper_bgcolor="rgba(0,0,0,0)"
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
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

# ============================================================
# TAB 3: TRENDS
# ============================================================
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
    fig.add_trace(go.Bar(x=agg_df["Period"], y=agg_df["Revenue"], name="Revenue", marker_color="#FF6B6B"))
    fig.add_trace(go.Scatter(x=agg_df["Period"], y=agg_df["Profit"], name="Profit", mode="lines+markers",
                             line=dict(color="#2ECC71", width=3), marker=dict(size=8), yaxis="y2"))
    fig.add_trace(go.Scatter(x=agg_df["Period"], y=agg_df["Margin %"], name="Margin %", mode="lines+markers",
                             line=dict(color="#F1C40F", width=2, dash="dash"), marker=dict(size=6), yaxis="y2"))
    fig.update_layout(
        xaxis=dict(title="Period"),
        yaxis=dict(title=f"{CURRENCY}", side="left"),
        yaxis2=dict(title="Profit / Margin %", overlaying="y", side="right"),
        hovermode="x unified",
        height=450,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
    st.plotly_chart(fig, use_container_width=True)

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

# ============================================================
# TAB 4: RAW DATA
# ============================================================
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
        st.download_button(
            label="⬇️ Download as CSV",
            data=csv,
            file_name="miday_sales_data.csv",
            mime="text/csv"
        )
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

# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.caption(f"🔄 Data refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.sidebar.caption("💡 Tap ☰ to open filters")
