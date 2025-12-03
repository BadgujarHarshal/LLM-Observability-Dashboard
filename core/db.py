# core/db.py

import sqlite3
import os

# Always create DB in project root
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "llm_logs.db")
DB_PATH = os.path.abspath(DB_PATH)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db():
    conn = get_connection()

    # ----------- MAIN LOGS TABLE ----------- #
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
    );
    """)

    # -------- MULTIMODAL INPUT LOG TABLE -------- #
    conn.execute("""
    CREATE TABLE IF NOT EXISTS llm_multimodal_inputs (
        id TEXT PRIMARY KEY,
        log_id TEXT,
        input_type TEXT,
        file_path TEXT,
        file_hash TEXT,
        metadata TEXT
    );
    """)

    # -------- MULTIMODAL OUTPUT LOG TABLE -------- #
    conn.execute("""
    CREATE TABLE IF NOT EXISTS llm_multimodal_outputs (
        id TEXT PRIMARY KEY,
        log_id TEXT,
        output_type TEXT,
        file_path TEXT,
        metadata TEXT
    );
    """)

    # ----------- DAILY METRICS TABLE ----------- #
    conn.execute("""
    CREATE TABLE IF NOT EXISTS llm_metrics_daily (
        date TEXT PRIMARY KEY,
        total_requests INTEGER,
        avg_latency_ms REAL,
        error_count INTEGER,
        avg_tokens_in REAL,
        avg_tokens_out REAL,
        total_cost_usd REAL,
        total_cost_inr REAL
    );
    """)

    # ----------- ALERTS TABLE ----------- #
    conn.execute("""
    CREATE TABLE IF NOT EXISTS llm_alerts (
        id TEXT PRIMARY KEY,
        timestamp TEXT,
        alert_type TEXT,
        message TEXT,
        severity TEXT,   -- info / warning / critical
        value REAL,
        expected REAL,
        resolved INTEGER DEFAULT 0
    );
    """)

    conn.commit()
    conn.close()
