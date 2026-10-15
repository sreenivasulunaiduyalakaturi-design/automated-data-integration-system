# Automated Data Integration System

A simple ETL pipeline that automatically pulls customer data from multiple sources
(CSV, JSON, SQLite, optional REST API), cleans and de-duplicates it, and loads it
into a single unified warehouse database.

## Structure
| File | Purpose |
|---|---|
| `config.py` | Sources, column mappings, paths |
| `extractors.py` | Reads CSV / JSON / SQLite / API |
| `transformers.py` | Cleaning, validation, de-duplication |
| `loaders.py` | Upsert into `warehouse.db`, run logging |
| `sample_data.py` | Generates demo data |
| `main.py` | Orchestrator + scheduler |

## Run
```
pip install -r requirements.txt
python main.py --sample          # demo run
python main.py --interval 300    # automated, every 5 minutes
```
Add a new source by appending an entry to `SOURCES` in `config.py`.
