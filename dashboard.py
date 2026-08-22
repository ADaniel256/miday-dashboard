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
    try:
        # 1. Read the CSV without assuming any header row
        df_raw = pd.read_csv(SHEET_URL, encoding='utf-8-sig', header=None)

        # 2. Find the row that contains "Date" in the first column (case-insensitive)
        header_row_idx = None
        for idx, row in df_raw.iterrows():
            first_cell = str(row[0]).strip() if pd.notna(row[0]) else ""
            if "date" in first_cell.lower():
                header_row_idx = idx
                break

        if header_row_idx is None:
            # If not found, show the first few rows to help debug
            preview = df_raw.head(5).values.tolist()
            st.error(f"Could not find a row with 'Date'. First 5 rows: {preview}")
            return pd.DataFrame()

        # 3. Take data from that row onward
        df = df_raw.iloc[header_row_idx:].copy()
        # Set the first row as column names
        df.columns = df.iloc[0]
        # Remove the header row from data
        df = df[1:].reset_index(drop=True)

        # 4. Clean column names: strip spaces and rename if necessary
        df.columns = df.columns.str.strip()
        # If the first column is not "Date" but something else, rename it
        if "Date" not in df.columns:
            # Try to find any column containing "date"
            possible = [c for c in df.columns if "date" in c.lower()]
            if possible:
                df = df.rename(columns={possible[0]: "Date"})
            else:
                st.error(f"No 'Date' column found after cleaning. Columns: {list(df.columns)}")
                return pd.DataFrame()

        # 5. Remove rows where Date is missing
        df = df.dropna(subset=["Date"])
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])

        # 6. Clean numeric columns
        for col in ["Unit Price", "Revenue", "COGS"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(",", "").str.replace("#N/A", "")
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # 7. Ensure Quantity and Category exist
        if "Quantity" in df.columns:
            df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0).astype(int)
        else:
            df["Quantity"] = 0

        df["Category"] = df.get("Category", "Uncategorized").fillna("Uncategorized")
        df["Payment Status"] = df.get("Payment Status", "Unknown").fillna("Unknown")

        return df

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load and show
df = load_data()
if df.empty:
    st.stop()

# --- Sidebar ---
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

fdf = df.copy()
if len(dr) == 2:
    fdf = fdf[(fdf["Date"] >= pd.to_datetime(dr[0])) & (fdf["Date"] <= pd.to_datetime(dr[1]))]
if cat != "All":
    fdf = fdf[fdf["Category"] == cat]
if stat != "All":
    fdf = fdf[fdf["Payment Status"] == stat]

# --- KPIs ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Revenue", f"${fdf['Revenue'].sum():,.0f}")
c2.metric("📦 Units", f"{fdf['Quantity'].sum():,}")
c3.metric("🧾 Orders", f"{len(fdf):,}")
avg = fdf['Revenue'].sum() / len(fdf) if len(fdf) > 0 else 0
c4.metric("📈 Avg Order", f"${avg:,.0f}")

# --- Charts ---
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
