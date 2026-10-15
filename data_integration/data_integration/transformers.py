"""Transform step: clean, validate and de-duplicate the combined data."""
import logging
import re
import pandas as pd

log = logging.getLogger(__name__)
EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


def _clean_phone(value):
    if pd.isna(value):
        return None
    digits = re.sub(r"\D", "", str(value))
    return digits[-10:] if len(digits) >= 10 else (digits or None)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.replace({"None": None, "nan": None, "": None})

    df["email"] = df["email"].str.strip().str.lower()
    df["name"] = df["name"].str.strip().str.title()
    df["city"] = df["city"].str.strip().str.title()
    df["phone"] = df["phone"].map(_clean_phone)

    # Validation: drop rows with missing / malformed email (our unique key)
    valid = df["email"].fillna("").map(lambda e: bool(EMAIL_RE.match(e)))
    log.info("Dropping %d rows with invalid email", (~valid).sum())
    df = df[valid]

    # Dedup: keep the most complete record per email
    df["_completeness"] = df[["name", "phone", "city"]].notna().sum(axis=1)
    before = len(df)
    df = (df.sort_values("_completeness", ascending=False)
            .drop_duplicates(subset="email", keep="first")
            .drop(columns="_completeness"))
    log.info("Removed %d duplicate records", before - len(df))
    return df.reset_index(drop=True)
