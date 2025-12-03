# dashboard/pages/Analytics.py

import streamlit as st
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# ---------- DB PATH (absolute for reliability) ----------
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "llm_logs.db"))

st.set_page_config(page_title="📈 Deep Analytics", layout="wide")
st.title("📈 Deep Analytics — LLM Performance Insights")


# ---------- DB QUERY HELPER (safe) ----------
def get_data(query):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


# ---------- Load logs ----------
logs = get_data("SELECT * FROM llm_logs ORDER BY timestamp DESC")

if logs.empty:
    st.warning("No logs available yet — run `python main.py` to generate logs.")
    st.stop()


# ============================================================
# 💰 COST TREND (USD + INR)
# ============================================================
st.subheader("💰 Cost Trend (USD + INR)")

cost_df = logs.copy()
cost_df["date"] = pd.to_datetime(cost_df["timestamp"]).dt.date
daily_cost = cost_df.groupby("date")[["cost_usd", "cost_inr"]].sum()

st.line_chart(daily_cost)


# ============================================================
# ⚡ Tokens vs Latency KDE HEATMAP
# ============================================================
st.subheader("⚡ Tokens vs Latency Heatmap")

fig, ax = plt.subplots()
sns.kdeplot(
    data=logs,
    x="tokens_in",
    y="latency_ms",
    fill=True,
    cmap="viridis",
    thresh=0.05,
    ax=ax
)
ax.set_xlabel("Tokens In")
ax.set_ylabel("Latency (ms)")
st.pyplot(fig)


# ============================================================
# 🤖 MODEL PERFORMANCE RANKING
# ============================================================
st.subheader("🤖 Model Performance Comparison")

model_df = logs.groupby("model_name").agg({
    "latency_ms": "mean",
    "cost_usd": "mean",
    "cost_inr": "mean",
    "error_type": lambda x: x.notnull().mean() * 100
}).rename(columns={"error_type": "error_rate(%)"})

st.dataframe(model_df)

st.bar_chart(model_df["latency_ms"])
st.bar_chart(model_df["cost_inr"])


# ============================================================
# 🧠 TOP PROMPTS BY EFFECTIVENESS
# ============================================================
st.subheader("🧠 Prompt Effectiveness Ranking")

prompt_df = logs.groupby("prompt").agg({
    "cost_inr": "mean",
    "latency_ms": "mean",
    "error_type": lambda x: x.notnull().mean() * 100
}).rename(columns={"error_type": "error_rate(%)"}).sort_values("error_rate(%)")

st.dataframe(prompt_df.head(20))


# ============================================================
# ⚠ ERROR SPIKE DETECTION
# ============================================================
st.subheader("⚠ Error Spike Days")

err_df = logs.copy()
err_df["date"] = pd.to_datetime(err_df["timestamp"]).dt.date
error_days = err_df.groupby("date")["error_type"].apply(lambda x: x.notnull().sum())

st.line_chart(error_days)


# ============================================================
# 🔍 CORRELATION MATRIX
# ============================================================
st.subheader("🔍 Correlation Matrix — What affects latency and cost?")

corr = logs[["tokens_in", "tokens_out", "latency_ms", "cost_inr", "cost_usd"]].corr()

fig, ax = plt.subplots(figsize=(6, 4))
sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig)
