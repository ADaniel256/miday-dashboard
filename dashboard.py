import streamlit as st
import pandas as pd

st.set_page_config(page_title="Test", layout="wide")
st.title("🔍 Debug Mode – Is this visible?")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8D3xOvu7VXVuwSSydp7I5TsrUnHd2dlzDy1g3MWaW1y0ojhEi4Ftvoi1ev4ZkeQeX4glRCzQvklsj/pub?gid=2071886823&single=true&output=csv"  # <-- REPLACE THIS

try:
    df = pd.read_csv(CSV_URL)
    st.success(f"✅ Data loaded! Shape: {df.shape}")
    st.dataframe(df.head(10))
except Exception as e:
    st.error(f"❌ Error: {e}")
    st.write("Please check your CSV URL.")
