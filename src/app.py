import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Option Credit Spread Engine", layout="wide")

st.title("📈 Option Credit Spread Signal Dashboard")
st.markdown("Live scanning engine targeting high-probability credit spreads across **3, 7, 15, 21, and 30 DTE**.")

# Sidebar configuration
st.sidebar.header("Scan Parameters")
selected_dte = st.sidebar.multiselect("Select DTE Expirations", [3, 7, 15, 21, 30], default=[7, 21, 30])
min_iv_rank = st.sidebar.slider("Minimum IV Rank", 0, 100, 30)

st.subheader("Current High-Probability Signals")

# Placeholder Dataframe for Signals
data = {
    "Ticker": ["SPY", "QQQ", "IWM", "SPY"],
    "DTE": [7, 15, 21, 30],
    "Type": ["Put Spread", "Put Spread", "Call Spread", "Put Spread"],
    "Strikes": ["550/545", "480/475", "210/215", "540/535"],
    "Credit ($)": [0.65, 1.20, 0.95, 1.45],
    "Probability of Profit": ["84%", "79%", "81%", "86%"],
    "IV Rank": [42, 38, 55, 40]
}
df = pd.DataFrame(data)

filtered_df = df[df["DTE"].isin(selected_dte)]
st.dataframe(filtered_df, use_container_width=True)
