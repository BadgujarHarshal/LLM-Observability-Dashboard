# dashboard/app.py

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import time
import os

import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT)

from core.db import init_db
init_db()

# ---------- DB PATH ----------
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "llm_logs.db"))

def get_data(query, params=None):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn, params=params or {})
    conn.close()
    return df


st.set_page_config(page_title="LLM Observability Dashboard", layout="wide")
st.title("🏠 Overview — LLM Observability Dashboard")


# ============================================================
# 🔥 FILTER PANEL
# ============================================================
st.sidebar.header("🔎 Filters (Overview)")

range_option = st.sidebar.selectbox(
    "Time Range",
    ["Last 7 days", "Last 30 days", "All time", "Custom range"]
)

from_date, to_date = None, None
if range_option == "Custom range":
    from_date = st.sidebar.date_input("From")
    to_date = st.sidebar.date_input("To")

def safe_list(query, col):
    try:
        df = get_data(query)
        return df[col].dropna().tolist()
    except Exception:
        return []

models = safe_list("SELECT DISTINCT model_name FROM llm_logs", "model_name")
users = safe_list("SELECT DISTINCT user_id FROM llm_logs", "user_id")
sessions = safe_list("SELECT DISTINCT session_id FROM llm_logs", "session_id")

model_filter = st.sidebar.selectbox("Model", ["All"] + models)
user_filter = st.sidebar.selectbox("User", ["All"] + users)
session_filter = st.sidebar.selectbox("Session", ["All"] + sessions)
error_filter = st.sidebar.selectbox("Errors", ["All", "Only errors", "Only successful"])


# ---------- WHERE CLAUSE ----------
where = []
params = {}

if range_option == "Last 7 days":
    where.append("date(timestamp) >= date('now', '-7 days')")
elif range_option == "Last 30 days":
    where.append("date(timestamp) >= date('now', '-30 days')")
elif range_option == "Custom range" and from_date and to_date:
    where.append("date(timestamp) BETWEEN :from AND :to")
    params["from"] = str(from_date)
    params["to"] = str(to_date)

if model_filter != "All":
    where.append("model_name = :model")
    params["model"] = model_filter
if user_filter != "All":
    where.append("user_id = :user")
    params["user"] = user_filter
if session_filter != "All":
    where.append("session_id = :session")
    params["session"] = session_filter
if error_filter == "Only errors":
    where.append("error_type IS NOT NULL")
elif error_filter == "Only successful":
    where.append("error_type IS NULL")

WHERE = ("WHERE " + " AND ".join(where)) if where else ""


# ============================================================
# 🔥 DAILY METRICS
# ============================================================
query_daily = f"SELECT * FROM llm_metrics_daily {WHERE.replace('timestamp', 'date')} ORDER BY date DESC"
try:
    daily = get_data(query_daily, params)
except Exception:
    daily = pd.DataFrame()

if not daily.empty:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Requests", int(daily['total_requests'].sum()))
    c2.metric("Avg Latency (ms)", f"{int(daily['avg_latency_ms'].mean())}")
    c3.metric("Total Errors", int(daily['error_count'].sum()))

    total_usd = round(daily['total_cost_usd'].sum(), 4)
    total_inr = round(daily['total_cost_inr'].sum(), 2)

    c4.metric("Total Cost", f"₹{total_inr}  |  ${total_usd}")

    st.subheader("📅 Daily Activity")
    st.line_chart(daily.set_index("date")["total_requests"])

    st.subheader("⚡ Latency Trend")
    st.line_chart(daily.set_index("date")["avg_latency_ms"])
else:
    st.warning("No data for selected filters.")


# ============================================================
# 🔥 RECENT LOG ENTRIES
# ============================================================
st.subheader("📁 Recent Log Entries (Last 100)")

try:
    logs_raw = get_data(f"""
        SELECT timestamp, session_id, user_id, model_name, prompt, latency_ms, error_type, cost_usd, cost_inr
        FROM llm_logs
        {WHERE}
        ORDER BY timestamp DESC
        LIMIT 100
    """, params)
    st.dataframe(logs_raw)
except Exception:
    st.info("No logs available yet. Run `python main.py` a few times.")


# ============================================================
# 🔄 AUTO REFRESH + CSV EXPORT
# ============================================================
st.markdown("---")

auto_refresh = st.checkbox("🔄 Auto Refresh every 20 seconds (Overview)")
if auto_refresh:
    time.sleep(20)
    st.experimental_rerun()

if 'logs_raw' in locals() and not logs_raw.empty:
    csv_data = logs_raw.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Download Filtered Logs (CSV)",
        data=csv_data,
        file_name="llm_logs_filtered.csv",
        mime="text/csv"
    )
