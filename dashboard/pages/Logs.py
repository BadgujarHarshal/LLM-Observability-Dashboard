# dashboard/pages/4_Logs.py

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

st.title("📄 Log Explorer")

st.sidebar.header("Filters — Logs")

search_text = st.sidebar.text_input("Search text in prompt/response", "")

where = []
params = {}

if search_text:
    where.append("(prompt LIKE :q OR response LIKE :q)")
    params["q"] = f"%{search_text}%"

WHERE = ("WHERE " + " AND ".join(where)) if where else ""

try:
    df = get_data(f"""
        SELECT
            timestamp,
            session_id,
            user_id,
            model_name,
            prompt,
            response,
            tokens_in,
            tokens_out,
            latency_ms,
            cost_usd,
            cost_inr,
            error_type
        FROM llm_logs
        {WHERE}
        ORDER BY timestamp DESC
        LIMIT 500
    """, params)
except Exception:
    df = pd.DataFrame()

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("No logs found for current filters/search.")

