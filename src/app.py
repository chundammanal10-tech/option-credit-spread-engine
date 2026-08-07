import streamlit as st
import pandas as pd

st.set_page_config(page_title="Master Trader Dashboard", layout="wide")

# Custom CSS for Mobile Optimization
st.markdown("""
    <style>
    .stDataFrame {width: 100% !important;}
    .reportview-container {padding: 10px;}
    </style>
""", unsafe_allow_html=True)

tabs = st.tabs(["🚀 Trading Cockpit", "🌍 Macro & Catalyst Intel"])

# --- TAB 1: TRADING COCKPIT ---
with tabs[0]:
    st.header("Credit Spread Signal Engine")
    
    # Mock data structured for Robinhood execution
    data = {
        "Ticker": ["SPY", "QQQ", "IWM"],
        "DTE": [30, 45, 30],
        "Type": ["Bull Put", "Bear Call", "Bull Put"],
        "Short Strike": [540, 490, 205],
        "Long Strike": [535, 495, 200],
        "Delta": [0.20, 0.22, 0.18],
        "Credit/Width": ["1/3", "1/3", "1/3"],
        "Action": ["Trade in Robinhood", "Trade in Robinhood", "Trade in Robinhood"]
    }
    df = pd.DataFrame(data)
    st.table(df) # Table displays better on mobile than st.dataframe
    
    st.info("Strategy: Target 15-25 Delta, 30-45 DTE. Close at 50% profit. Risk = 2x credit.")

# --- TAB 2: MARKET INTEL ---
with tabs[1]:
    st.header("Macro & Catalyst Intelligence")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Market Pulse")
        st.write("• **10-Year Bond Rate:** 4.2% (Trending Down - Bullish for Equities)")
        st.write("• **Gold (GLD):** Oversold (Look for Mean Reversion)")
    with col2:
        st.subheader("Catalysts & Sentiment")
        st.write("• **Inverse Cramer:** Currently betting against [Sector X]")
        st.write("• **Politician Trades:** Unusual activity in [Ticker Y]")
        st.write("• **Market Sentiment:** Fear/Greed Index = 65 (Neutral/Greed)")
    
    st.warning("Catalyst Watch: FOMC Minutes release on Wednesday. Reduce position sizing.")
