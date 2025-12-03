# dashboard/pages/2_Prompts.py

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

st.title("🧠 Prompt Intelligence")

st.sidebar.header("Filters — Prompts")

model_filter = "All"
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
            prompt,
            COUNT(*) AS calls,
            AVG(latency_ms) AS avg_latency,
            SUM(cost_inr) AS total_cost_inr,
            SUM(CASE WHEN error_type IS NOT NULL THEN 1 ELSE 0 END) AS errors
        FROM llm_logs
        {WHERE}
        GROUP BY prompt
        HAVING prompt IS NOT NULL AND prompt != ''
        ORDER BY calls DESC
        LIMIT 50
    """, params)
except Exception:
    df = pd.DataFrame()

if not df.empty:
    st.subheader("Top 50 Prompts (by usage)")
    st.dataframe(df)

    st.subheader("Most Used Prompts")
    st.bar_chart(df.set_index("prompt")["calls"])

    st.subheader("Most Expensive Prompts (₹)")
    st.bar_chart(df.set_index("prompt")["total_cost_inr"])
else:
    st.info("No prompt analytics yet. Generate more interactions.")

