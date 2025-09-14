# debug_news.py (Standalone News Tool Validator)

import yfinance as yf
from newsapi import NewsApiClient
import config
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)

def test_news_fetcher(ticker_symbol):
    """
    A self-contained, verbose function to test the full news fetching process.
    """
    try:
        print(f"\n[DEBUG] Testing ticker: {ticker_symbol}")
        print("  - Step 1: Fetching company info from yfinance...")
        stock_info = yf.Ticker(ticker_symbol).info
        company_name = stock_info.get('longName', ticker_symbol.split('.')[0])
        print(f"  - Step 2: Company name found: '{company_name}'")

        ticker_root = ticker_symbol.split('.')[0]

        query = f'"{company_name}" OR "{ticker_root}"'
        print(f"  - Step 3: Built search query: {query}")

        newsapi = NewsApiClient(api_key=config.NEWS_API_KEY)

        print("  - Step 4: Querying NewsAPI...")
        all_articles = newsapi.get_everything(
            q=query,
            language='en',
            sort_by='relevancy',
            page_size=5
        )
        print("  - Step 5: NewsAPI query complete.")

        headlines = [article['title'] for article in all_articles['articles']]

        print("\n--- RESULT ---")
        if headlines:
            print("✅ Success! Found the following headlines:")
            for i, headline in enumerate(headlines):
                print(f"  {i+1}. {headline}")
        else:
            print("- No recent headlines found by the API for this query.")

    except Exception as e:
        print(f"\n--- ❌ ERROR ---")
        print(f"An error occurred: {e}")

# --- Main execution block ---
if __name__ == "__main__":
    print("--- Starting Standalone News Debugger ---")
    test_news_fetcher("RELIANCE.NS")
    print("\n--- Debugger Finished ---")