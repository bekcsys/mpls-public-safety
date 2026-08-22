from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd

FIELD_MAP = {
    "OBJECTID": "object_id",
    "caseNumber": "case_number",
    "reportedDateTime": "reported_at",
    "beginDate": "begin_date",
    "offense": "offense",
    "description": "description",
    "precinct": "precinct",
    "neighborhood": "neighborhood",
    "publicaddress": "public_address",
    "UCRCode": "ucr_code",
    "centerLat": "latitude",
    "centerLong": "longitude",
}

TIMESTAMP_COLUMNS = ("reported_at", "begin_date")
TEXT_COLUMNS = (
    "case_number",
    "offense",
    "description",
    "precinct",
    "neighborhood",
    "public_address",
    "ucr_code",
)


def process_incidents(records: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    columns = list(FIELD_MAP.values())
    if not records:
        return pd.DataFrame(columns=columns)

    frame = pd.DataFrame.from_records(list(records))
    available = {source: target for source, target in FIELD_MAP.items() if source in frame.columns}
    processed = frame.loc[:, list(available)].rename(columns=available)

    for column in columns:
        if column not in processed.columns:
            processed[column] = pd.NA
    processed = processed[columns]

    for column in TIMESTAMP_COLUMNS:
        processed[column] = pd.to_datetime(processed[column], unit="ms", utc=True, errors="coerce")

    for column in TEXT_COLUMNS:
        processed[column] = processed[column].astype("string").str.strip()

    processed["latitude"] = pd.to_numeric(processed["latitude"], errors="coerce")
    processed["longitude"] = pd.to_numeric(processed["longitude"], errors="coerce")
    processed["object_id"] = pd.to_numeric(processed["object_id"], errors="coerce")

    has_case_number = processed["case_number"].notna() & (processed["case_number"] != "")
    unique = processed.loc[has_case_number].drop_duplicates(subset=["case_number"], keep="last")
    missing = processed.loc[~has_case_number]
    return pd.concat([unique, missing], ignore_index=True)
