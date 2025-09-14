# tools.py (Complete Version with Test Block)

import yfinance as yf
from ta.momentum import RSIIndicator
from newsapi import NewsApiClient
from tqdm import tqdm
import warnings
import streamlit as st

warnings.filterwarnings("ignore", category=RuntimeWarning)

# --- AGENT TOOLBOX ---

def get_full_analysis(ticker_symbol):
    """Performs a full analysis on a single stock and returns a structured dictionary."""
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        hist_data = stock.history(period="60d")
        if hist_data.empty: return None

        # ... [other calculations remain the same] ...
        market_cap = info.get('marketCap', 0)
        profit_margin = info.get('profitMargins', 0)
        debt_to_equity = info.get('debtToEquity')
        category = info.get('category', '').lower()
        company_name = info.get('longName', ticker_symbol)

        hist_data['SMA_5'] = hist_data['Close'].rolling(window=5).mean()
        hist_data['SMA_20'] = hist_data['Close'].rolling(window=20).mean()
        sma_5 = hist_data['SMA_5'].iloc[-1]
        sma_20 = hist_data['SMA_20'].iloc[-1]
        rsi = RSIIndicator(hist_data['Close'], window=14).rsi().iloc[-1]
        avg_volume_15d = hist_data['Volume'].iloc[-16:-1].mean()
        current_volume = hist_data['Volume'].iloc[-1]

        analysis = {
            'ticker': ticker_symbol,
            'name': company_name,
            'market_cap': market_cap,
            'profit_margin': profit_margin,
            'sma_20_value': sma_20, # <-- ADD THIS LINE
            'passes_mc': 10e9 <= market_cap <= 200e9,
            'passes_pm': profit_margin is not None and profit_margin > 0.05,
            'passes_de': ('financial' in category or 'bank' in category) or (debt_to_equity is not None and debt_to_equity < 100),
            'passes_sma': sma_5 > sma_20,
            'passes_rsi': rsi < 70,
            'passes_volume': current_volume > (3 * avg_volume_15d)
        }
        return analysis
    except Exception:
        return None

def get_watchlist_candidates(stock_universe):
    """Runs the initial filters to find stocks that are poised for a move."""
    watchlist = []
    for ticker in tqdm(stock_universe, desc="Finding Watchlist Candidates"):
        analysis = get_full_analysis(ticker)
        if analysis and analysis['passes_mc'] and analysis['passes_pm'] and \
           analysis['passes_de'] and analysis['passes_sma'] and analysis['passes_rsi']:
            watchlist.append(ticker)
    return watchlist

def get_news_headlines(ticker_symbol):
    """Fetches recent news headlines for a given stock ticker using the 'everything' endpoint."""
    try:
        company_name = yf.Ticker(ticker_symbol).info.get('longName', ticker_symbol.split('.')[0])
        ticker_root = ticker_symbol.split('.')[0]
        query = f'"{company_name}" OR "{ticker_root}"'
        newsapi = NewsApiClient(api_key=st.secrets["NEWS_API_KEY"])
        all_articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=5)
        headlines = [article['title'] for article in all_articles['articles']]
        return headlines if headlines else ["No recent headlines found."]
    except Exception as e:
        return [f"Error fetching news: {e}"]

def calculate_price_targets(ticker_symbol):
    """Calculates potential price targets using a more robust swing identification method."""
    try:
        stock = yf.Ticker(ticker_symbol)
        hist = stock.history(period="1y")
        if hist.empty:
            return {"target_1": "N/A", "target_2": "N/A"}

        last_90_days = hist.iloc[-90:]
        swing_low_date = last_90_days['Low'].idxmin()
        swing_low_price = last_90_days['Low'].min()
        data_after_low = last_90_days[last_90_days.index > swing_low_date]

        if data_after_low.empty:
            return {"target_1": "No Upward Swing", "target_2": "N/A"}

        swing_high_price = data_after_low['High'].max()
        swing_range = swing_high_price - swing_low_price

        if swing_range <= 0:
            return {"target_1": "No Upward Swing", "target_2": "N/A"}

        target_1 = swing_high_price + (swing_range * 1.618)
        target_2 = swing_high_price + (swing_range * 2.618)

        return {"target_1": f"₹{target_1:.2f}", "target_2": f"₹{target_2:.2f}"}
    except Exception:
        return {"target_1": "Error", "target_2": "Error"}

# --- MAIN EXECUTION BLOCK (for testing our tools) ---
if __name__ == "__main__":
    test_universe = ["BATAINDIA.NS", "IEX.NS", "STAR.NS", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
    
    print(f"--- Testing Tools on a Sample of {len(test_universe)} Stocks ---")
    
    watchlist = get_watchlist_candidates(test_universe)
    print("\n--- Watchlist Tool Test Complete ---")
    if watchlist:
        print(f"✅ Found {len(watchlist)} Watchlist Candidate(s): {watchlist}")
    else:
        print("- No Watchlist Candidates found.")

    if watchlist:
        candidate = watchlist[0]
        print(f"\n--- Testing Full Suite for: {candidate} ---")
        
        details = get_full_analysis(candidate)
        print("\n[Full Analysis Report]:")
        if details:
            for key, value in details.items():
                print(f"  - {key}: {value}")
        
        headlines = get_news_headlines(candidate)
        print("\n[Recent Headlines]:")
        for i, headline in enumerate(headlines):
            print(f"  {i+1}. {headline}")
            
        targets = calculate_price_targets(candidate)
        print("\n[Price Targets]:")
        print(f"  - Target 1 (161.8%): {targets['target_1']}")
        print(f"  - Target 2 (261.8%): {targets['target_2']}")