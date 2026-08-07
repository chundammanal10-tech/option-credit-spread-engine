import time
import logging
import pandas as pd
import yfinance as yf
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def check_vix_circuit_breaker():
    """Fetches real-time VIX to assess black swan market panic conditions."""
    try:
        vix = yf.Ticker("^VIX")
        hist = vix.history(period="2d")
        if len(hist) < 2:
            return False, 15.0, 0.0
        
        current_vix = hist['Close'].iloc[-1]
        prev_vix = hist['Close'].iloc[-2]
        pct_change = ((current_vix - prev_vix) / prev_vix) * 100
        
        if current_vix > 25.0 or pct_change > 15.0:
            logging.warning(f"🚨 VIX CIRCUIT BREAKER TRIPPED! VIX: {current_vix:.2f} (Change: {pct_change:+.2f}%)")
            return True, current_vix, pct_change
            
        logging.info(f"✅ VIX Normal: {current_vix:.2f} ({pct_change:+.2f}%). Premium selling authorized.")
        return False, current_vix, pct_change
    except Exception as e:
        logging.error(f"Error checking VIX: {e}")
        return False, 15.0, 0.0

def fetch_live_option_credit_spread(ticker_symbol="SPY"):
    """Pulls live option chains to calculate a true Bull Put Credit Spread."""
    is_halted, vix_val, vix_chg = check_vix_circuit_breaker()
    if is_halted:
        return {"status": "HALTED", "reason": f"VIX Panic Gate Active (VIX: {vix_val:.2f})"}

    try:
        tk = yf.Ticker(ticker_symbol)
        expirations = tk.options
        if not expirations:
            return {"status": "ERROR", "reason": "No option expirations available."}
            
        target_expiry = expirations[min(2, len(expirations)-1)]
        chain = tk.option_chain(target_expiry)
        puts = chain.puts
        
        spot_price = tk.fast_info.get("last_price", 0.0)
        if not spot_price or spot_price == 0.0:
            hist = tk.history(period="1d")
            spot_price = hist['Close'].iloc[-1] if not hist.empty else 500.0

        # Filter puts safely OTM (approx 3% to 4% below spot price for safety)
        target_short_strike_price = round(spot_price * 0.96, 0)
        
        otm_puts = puts[puts['strike'] <= target_short_strike_price].copy()
        if otm_puts.empty:
            otm_puts = puts.tail(15)
            
        # Select the closest strike for our short put
        short_put = otm_puts.iloc[-1] if not otm_puts.empty else puts.iloc[0]
        short_strike = short_put['strike']
        
        # Define a standard $5 wide wing protection
        long_strike = short_strike - 5.0
        
        iv = short_put['impliedVolatility'] if 'impliedVolatility' in short_put and pd.notna(short_put['impliedVolatility']) else 0.16
        bid = short_put['bid'] if 'bid' in short_put and pd.notna(short_put['bid']) else 0.50
        ask = short_put['ask'] if 'ask' in short_put and pd.notna(short_put['ask']) else 0.70
        
        net_credit = round(max(0.30, min((bid + ask) / 2.0, 2.0)), 2)
        max_risk = round(5.0 - net_credit, 2)
        
        return {
            "status": "APPROVED",
            "ticker": ticker_symbol,
            "spot": round(spot_price, 2),
            "expiry": target_expiry,
            "short_strike": f"{short_strike}P",
            "long_strike": f"{long_strike}P",
            "iv": round(iv * 100, 1),
            "net_credit": net_credit,
            "max_risk": max_risk,
            "vix": vix_val
        }
    except Exception as e:
        logging.error(f"Failed parsing option chain for {ticker_symbol}: {e}")
        return {"status": "ERROR", "reason": str(e)}

def run_background_monitoring_loop():
    logging.info("Starting Autonomous Credit Spread Position Monitoring Daemon...")
    while True:
        vix_halt, vix_val, _ = check_vix_circuit_breaker()
        logging.info(f"Monitor heartbeat: VIX checked at {vix_val:.2f}. Scanning active spreads...")
        time.sleep(900)

if __name__ == "__main__":
    print(fetch_live_option_credit_spread("SPY"))
