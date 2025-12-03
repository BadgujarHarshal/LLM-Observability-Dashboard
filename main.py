# main.py

import time, os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

from core.db import init_db, get_connection
from core.logger import LLMLogger
from core.analytics import update_daily_metrics
from core.currency import get_inr_rate
from core.alerts import run_alert_checks

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

init_db()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def get_available_groq_model():
    try:
        model_list = client.models.list()
        model_ids = [m.id for m in model_list.data]
        preferred = ["llama", "mixtral", "gemma"]

        for k in preferred:
            for m in model_ids:
                if k in m.lower():
                    print(f"[MODEL SELECTED] {m}")
                    return m
        
        print(f"[MODEL SELECTED] {model_ids[0]}")
        return model_ids[0]

    except Exception as e:
        raise RuntimeError(f"Failed fetching models: {e}")


def call_llm(prompt, session_id="default", user_id="anonymous", temperature=0.7):
    model = get_available_groq_model()
    start = time.time()

    try:
        result = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )

        latency = int((time.time() - start) * 1000)
        response = result.choices[0].message.content

        # ===== COST HANDLING =====
        tokens = result.usage.total_tokens
        cost_usd = (tokens / 1_000_000) * 5
        cost_inr = cost_usd * get_inr_rate()

        log_id = LLMLogger.log_text_interaction(
            session_id=session_id,
            user_id=user_id,
            model_name=model,
            prompt=prompt,
            response=response,
            tokens_in=result.usage.prompt_tokens,
            tokens_out=result.usage.completion_tokens,
            latency_ms=latency,
            cost_usd=cost_usd,
            cost_inr=cost_inr,
            temperature=temperature
        )

        # -------- METRICS + ALERTS ----------
        update_daily_metrics()

        # Fetch log row + daily row for alert engine
        conn = get_connection()
        cur = conn.cursor()

        log_row = cur.execute("SELECT * FROM llm_logs WHERE id = ?", (log_id,)).fetchone()
        daily_row = cur.execute("SELECT * FROM llm_metrics_daily ORDER BY date DESC LIMIT 1").fetchone()

        if log_row and daily_row:
            # Convert log_row to dict
            log_cols = [c[1] for c in cur.execute("PRAGMA table_info(llm_logs)")]
            log_row = dict(zip(log_cols, log_row))

            # Convert daily_row to dict
            daily_cols = [c[1] for c in cur.execute("PRAGMA table_info(llm_metrics_daily)")]
            daily_row = dict(zip(daily_cols, daily_row))

        conn.close()

        if log_row and daily_row:
            run_alert_checks(log_row, daily_row)

        print(f"[LOGGED] → {log_id}")
        return response

    except Exception as e:
        latency = int((time.time() - start) * 1000)

        LLMLogger.log_text_interaction(
            session_id=session_id,
            user_id=user_id,
            model_name=model,
            prompt=prompt,
            response=None,
            tokens_in=0,
            tokens_out=0,
            latency_ms=latency,
            cost_usd=0,
            cost_inr=0,
            temperature=temperature,
            error_type=str(e)
        )

        update_daily_metrics()
        raise


if __name__ == "__main__":
    answer = call_llm("What is quantum computing?")
    print("\nMODEL RESPONSE:\n", answer)
