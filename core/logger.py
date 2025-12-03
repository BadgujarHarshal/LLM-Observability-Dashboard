# core/logger.py

import sqlite3
import uuid
from datetime import datetime

DB_PATH = "llm_logs.db"


class LLMLogger:

    @staticmethod
    def ensure_columns(conn):
        """Add missing columns without breaking existing DB."""
        existing_cols = [
            row[1] for row in conn.execute("PRAGMA table_info(llm_logs)").fetchall()
        ]

        required_cols = {
            "cost_inr": "ALTER TABLE llm_logs ADD COLUMN cost_inr REAL",
            "cost_usd": "ALTER TABLE llm_logs ADD COLUMN cost_usd REAL"
        }

        for col, query in required_cols.items():
            if col not in existing_cols:
                conn.execute(query)
                conn.commit()

    @staticmethod
    def log_text_interaction(
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
        temperature,
        error_type=None,
        rating=None,
        metadata=None
    ):
        conn = sqlite3.connect(DB_PATH)

        # Create table if not exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS llm_logs (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                session_id TEXT,
                user_id TEXT,
                model_name TEXT,
                prompt TEXT,
                response TEXT,
                tokens_in INTEGER,
                tokens_out INTEGER,
                latency_ms INTEGER,
                cost_usd REAL,
                cost_inr REAL,
                temperature REAL,
                error_type TEXT,
                rating INTEGER,
                metadata TEXT
            )
        """)

        # Ensure new columns exist
        LLMLogger.ensure_columns(conn)

        # Insert log row
        log_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        conn.execute("""
            INSERT INTO llm_logs (
                id, timestamp, session_id, user_id, model_name, prompt, response,
                tokens_in, tokens_out, latency_ms, cost_usd, cost_inr,
                temperature, error_type, rating, metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            log_id, timestamp, session_id, user_id, model_name, prompt, response,
            tokens_in, tokens_out, latency_ms, cost_usd, cost_inr,
            temperature, error_type, rating, metadata
        ))

        conn.commit()
        conn.close()
        return log_id


