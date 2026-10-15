"""Extract step: read raw data from each kind of source into a DataFrame."""
import json
import sqlite3
import pandas as pd


def extract_csv(src):
    return pd.read_csv(src["path"], dtype=str)


def extract_json(src):
    with open(src["path"], encoding="utf-8") as f:
        return pd.DataFrame(json.load(f)).astype(str)


def extract_sqlite(src):
    with sqlite3.connect(src["path"]) as conn:
        return pd.read_sql_query(src["query"], conn).astype(str)


def extract_api(src):
    import requests  # imported lazily so it's optional
    resp = requests.get(src["url"], timeout=15)
    resp.raise_for_status()
    return pd.DataFrame(resp.json()).astype(str)


EXTRACTORS = {"csv": extract_csv, "json": extract_json,
              "sqlite": extract_sqlite, "api": extract_api}


def extract(src):
    """Extract one source and rename its columns to the unified schema."""
    df = EXTRACTORS[src["type"]](src)
    df = df.rename(columns=src["mapping"])
    df["source"] = src["name"]
    for col in ("source_id", "name", "email", "phone", "city"):
        if col not in df.columns:
            df[col] = None
    return df[["source", "source_id", "name", "email", "phone", "city"]]
