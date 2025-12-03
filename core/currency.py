# core/currency.py 

import sqlite3
import requests
from datetime import datetime

DB_PATH = "llm_logs.db"

def get_inr_rate():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS currency_rates (
            date TEXT PRIMARY KEY,
            usd_to_inr REAL
        )
    """)
    conn.commit()

    today = datetime.now().strftime("%Y-%m-%d")

    # Check if rate already saved today
    row = conn.execute("SELECT usd_to_inr FROM currency_rates WHERE date = ?", (today,)).fetchone()
    if row:
        conn.close()
        return row[0]

    # Fetch from API (if not saved yet)
    try:
        r = requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()
        rate = float(r["rates"]["INR"])
    except Exception:
        rate = 83.0  # fallback safe default INR rate

    conn.execute("INSERT OR REPLACE INTO currency_rates (date, usd_to_inr) VALUES (?, ?)", (today, rate))
    conn.commit()
    conn.close()
    return rate
