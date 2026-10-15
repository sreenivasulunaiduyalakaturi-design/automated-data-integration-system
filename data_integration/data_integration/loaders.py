"""Load step: upsert unified records into the warehouse and log each run."""
import sqlite3
from datetime import datetime

SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
    email       TEXT PRIMARY KEY,
    source      TEXT,
    source_id   TEXT,
    name        TEXT,
    phone       TEXT,
    city        TEXT,
    updated_at  TEXT
);
CREATE TABLE IF NOT EXISTS etl_runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at  TEXT,
    status      TEXT,
    rows_extracted INTEGER,
    rows_loaded    INTEGER,
    message     TEXT
);
"""

UPSERT = """
INSERT INTO customers (email, source, source_id, name, phone, city, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(email) DO UPDATE SET
    source=excluded.source, source_id=excluded.source_id, name=excluded.name,
    phone=excluded.phone, city=excluded.city, updated_at=excluded.updated_at
"""


def load(df, db_path):
    now = datetime.now().isoformat(timespec="seconds")
    rows = [(r.email, r.source, r.source_id, r.name, r.phone, r.city, now)
            for r in df.itertuples(index=False)]
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.executemany(UPSERT, rows)
    return len(rows)


def log_run(db_path, started_at, status, extracted, loaded, message=""):
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.execute(
            "INSERT INTO etl_runs (started_at, status, rows_extracted, rows_loaded, message) "
            "VALUES (?, ?, ?, ?, ?)",
            (started_at, status, extracted, loaded, message))
