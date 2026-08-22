import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="MiDAY Live", layout="wide")
st.title("☕ MiDAY System - Live Dashboard")

# =====================================================
EXCEL_URL = "https://raw.githubusercontent.com/ADaniel256/miday-dashboard/main/MiDAY%20System.xlsx"
# =====================================================

@st.cache_data(ttl=600)
def load_data():
    try:
        df = pd.read_excel(EXCEL_URL, sheet_name="MASTER_SALES")

        df = df.dropna(subset=["Date"], how="all")
        df = df[df["Date"].notna()]
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])

        # Clean numeric columns
        for col in ["Unit Price", "Revenue", "COGS"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        if "Quantity" in df.columns:
            df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0).astype(int)
        else:
            df["Quantity"] = 0

        df["Category"] = df.get("Category", "Uncategorized").fillna("Uncategorized")
        df["Payment Status"] = df.get("Payment Status", "Unknown").fillna("Unknown")

        # ✅ Calculate Profit and Margin
        df["Profit"] = df["Revenue"] - df["COGS"]
        df["Margin %"] = (df["Profit"] / df["Revenue"] * 100).round(1)
        df["Margin %"] = df["Margin %"].fillna(0)  # Handle cases where Revenue = 0

        return df

    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.stop()

# --- Sidebar filters ---
st.sidebar.header("🔍 Filters")
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

min_d = df["Date"].min().date()
max_d = df["Date"].max().date()
dr = st.sidebar.date_input("Date Range", [min_d, max_d], min_value=min_d, max_value=max_d)

cat_options = ["All"] + sorted(df["Category"].dropna().unique().tolist())
cat = st.sidebar.selectbox("Category", cat_options)

stat_options = ["All"] + sorted(df["Payment Status"].dropna().unique().tolist())
stat = st.sidebar.selectbox("Payment Status", stat_options)

# ✅ Time Granularity Selector
granularity = st.sidebar.radio("Time Granularity", ["Daily", "Weekly", "Monthly"], index=0)

# Apply filters
fdf = df.copy()
if len(dr) == 2:
    fdf = fdf[(fdf["Date"] >= pd.to_datetime(dr[0])) & (fdf["Date"] <= pd.to_datetime(dr[1]))]
if cat != "All":
    fdf = fdf[fdf["Category"] == cat]
if stat != "All":
    fdf = fdf[fdf["Payment Status"] == stat]

# --- Aggregate by selected granularity ---
def aggregate_by_period(df, gran):
    if gran == "Daily":
        df['Period'] = df['Date'].dt.date
    elif gran == "Weekly":
        df['Period'] = df['Date'].dt.to_period('W').apply(lambda r: r.start_time.date())
    else:  # Monthly
        df['Period'] = df['Date'].dt.to_period('M').apply(lambda r: r.start_time.date())
    
    agg = df.groupby('Period').agg({
        'Revenue': 'sum',
        'Profit': 'sum',
        'COGS': 'sum',
        'Quantity': 'sum',
        'Date': 'count'  # Count of orders
    }).rename(columns={'Date': 'Orders'}).reset_index()
    
    agg['Margin %'] = (agg['Profit'] / agg['Revenue'] * 100).round(1).fillna(0)
    return agg

agg_df = aggregate_by_period(fdf, granularity)

# --- KPIs ---
total_revenue = fdf['Revenue'].sum()
total_profit = fdf['Profit'].sum()
overall_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
total_orders = len(fdf)
total_units = fdf['Quantity'].sum()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("💰 Revenue", f"${total_revenue:,.0f}")
c2.metric("📈 Profit", f"${total_profit:,.0f}")
c3.metric("📊 Margin %", f"{overall_margin:.1f}%")
c4.metric("🧾 Orders", f"{total_orders:,}")
c5.metric("📦 Units", f"{total_units:,}")

st.divider()

# --- Charts Layout ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"📊 Revenue & Profit ({granularity})")
    if not agg_df.empty:
        fig = go.Figure()
        # Bars for Revenue
        fig.add_trace(go.Bar(
            x=agg_df['Period'],
            y=agg_df['Revenue'],
            name='Revenue',
            marker_color='#FF6B6B'
        ))
        # Line for Profit
        fig.add_trace(go.Scatter(
            x=agg_df['Period'],
            y=agg_df['Profit'],
            name='Profit',
            mode='lines+markers',
            line=dict(color='#2ECC71', width=3),
            marker=dict(size=8),
            yaxis='y2'  # secondary axis
        ))
        # Line for Margin %
        fig.add_trace(go.Scatter(
            x=agg_df['Period'],
            y=agg_df['Margin %'],
            name='Margin %',
            mode='lines+markers',
            line=dict(color='#F1C40F', width=2, dash='dash'),
            marker=dict(size=6),
            yaxis='y2'
        ))
        
        fig.update_layout(
            xaxis=dict(title='Period'),
            yaxis=dict(title='Revenue ($)', side='left'),
            yaxis2=dict(title='Profit / Margin %', overlaying='y', side='right'),
            legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)'),
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for the selected filters.")

with col2:
    st.subheader("📊 Revenue by Category")
    cat_sum = fdf.groupby("Category")["Revenue"].sum().sort_values(ascending=False).reset_index()
    if not cat_sum.empty:
        fig = px.pie(cat_sum, names="Category", values="Revenue", hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data.")

col3, col4 = st.columns(2)

with col3:
    st.subheader("🏆 Top 8 Products")
    top = fdf.groupby("Product Name")["Revenue"].sum().sort_values(ascending=False).head(8).reset_index()
    if not top.empty:
        fig = px.bar(top, y="Product Name", x="Revenue", title="",
                     orientation="h", color="Revenue", color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data.")

with col4:
    st.subheader("💳 Revenue by Payment Status")
    pay = fdf.groupby("Payment Status")["Revenue"].sum().reset_index()
    if not pay.empty:
        fig = px.pie(pay, names="Payment Status", values="Revenue",
                     color_discrete_sequence=["#2ECC71", "#F1C40F", "#E74C3C", "#3498DB"])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data.")

# --- Breakdown Table (Expander) ---
with st.expander(f"📋 Detailed {granularity} Breakdown"):
    if not agg_df.empty:
        # Format for display
        display_df = agg_df.copy()
        display_df['Period'] = display_df['Period'].astype(str)
        display_df['Revenue'] = display_df['Revenue'].apply(lambda x: f"${x:,.0f}")
        display_df['Profit'] = display_df['Profit'].apply(lambda x: f"${x:,.0f}")
        display_df['COGS'] = display_df['COGS'].apply(lambda x: f"${x:,.0f}")
        display_df['Margin %'] = display_df['Margin %'].apply(lambda x: f"{x:.1f}%")
        st.dataframe(display_df, use_container_width=True)
        
        # Download button
        csv = agg_df.to_csv(index=False)
        st.download_button(
            label=f"📥 Download {granularity} Data as CSV",
            data=csv,
            file_name=f"miday_{granularity.lower()}_breakdown.csv",
            mime="text/csv"
        )
    else:
        st.info("No data to display.")

# --- Raw Data Table ---
with st.expander("📋 View Raw Transaction Data"):
    st.dataframe(fdf[["Date", "Product Name", "Category", "Quantity", "Unit Price", 
                      "Revenue", "COGS", "Profit", "Margin %", "Payment Status", "Notes"]],
                 use_container_width=True, height=400)
