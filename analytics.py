# analytics.py (using Profit Margin instead of ROE)

import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)
pd.set_option('display.max_columns', None)

# --- FILTER FUNCTIONS ---
def apply_primary_filters(ticker_symbol, analytics):
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        
        # Rule 1: Market Cap
        market_cap = info.get('marketCap', 0)
        if 10_000_000_000 <= market_cap <= 200_000_000_000:
            analytics['market_cap_passes'] += 1
        else: return False

        # --- REVISED RULE 2: Profitability Filter (Profit Margin) ---
        profit_margin = info.get('profitMargins')
        if profit_margin is not None and profit_margin > 0.05: # Profit Margin > 5%
            analytics['profit_margin_passes'] += 1 # Renamed for clarity
        else: return False

        # Rule 3: D/E
        category = info.get('category', '').lower()
        if 'financial' in category or 'bank' in category:
            analytics['de_passes'] += 1
        else:
            debt_to_equity = info.get('debtToEquity')
            if debt_to_equity is not None and debt_to_equity < 100:
                analytics['de_passes'] += 1
            else: return False
        
        return True
    except Exception: return False

def apply_secondary_filters(hist_data, analytics):
    try:
        hist_data['SMA_5'] = hist_data['Close'].rolling(window=5).mean()
        hist_data['SMA_20'] = hist_data['Close'].rolling(window=20).mean()
        if hist_data['SMA_5'].iloc[-1] > hist_data['SMA_20'].iloc[-1]:
            analytics['sma_passes'] += 1
        else: return False

        rsi = RSIIndicator(hist_data['Close'], window=14).rsi()
        if rsi.iloc[-1] < 70:
            analytics['rsi_passes'] += 1
        else: return False

        avg_volume_15d = hist_data['Volume'].iloc[-16:-1].mean()
        current_volume = hist_data['Volume'].iloc[-1]
        if current_volume > (3 * avg_volume_15d):
            analytics['volume_passes'] += 1
        else: return False
            
        return True
    except Exception: return False

# --- MAIN SCREENER EXECUTION ---
if __name__ == "__main__":
    stock_universe = [
        "AUROPHARMA.NS", "BERGEPAINT.NS", "BHEL.NS", "BOSCHLTD.NS", "CANBK.NS", "COFORGE.NS", "CONCOR.NS", "CUMMINSIND.NS", "DLF.NS", "GAIL.NS",
        "GODREJPROP.NS", "HDFCAMC.NS", "HINDCOPPER.NS", "HINDPETRO.NS", "IDFCFIRSTB.NS", "INDHOTEL.NS", "JINDALSTEL.NS", "JSWENERGY.NS", "LICHSGFIN.NS", "LUPIN.NS",
        "M&MFIN.NS", "MRF.NS", "MPHASIS.NS", "MUTHOOTFIN.NS", "NMDC.NS", "OFSS.NS", "PAGEIND.NS", "PERSISTENT.NS", "PETRONET.NS", "PFC.NS",
        "PIIND.NS", "PNB.NS", "POLYCAB.NS", "SAIL.NS", "SRF.NS", "SUNTV.NS", "TATAPOWER.NS", "TATACHEM.NS", "TATACOMM.NS", "TATAELXSI.NS",
        "TORNTPOWER.NS", "TVSMOTOR.NS", "UBL.NS", "UNIONBANK.NS", "VOLTAS.NS", "ZEEL.NS", "ZOMATO.NS", "ABB.NS", "ACC.NS", "ADANIPOWER.NS",
        "ASHOKLEY.NS", "ASTRAL.NS", "AUROPHARMA.NS", "BALKRISIND.NS", "BANKBARODA.NS", "BATAINDIA.NS", "BHARATFORG.NS", "BIOCON.NS", "COLPAL.NS", "DALBHARAT.NS",
        "DEEPAKNTR.NS", "ESCORTS.NS", "EXIDEIND.NS", "FEDERALBNK.NS", "FORTIS.NS", "GICRE.NS", "GLAND.NS", "GLENMARK.NS", "GODREJIND.NS", "HINDZINC.NS",
        "ICICIGI.NS", "ICICIPRULI.NS", "IDBI.NS", "IDEA.NS", "IEX.NS", "IGL.NS", "INDIACEM.NS", "IRCTC.NS", "JIOFIN.NS", "JSWINFRA.NS",
        "LAURUSLABS.NS", "LODHA.NS", "LTTS.NS", "MANAPPURAM.NS", "MAXHEALTH.NS", "MOTHERSON.NS", "NAUKRI.NS", "NYKAA.NS", "OBEROIRLTY.NS", "ONGC.NS",
        "PAYTM.NS", "RECLTD.NS", "SBICARD.NS", "SIEMENS.NS", "SONACOMS.NS", "STAR.NS", "SYNGENE.NS", "TATATECH.NS", "TRENT.NS", "YESBANK.NS"
    ]

    unique_stocks = list(set(stock_universe))
    print(f"Screening {len(unique_stocks)} stocks from the Midcap universe (Using Profit Margin)...")
    
    qualified_stocks = []
    analytics = { "total_screened": 0, "primary_passed": 0, "market_cap_passes": 0, "profit_margin_passes": 0, "de_passes": 0, "sma_passes": 0, "rsi_passes": 0, "volume_passes": 0 }
    
    for ticker in tqdm(unique_stocks, desc="Screening Progress"):
        analytics['total_screened'] += 1
        if not apply_primary_filters(ticker, analytics): continue
        analytics['primary_passed'] += 1
        hist_data = yf.Ticker(ticker).history(period="60d")
        if hist_data.empty: continue
        if not apply_secondary_filters(hist_data, analytics): continue
        qualified_stocks.append(ticker)

    print("\n--- Screening Complete ---")
    print("\n📊 Funnel Analysis Report (Nifty Midcap 100, Using Profit Margin):")
    print("---------------------------------")
    print(f"Total Stocks Screened:      {analytics['total_screened']}")
    print(f"Passed Market Cap:          {analytics['market_cap_passes']}")
    print(f"Passed Profit Margin (>5%): {analytics['profit_margin_passes']}")
    print(f"Passed D/E (<1.0):          {analytics['de_passes']}")
    print(f"---------------------------------")
    print(f"Total Passed Primary:       {analytics['primary_passed']}")
    print(f"---------------------------------")
    print(f"Passed SMA Trend:           {analytics['sma_passes']}")
    print(f"Passed RSI (<70):           {analytics['rsi_passes']}")
    print(f"Passed Volume Breakout:     {analytics['volume_passes']}")
    print("---------------------------------")
    
    if qualified_stocks:
        print(f"\n✅ Qualified Stocks Found ({len(qualified_stocks)}):")
        for stock in qualified_stocks: print(f"  - {stock}")
    else:
        print("❌ No stocks met all the filter criteria today.")