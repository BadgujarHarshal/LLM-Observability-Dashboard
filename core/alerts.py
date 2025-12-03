# core/alerts.py

import uuid
from datetime import datetime
from core.db import get_connection

# ------- Option 2 thresholds (Balanced) -------
LATENCY_STATIC = 1500            # ms
ERROR_RATE_STATIC = 15           # %
COST_SPIKE_STATIC = 2.0          # 2x normal daily cost


def insert_alert(alert_type, message, severity, value=None, expected=None):
    conn = get_connection()
    alert_id = str(uuid.uuid4())

    conn.execute("""
    INSERT INTO llm_alerts (
        id, timestamp, alert_type, message, severity, value, expected, resolved
    ) VALUES (?, ?, ?, ?, ?, ?, ?, 0)
    """, (
        alert_id,
        datetime.utcnow().isoformat(),
        alert_type,
        message,
        severity,
        value,
        expected
    ))

    conn.commit()
    conn.close()
    print(f"[ALERT] → {alert_type} | {severity} | {message}")


def run_alert_checks(log_row, daily_row):
    """
    log_row = last interaction logged
    daily_row = aggregated daily metrics from llm_metrics_daily
    """

    latency = log_row["latency_ms"]
    cost = log_row["cost_usd"]
    error = log_row["error_type"]

    avg_cost_today = daily_row["total_cost_usd"]
    total_requests_today = daily_row["total_requests"]

    # ---------------- LATENCY ALERT ----------------
    if latency > LATENCY_STATIC:
        insert_alert(
            alert_type="HIGH_LATENCY",
            message=f"Latency {latency}ms exceeded threshold {LATENCY_STATIC}ms",
            severity="warning",
            value=latency,
            expected=LATENCY_STATIC
        )

    # ---------------- ERROR SPIKE ALERT ----------------
    if error is not None:
        # error_rate = 1 error over X requests
        error_rate = (daily_row["error_count"] / total_requests_today) * 100
        if error_rate > ERROR_RATE_STATIC:
            insert_alert(
                alert_type="ERROR_SPIKE",
                message=f"Error rate {error_rate:.1f}% exceeded threshold {ERROR_RATE_STATIC}%",
                severity="critical",
                value=error_rate,
                expected=ERROR_RATE_STATIC
            )

    # ---------------- COST SPIKE ALERT ----------------
    # Check if cost is unusually high (compared to avg daily cost)
    if avg_cost_today > 0 and cost > avg_cost_today * COST_SPIKE_STATIC:
        insert_alert(
            alert_type="COST_SPIKE",
            message=f"Cost ${cost:.4f} exceeded {COST_SPIKE_STATIC}× of today's avg ${avg_cost_today:.4f}",
            severity="warning",
            value=cost,
            expected=avg_cost_today * COST_SPIKE_STATIC
        )
 