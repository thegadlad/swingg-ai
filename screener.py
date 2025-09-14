# screener.py (with Exact Stop-Loss Price)

import yfinance as yf
from tqdm import tqdm
import warnings
import json
from datetime import datetime
import os
import glob
from universes import NIFTY_50, NIFTY_MIDCAP_100, HIGH_LIQUIDITY_SMALLCAPS
from tools import get_full_analysis, calculate_price_targets

warnings.filterwarnings("ignore", category=RuntimeWarning)

# ... [validate_previous_watchlist function is unchanged] ...
# ... [screen_stocks function is unchanged] ...

def validate_previous_watchlist(previous_watchlist_data):
    print("\n--- Part 1: Validating Previous Day's Watchlist ---")
    previous_watchlist = previous_watchlist_data.get('watchlist_candidates', [])
    if not previous_watchlist:
        print("No previous watchlist found to validate.")
        return
    print("\n[Validation Report]:")
    for stock in previous_watchlist:
        # ... (rest of the function is the same)
        ticker = stock['ticker']
        current_analysis = get_full_analysis(ticker)
        if not current_analysis:
            print(f"  - {ticker}: Could not retrieve current data.")
            continue
        status, details = "Signal Intact", "Conditions remain similar."
        if current_analysis['passes_volume']:
            status, details = "✅ Signal Strengthened", "Volume breakout detected!"
        elif not current_analysis['passes_sma'] or not current_analysis['passes_rsi']:
            status, details = "❌ Signal Weakened", "Trend or momentum has broken down."
        print(f"  - {ticker} ({stock['name']}): {status} -> {details}")

def screen_stocks(stock_universe):
    action_signals, watchlist_candidates = [], []
    for ticker_symbol in tqdm(stock_universe, desc="Screening For New Signals"):
        try:
            analysis = get_full_analysis(ticker_symbol)
            if not analysis: continue
            if analysis['passes_mc'] and analysis['passes_pm'] and analysis['passes_de'] and \
               analysis['passes_sma'] and analysis['passes_rsi']:
                watchlist_candidates.append(analysis) # Return the full analysis dict
                if analysis['passes_volume']:
                    action_signals.append(analysis)
        except Exception:
            continue
    return action_signals, watchlist_candidates

def print_stock_report(stock_analysis):
    """
    Prints a formatted report for a single stock, including its exit strategy.
    """
    ticker = stock_analysis['ticker']
    name = stock_analysis['name']
    sma_20 = stock_analysis.get('sma_20_value', 0) # Get the SMA value
    
    print(f"  - {ticker} ({name})")
    targets = calculate_price_targets(ticker)
    print("    - Exit Strategy:")
    print(f"      - Price Targets: T1 @ {targets['target_1']}, T2 @ {targets['target_2']}")
    # --- CHANGE HERE: Display the actual SMA price ---
    print(f"      - Management Rule: Exit if price closes below ₹{sma_20:.2f} (the 20-day SMA).")

# --- MAIN SCREENER EXECUTION ---
if __name__ == "__main__":
    # ... [File loading logic is unchanged] ...
    previous_watchlist_data = {}
    list_of_files = glob.glob('watchlist_*.json')
    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getctime)
        print(f"Loading previous watchlist from: {latest_file}")
        with open(latest_file, 'r') as f:
            previous_watchlist_data = json.load(f)

    validate_previous_watchlist(previous_watchlist_data)
    previous_tickers = {stock['ticker'] for stock in previous_watchlist_data.get('watchlist_candidates', [])}

    print("\n\n--- Part 2: Screening for New Signals Today ---")
    combined_universe = NIFTY_50 + NIFTY_MIDCAP_100 + HIGH_LIQUIDITY_SMALLCAPS
    unique_stocks = sorted(list(set(combined_universe)))

    print(f"Running screener on a combined universe of {len(unique_stocks)} stocks...")
    action_signals, watchlist_candidates = screen_stocks(unique_stocks)

    print("\n--- Screening Complete: Final Report ---")

    # --- Reporting logic is now simpler as we pass the full analysis object ---
    current_watchlist_tickers = {stock['ticker'] for stock in watchlist_candidates}
    new_signals = [stock for stock in watchlist_candidates if stock['ticker'] not in previous_tickers]
    still_valid_signals = [stock for stock in watchlist_candidates if stock['ticker'] in previous_tickers]
    dropped_signals = [stock for stock in previous_watchlist_data.get('watchlist_candidates', []) if stock['ticker'] not in current_watchlist_tickers]

    if action_signals:
        print(f"\n✅ Found {len(action_signals)} Immediate Action Signal(s):")
        for stock in action_signals: print_stock_report(stock)
    else:
        print("\n❌ No Immediate Action Signals found today.")

    if new_signals:
        print(f"\n✨ Found {len(new_signals)} New High-Priority Watchlist Stock(s):")
        for stock in new_signals: print_stock_report(stock)

    if still_valid_signals:
        print(f"\n👀 Found {len(still_valid_signals)} Previous Signal(s) Still Valid:")
        for stock in still_valid_signals: print_stock_report(stock)
        
    if dropped_signals:
        print(f"\n➖ Found {len(dropped_signals)} Dropped Signal(s) (No Longer Qualify):")
        for stock in dropped_signals: print(f"  - {stock['ticker']} ({stock['name']})")

    today_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"watchlist_{today_str}.json"
    # We need to save a simplified version to JSON, not the full complex object
    watchlist_to_save = [{'ticker': s['ticker'], 'name': s['name']} for s in watchlist_candidates if s['ticker'] not in {a['ticker'] for a in action_signals}]
    actions_to_save = [{'ticker': s['ticker'], 'name': s['name']} for s in action_signals]
    with open(filename, 'w') as f:
        json.dump({"action_signals": actions_to_save, "watchlist_candidates": watchlist_to_save}, f, indent=4)
    print(f"\n💾 Today's results saved to {filename}")