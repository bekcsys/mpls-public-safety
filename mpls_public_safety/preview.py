from __future__ import annotations

from typing import Any

import pandas as pd

RAW_PREVIEW_COLUMNS = (
    "caseNumber",
    "publicaddress",
    "reportedDateTime",
    "UCRCode",
    "centerLat",
    "centerLong",
)
PROCESSED_PREVIEW_COLUMNS = (
    "case_number",
    "public_address",
    "reported_at",
    "ucr_code",
    "latitude",
    "longitude",
)
ENRICHED_PREVIEW_COLUMNS = (
    "case_number",
    "public_address",
    "neighborhood",
    "community",
    "location_ring",
    "city",
    "location_label",
)
KEPT_RAW_COLUMNS = {
    "OBJECTID",
    "caseNumber",
    "reportedDateTime",
    "beginDate",
    "offense",
    "description",
    "precinct",
    "neighborhood",
    "publicaddress",
    "UCRCode",
    "centerLat",
    "centerLong",
}


def build_cleaning_preview(
    raw: pd.DataFrame,
    processed: pd.DataFrame | None = None,
    n: int = 5,
    enriched: pd.DataFrame | None = None,
    metro_places: pd.DataFrame | None = None,
    neighborhood_counts: pd.DataFrame | None = None,
) -> dict[str, Any]:
    raw_sample = _stringify(_select(raw, RAW_PREVIEW_COLUMNS).head(n))
    processed_sample = (
        _stringify(_select(processed, PROCESSED_PREVIEW_COLUMNS).head(n))
        if processed is not None
        else pd.DataFrame()
    )
    dropped = sorted(set(raw.columns) - KEPT_RAW_COLUMNS)
    sections = [
        f"raw rows: {len(raw)} ({len(raw.columns)} columns)",
        "raw sample",
        raw_sample.to_markdown(index=False),
    ]
    if processed is not None:
        sections[1:1] = [
            f"processed rows: {len(processed)} ({len(processed.columns)} columns)",
            f"dropped columns: {', '.join(dropped) if dropped else 'none'}",
        ]
        sections.extend(["processed sample", processed_sample.to_markdown(index=False)])
    if enriched is not None:
        enriched_sample = _stringify(_select(enriched, ENRICHED_PREVIEW_COLUMNS).head(n))
        sections.extend(
            [
                f"enriched rows: {len(enriched)} ({len(enriched.columns)} columns)",
                "enriched sample",
                enriched_sample.to_markdown(index=False),
            ]
        )
    if metro_places is not None and "city" in metro_places.columns:
        examples = metro_places.loc[
            metro_places["city"].str.casefold().isin(["edina", "minneapolis", "richfield"])
        ]
        if not examples.empty:
            sections.extend(["metro place examples", examples.to_markdown(index=False)])
    if neighborhood_counts is not None:
        sections.extend(
            [
                f"neighborhoods: {len(neighborhood_counts)}",
                "cases by neighborhood",
                neighborhood_counts.to_markdown(index=False),
            ]
        )
    return {
        "raw_count": len(raw),
        "processed_count": len(processed) if processed is not None else 0,
        "dropped_columns": dropped,
        "raw_sample": raw_sample.to_dict(orient="records"),
        "processed_sample": processed_sample.to_dict(orient="records"),
        "markdown": "\n\n".join(sections),
    }


def _select(frame: pd.DataFrame, columns: tuple[str, ...]) -> pd.DataFrame:
    present = [column for column in columns if column in frame.columns]
    return frame.loc[:, present].copy()


def _stringify(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.astype("string").fillna("")


if __name__ == "__main__":
    import os
    from pathlib import Path

    root = Path(os.getenv("DATA_DIR", "data"))
    raw_path = root / "raw" / "incidents.parquet"
    processed_path = root / "processed" / "incidents.parquet"
    enriched_path = root / "processed" / "incidents_enriched.parquet"
    metro_path = root / "raw" / "metro_places.parquet"
    counts_path = root / "processed" / "neighborhood_case_counts.parquet"
    if not raw_path.exists() or not processed_path.exists():
        raise SystemExit("Run `make materialize` first so raw and processed Parquet files exist.")
    print(
        build_cleaning_preview(
            pd.read_parquet(raw_path),
            pd.read_parquet(processed_path),
            enriched=pd.read_parquet(enriched_path) if enriched_path.exists() else None,
            metro_places=pd.read_parquet(metro_path) if metro_path.exists() else None,
            neighborhood_counts=pd.read_parquet(counts_path) if counts_path.exists() else None,
        )["markdown"]
    )
