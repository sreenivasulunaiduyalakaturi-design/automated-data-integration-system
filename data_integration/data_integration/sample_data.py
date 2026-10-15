"""Generate small demo datasets (with deliberate messiness) for testing."""
import json
import sqlite3
import pandas as pd
from config import DATA_DIR


def generate():
    DATA_DIR.mkdir(exist_ok=True)

    pd.DataFrame([
        {"id": "1", "full_name": " alice johnson ", "email": "Alice@Example.com", "phone": "+1 (555) 010-1111", "city": "new york"},
        {"id": "2", "full_name": "bob smith", "email": "bob@example.com", "phone": "555-010-2222", "city": "chicago"},
        {"id": "3", "full_name": "bad record", "email": "not-an-email", "phone": "", "city": ""},
    ]).to_csv(DATA_DIR / "customers_crm.csv", index=False)

    with open(DATA_DIR / "customers_web.json", "w") as f:
        json.dump([
            {"customer_id": "W10", "name": "Alice Johnson", "email_address": "alice@example.com", "mobile": "5550101111", "location": ""},
            {"customer_id": "W11", "name": "Carol White", "email_address": "carol@example.com", "mobile": "555 010 3333", "location": "austin"},
        ], f, indent=2)

    with sqlite3.connect(DATA_DIR / "legacy.db") as conn:
        conn.executescript("""
            DROP TABLE IF EXISTS clients;
            CREATE TABLE clients (cid INTEGER, first TEXT, last TEXT, mail TEXT, tel TEXT, town TEXT);
            INSERT INTO clients VALUES
              (100, 'dave', 'brown', 'dave@example.com', '555-010-4444', 'seattle'),
              (101, 'bob', 'smith', 'BOB@example.com', NULL, 'Chicago');
        """)
    print(f"Sample data written to {DATA_DIR}")


if __name__ == "__main__":
    generate()
