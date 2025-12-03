# dashboard/pages/Alerts.py

import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="🚨 Alerts Center", layout="wide")
st.title("🚨 Alerts Center — Real-Time Issues & System Warnings")

# ---------- ALWAYS use the same DB as main.py ----------
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "llm_logs.db"))

def get_data(query, params=None):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn, params=params or {})
    conn.close()
    return df

def resolve_alert(alert_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE llm_alerts SET resolved = 1 WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()

# ---------------- FILTER PANEL ----------------
st.sidebar.header("🔎 Filters")

severity_filter = st.sidebar.selectbox("Severity", ["All", "critical", "warning", "info"])
status_filter    = st.sidebar.selectbox("Status",   ["All", "Only Unresolved", "Only Resolved"])

where = []
params = {}

if severity_filter != "All":
    where.append("severity = :severity")
    params["severity"] = severity_filter

if status_filter == "Only Unresolved":
    where.append("resolved = 0")
elif status_filter == "Only Resolved":
    where.append("resolved = 1")

WHERE = ("WHERE " + " AND ".join(where)) if where else ""

alerts = get_data(f"SELECT * FROM llm_alerts {WHERE} ORDER BY timestamp DESC", params)

if alerts.empty:
    st.success("🎉 No alerts found. System looks healthy!")
    st.stop()

# ---------------- METRICS SUMMARY ----------------
c1, c2, c3 = st.columns(3)
c1.metric("Total Alerts", len(alerts))
c2.metric("Critical Alerts", len(alerts[alerts["severity"] == "critical"]))
c3.metric("Unresolved Alerts", len(alerts[alerts["resolved"] == 0]))

# ---------------- COLOR BADGE ----------------
def badge(sev):
    return "🟥 Critical" if sev == "critical" else "🟧 Warning" if sev == "warning" else "🟩 Info"

# ---------------- ALERT LIST ----------------
st.subheader("📋 Alert List")
for _, row in alerts.iterrows():
    with st.container():
        st.write("---")
        c1, c2 = st.columns([6, 1])

        with c1:
            st.markdown(
                f"""
                **{badge(row['severity'])} — {row['alert_type']}**
                - 📄 **Message:** {row['message']}
                - 📌 **Value:** `{row['value']}`
                - 🎯 **Expected:** `{row['expected']}`
                - 🕒 **Time:** {row['timestamp']}
                """
            )

        with c2:
            if row["resolved"] == 0:
                if st.button("✔ Resolve", key=row["id"]):
                    resolve_alert(row["id"])
                    st.rerun()
            else:
                st.markdown("### 🟢 Resolved")

# ---------------- RAW TABLE ----------------
st.subheader("📁 Raw Data Table")
st.dataframe(alerts)
