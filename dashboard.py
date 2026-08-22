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

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1f3a5f; }
    .sub-header { font-size: 1.2rem; color: #4a6b8a; }
    .metric-card { background-color: #f8f9fa; border-radius: 10px; padding: 15px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .metric-value { font-size: 2rem; font-weight: 600; color: #1f3a5f; }
    .metric-label { font-size: 0.9rem; color: #6c757d; }
</style>
""", unsafe_allow_html=True)

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

df = load_data()
if df.empty:
    st.stop()

# --- Helper function ---
def fmt_currency(value):
    return f"{CURRENCY} {value:,.0f}"

# --- Sidebar Filters ---
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

# Apply filters
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

# --- Tabs (CORRECTED: tab1, tab2, tab3, tab4) ---
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "📊 Product Analysis", "📅 Trends & Breakdowns", "📋 Raw Data"])

# ===================== TAB 1: OVERVIEW =====================
with tab1:
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

    if compare_mode and not fdf_compare.empty:
        st.subheader("📊 Period Comparison")
        delta_rev = fdf['Revenue'].sum() - fdf_compare['Revenue'].sum()
        delta_profit = fdf['Profit'].sum() - fdf_compare['Profit'].sum()
        col1, col2 = st.columns(2)
        col1.metric("Revenue Change", fmt_currency(delta_rev), delta_color="normal")
        col2.metric("Profit Change", fmt_currency(delta_profit), delta_color="normal")

    col1, col2 = st.columns(2)
    with col1:
        daily = fdf.groupby("Date")["Revenue"].sum().reset_index()
        fig = px.line(daily, x="Date", y="Revenue", title="Revenue Trend", markers=True)
        fig.update_layout(yaxis_title=CURRENCY)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        cat_sum = fdf.groupby("Category")["Revenue"].sum().sort_values(ascending=False).reset_index()
        fig = px.pie(cat_sum, names="Category", values="Revenue", hole=0.4, title="Revenue by Category")
        st.plotly_chart(fig, use_container_width=True)

    cumulative = fdf.sort_values("Date")
    cumulative["Cumulative Revenue"] = cumulative["Revenue"].cumsum()
    fig = px.area(cumulative, x="Date", y="Cumulative Revenue", title="Cumulative Revenue Over Time")
    fig.update_layout(yaxis_title=CURRENCY)
    st.plotly_chart(fig, use_container_width=True)

# ===================== TAB 2: PRODUCT ANALYSIS =====================
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
        barmode="group"
    )
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

# ===================== TAB 3: TRENDS & BREAKDOWNS =====================
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
        hovermode="x unified"
    )
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

# ===================== TAB 4: RAW DATA =====================
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
st.sidebar.caption(f"Data updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.sidebar.caption("💡 Click 'Refresh Data' to fetch the latest from Google Sheets")
