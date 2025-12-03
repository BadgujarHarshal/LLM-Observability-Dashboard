# dashboard/pages/3_Errors.py

import streamlit as st
import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "llm_logs.db")
DB_PATH = os.path.abspath(DB_PATH)

def get_data(query, params=None):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn, params=params or {})
    conn.close()
    return df

st.title("⚠ Error Diagnostics")

st.sidebar.header("Filters — Errors")

model_filter = "All"
models = []
try:
    models = get_data("SELECT DISTINCT model_name FROM llm_logs")["model_name"].tolist()
except Exception:
    pass

model_filter = st.sidebar.selectbox("Model", ["All"] + models)

where = ["error_type IS NOT NULL"]
params = {}

if model_filter != "All":
    where.append("model_name = :model")
    params["model"] = model_filter

WHERE = "WHERE " + " AND ".join(where)

try:
    summary = get_data(f"""
        SELECT error_type, COUNT(*) AS count
        FROM llm_logs
        {WHERE}
        GROUP BY error_type
        ORDER BY count DESC
    """, params)
except Exception:
    summary = pd.DataFrame()

if not summary.empty:
    st.subheader("Error Types")
    st.dataframe(summary)
    st.bar_chart(summary.set_index("error_type")["count"])
else:
    st.success("No errors recorded yet. 🎉")


st.subheader("Recent Error Logs (Last 100)")

try:
    errors = get_data(f"""
        SELECT timestamp, model_name, prompt, error_type, latency_ms
        FROM llm_logs
        {WHERE}
        ORDER BY timestamp DESC
        LIMIT 100
    """, params)
    st.dataframe(errors)
except Exception:
    st.info("No error logs to show yet.")

