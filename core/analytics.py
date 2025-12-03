# core/analytics.py

from core.db import get_connection

def update_daily_metrics():
    conn = get_connection()

    # Fetch aggregated metrics from raw logs
    rows = conn.execute("""
        SELECT
            date(timestamp) AS date,
            COUNT(*) AS total_requests,
            AVG(latency_ms) AS avg_latency_ms,
            AVG(tokens_in) AS avg_tokens_in,
            AVG(tokens_out) AS avg_tokens_out,
            SUM(cost_usd) AS total_cost_usd,
            SUM(cost_inr) AS total_cost_inr,
            SUM(CASE WHEN error_type IS NOT NULL THEN 1 ELSE 0 END) AS error_count
        FROM llm_logs
        GROUP BY date
    """).fetchall()

    # Insert aggregated values into llm_metrics_daily
    for row in rows:
        conn.execute("""
            INSERT OR REPLACE INTO llm_metrics_daily
            (date, total_requests, avg_latency_ms, error_count,
             avg_tokens_in, avg_tokens_out, total_cost_usd, total_cost_inr)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, row)

    conn.commit()
    return True

