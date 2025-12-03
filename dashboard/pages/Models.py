# dashboard/pages/1_Models.py

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

st.title("🤖 Model Analytics")

# Simple filters for this page
st.sidebar.header("Filters — Models")

models = []
try:
    models = get_data("SELECT DISTINCT model_name FROM llm_logs")["model_name"].tolist()
except Exception:
    pass

model_filter = st.sidebar.selectbox("Model", ["All"] + models)

where = []
params = {}

if model_filter != "All":
    where.append("model_name = :model")
    params["model"] = model_filter

WHERE = ("WHERE " + " AND ".join(where)) if where else ""

try:
    df = get_data(f"""
        SELECT
            model_name,
            COUNT(*) AS calls,
            AVG(latency_ms) AS avg_latency,
            MIN(latency_ms) AS min_latency,
            MAX(latency_ms) AS max_latency,
            SUM(tokens_in) AS total_tokens_in,
            SUM(tokens_out) AS total_tokens_out,
            SUM(cost_usd) AS total_cost_usd,
            SUM(cost_inr) AS total_cost_inr,
            SUM(CASE WHEN error_type IS NOT NULL THEN 1 ELSE 0 END) AS errors
        FROM llm_logs
        {WHERE}
        GROUP BY model_name
        ORDER BY calls DESC
    """, params)
except Exception:
    df = pd.DataFrame()

if not df.empty:
    st.subheader("Model Summary")
    st.dataframe(df)

    st.subheader("Calls per Model")
    st.bar_chart(df.set_index("model_name")["calls"])

    st.subheader("Average Latency per Model (ms)")
    st.bar_chart(df.set_index("model_name")["avg_latency"])

    st.subheader("Total Cost per Model (₹)")
    st.bar_chart(df.set_index("model_name")["total_cost_inr"])
else:
    st.info("No model analytics available yet. Run `python main.py` more times.")

