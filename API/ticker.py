import time
from datetime import datetime
import sqlite3

# Simple mapping of the assets you are tracking
TRACKED_TICKERS = ["NIFTY_50", "CRUDE_OIL"]

def fetch_live_market_rates():
    """
    Worker function to fetch current prices.
    In development, this can mock data; in production, it calls yfinance or an API.
    """
    # TODO: Connect API fetch here
    print(f"[{datetime.now()}] Fetching fresh market ticks...")
    return {
        "NIFTY_50": {"current": 23500.50, "prev_close": 23400.00},
        "CRUDE_OIL": {"current": 78.20, "prev_close": 79.00}
    }

def update_ticker_database(db_path, price_data):
    """
    Flushes the fresh prices into the SQLite ticker table.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        for symbol, prices in price_data.items():
            cursor.execute("""
                INSERT INTO market_tickers (ticker_symbol, current_price, prev_close_price, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(ticker_symbol) DO UPDATE SET
                    current_price = excluded.current_price,
                    prev_close_price = excluded.prev_close_price,
                    updated_at = excluded.updated_at;
            """, (symbol, prices["current"], prices["prev_close"], now_str))
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Database update failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    DB_FILE = "arachnet.db"
    print("--- Market Price Ticker Engine Initialized ---")
    
    # Infinite background execution loop
    while True:
        try:
            latest_prices = fetch_live_market_rates()
            update_ticker_database(DB_FILE, latest_prices)
            print("[SUCCESS] Market prices synchronized. Entering sleep state.")
        except Exception as e:
            print(f"[ERROR] Run loop encountered an issue: {e}")
            
        # Sleep for exactly 5 minutes (300 seconds) before executing again
        time.sleep(300)