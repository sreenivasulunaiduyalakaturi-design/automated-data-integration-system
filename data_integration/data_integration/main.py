"""Automated Data Integration System - pipeline orchestrator.

Usage:
    python main.py --sample            # create demo data and run once
    python main.py                     # run once
    python main.py --interval 300      # run every 300 seconds (automated)
"""
import argparse
import logging
import sqlite3
import time
from datetime import datetime

import pandas as pd

import config
from extractors import extract
from transformers import transform
from loaders import load, log_run

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(config.LOG_FILE), logging.StreamHandler()],
)
log = logging.getLogger("pipeline")


def run_pipeline():
    started = datetime.now().isoformat(timespec="seconds")
    config.DATA_DIR.mkdir(exist_ok=True)
    frames, errors = [], []

    # EXTRACT - one failing source must not stop the others
    for src in config.SOURCES:
        if src.get("enabled", True) is False:
            continue
        try:
            df = extract(src)
            log.info("Extracted %d rows from %s", len(df), src["name"])
            frames.append(df)
        except Exception as exc:
            log.error("Source %s failed: %s", src["name"], exc)
            errors.append(f"{src['name']}: {exc}")

    if not frames:
        log_run(config.WAREHOUSE_DB, started, "FAILED", 0, 0, "; ".join(errors))
        log.error("No data extracted, aborting run")
        return

    combined = pd.concat(frames, ignore_index=True)

    # TRANSFORM
    clean = transform(combined)

    # LOAD
    loaded = load(clean, config.WAREHOUSE_DB)
    status = "PARTIAL" if errors else "SUCCESS"
    log_run(config.WAREHOUSE_DB, started, status, len(combined), loaded, "; ".join(errors))
    log.info("Run %s: %d extracted -> %d loaded", status, len(combined), loaded)


def show_results():
    with sqlite3.connect(config.WAREHOUSE_DB) as conn:
        print("\n=== customers (unified) ===")
        print(pd.read_sql_query("SELECT email, name, phone, city, source FROM customers", conn).to_string(index=False))
        print("\n=== etl_runs ===")
        print(pd.read_sql_query("SELECT * FROM etl_runs", conn).to_string(index=False))


def main():
    parser = argparse.ArgumentParser(description="Automated Data Integration System")
    parser.add_argument("--sample", action="store_true", help="generate demo data first")
    parser.add_argument("--interval", type=int, default=0, help="repeat every N seconds (0 = run once)")
    args = parser.parse_args()

    if args.sample:
        from sample_data import generate
        generate()

    if args.interval > 0:
        log.info("Scheduler started: running every %d seconds (Ctrl+C to stop)", args.interval)
        try:
            while True:
                run_pipeline()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            log.info("Scheduler stopped")
    else:
        run_pipeline()
        show_results()


if __name__ == "__main__":
    main()
