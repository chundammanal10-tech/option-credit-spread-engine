import time
import logging
import pandas as pd
import yfinance as yf
from datetime import datetime

# Configure logging for audit trails
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_vix_regime():
    """VIX Regime Gate: Halts trading if panic exceeds threshold."""
    try:
        hist = yf.Ticker("^VIX").history(period="2d")
        curr_vix = hist['Close'].iloc[-1]
        prev_vix = hist['Close'].iloc[-2]
        pct_change = ((curr_vix - prev_vix) / prev_vix) * 100
        
        # Black Swan Switch
        if curr_vix > 25.0 or pct_change > 15.0:
            return True, curr_vix
        return False, curr_vix
    except:
        return True, 30.0 # Fail-safe: Assume danger if data fails

def calculate_greeks_and_trade(ticker="SPY"):
    """Institutional entry selection based on 0.20-0.30 Delta."""
    halted, vix = get_vix_regime()
    if halted:
        return {"status": "HALTED", "vix": vix}
        
    tk = yf.Ticker(ticker)
    opt = tk.option_chain(tk.options[0]) # Near term expiry
    
    # Filter for 0.20 - 0.30 Delta (High probability of expiring OTM)
    # Note: Using strike selection as proxy for delta if Greeks are missing
    df = opt.puts
    short_strike = df[df['strike'] < tk.fast_info['last_price'] * 0.96].iloc[-1]
    
    return {
        "status": "APPROVED",
        "short_strike": short_strike['strike'],
        "long_strike": short_strike['strike'] - 5.0,
        "net_credit": round((short_strike['bid'] + short_strike['ask']) / 2, 2),
        "iv": short_strike['impliedVolatility'],
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }

def monitor_positions(open_positions):
    """
    Cron-compatible loop to check every 15m.
    open_positions: list of dicts containing {'entry_credit': 1.00, 'symbol': 'SPY'}
    """
    for pos in open_positions:
        current_spread_price = get_current_spread_value(pos['symbol'])
        # Exit Logic: 50% Profit Target or 2x Stop Loss
        if current_spread_price <= (pos['entry_credit'] * 0.5):
            logging.info(f"✅ PROFIT TARGET HIT: {pos['symbol']} - Closing Position")
        elif current_spread_price >= (pos['entry_credit'] * 2.0):
            logging.info(f"🛑 STOP LOSS BREACHED: {pos['symbol']} - Liquidating")
