"""Central configuration: where data comes from and how it maps to the unified schema."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
WAREHOUSE_DB = DATA_DIR / "warehouse.db"
LOG_FILE = BASE_DIR / "integration.log"

# Unified schema every source is mapped into
UNIFIED_COLUMNS = ["source", "source_id", "name", "email", "phone", "city"]

# Each source: type, location, and a mapping {source_column: unified_column}
SOURCES = [
    {
        "name": "crm_csv",
        "type": "csv",
        "path": DATA_DIR / "customers_crm.csv",
        "mapping": {"id": "source_id", "full_name": "name", "email": "email",
                    "phone": "phone", "city": "city"},
    },
    {
        "name": "web_json",
        "type": "json",
        "path": DATA_DIR / "customers_web.json",
        "mapping": {"customer_id": "source_id", "name": "name",
                    "email_address": "email", "mobile": "phone", "location": "city"},
    },
    {
        "name": "legacy_db",
        "type": "sqlite",
        "path": DATA_DIR / "legacy.db",
        "query": "SELECT cid, first || ' ' || last AS name, mail, tel, town FROM clients",
        "mapping": {"cid": "source_id", "name": "name", "mail": "email",
                    "tel": "phone", "town": "city"},
    },
    # Optional REST API source (enable by setting "enabled": True and a real URL)
    {
        "name": "partner_api",
        "type": "api",
        "enabled": False,
        "url": "https://example.com/api/customers",
        "mapping": {"id": "source_id", "name": "name", "email": "email",
                    "phone": "phone", "city": "city"},
    },
]
