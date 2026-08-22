import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from dagster import AssetExecutionContext, MetadataValue, asset

from mpls_public_safety.client import MinneapolisIncidentClient
from mpls_public_safety.processing import process_incidents


def _data_path(*parts: str) -> Path:
    path = Path(os.getenv("DATA_DIR", "data")).joinpath(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@asset
def raw_incidents(context: AssetExecutionContext) -> list[dict[str, Any]]:
    records = MinneapolisIncidentClient.from_env().fetch_incidents()
    output_path = _data_path("raw", "incidents.parquet")
    pd.DataFrame(records).to_parquet(output_path, index=False)
    context.add_output_metadata(
        {
            "num_records": len(records),
            "ingestion_timestamp": MetadataValue.text(
                datetime.now(timezone.utc).isoformat()
            ),
            "path": MetadataValue.path(str(output_path)),
        }
    )
    return records


@asset
def processed_incidents(
    context: AssetExecutionContext, raw_incidents: list[dict[str, Any]]
) -> pd.DataFrame:
    processed = process_incidents(raw_incidents)
    output_path = _data_path("processed", "incidents.parquet")
    processed.to_parquet(output_path, index=False)
    context.add_output_metadata(
        {
            "num_records": len(processed),
            "ingestion_timestamp": MetadataValue.text(
                datetime.now(timezone.utc).isoformat()
            ),
            "path": MetadataValue.path(str(output_path)),
        }
    )
    return processed
