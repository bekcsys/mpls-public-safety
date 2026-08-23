from __future__ import annotations

import pandas as pd


def aggregate_cases_by_neighborhood(incidents: pd.DataFrame) -> pd.DataFrame:
    frame = incidents.copy()
    if "neighborhood" not in frame.columns:
        raise ValueError("incidents must include a neighborhood column")
    frame["neighborhood"] = frame["neighborhood"].astype("string").str.strip()
    frame["neighborhood"] = frame["neighborhood"].replace("", pd.NA)
    case_col = "case_number" if "case_number" in frame.columns else "caseNumber"
    aggregations = {case_col: "nunique"}
    if "community" in frame.columns:
        aggregations["community"] = "first"
    if "latitude" in frame.columns:
        aggregations["latitude"] = "mean"
    if "longitude" in frame.columns:
        aggregations["longitude"] = "mean"
    grouped = (
        frame.dropna(subset=["neighborhood"])
        .groupby("neighborhood", dropna=False, as_index=False)
        .agg(aggregations)
        .rename(columns={case_col: "case_count"})
    )
    return grouped.sort_values(
        ["case_count", "neighborhood"], ascending=[False, True], ignore_index=True
    )
