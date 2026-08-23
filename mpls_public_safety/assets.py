import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from dagster import AssetExecutionContext, MetadataValue, asset

from mpls_public_safety.aggregate import aggregate_cases_by_neighborhood
from mpls_public_safety.arcgis import ArcGISClient
from mpls_public_safety.client import MinneapolisIncidentClient
from mpls_public_safety.location import classify_metro_places, enrich_incidents
from mpls_public_safety.preview import build_cleaning_preview
from mpls_public_safety.processing import process_incidents
from viz.neighborhoods import plot_neighborhood_case_bubbles

COMMUNITIES_URL = (
    "https://services.arcgis.com/afSMGVsC7QlRK1kZ/arcgis/rest/services/"
    "Minneapolis_Communities/FeatureServer/0/query"
)
METRO_PLACES_URL = (
    "https://gis.metc.state.mn.us/arcgis/rest/services/cd/ThriveComDes/MapServer/0/query"
)


def _data_path(*parts: str) -> Path:
    path = Path(os.getenv("DATA_DIR", "data")).joinpath(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@asset
def raw_incidents(context: AssetExecutionContext) -> list[dict[str, Any]]:
    records = MinneapolisIncidentClient.from_env().fetch_incidents()
    raw = pd.DataFrame(records)
    output_path = _data_path("raw", "incidents.parquet")
    raw.to_parquet(output_path, index=False)
    preview = build_cleaning_preview(raw)
    context.add_output_metadata(
        {
            "num_records": len(records),
            "ingestion_timestamp": MetadataValue.text(
                datetime.now(timezone.utc).isoformat()
            ),
            "path": MetadataValue.path(str(output_path)),
            "preview": MetadataValue.md(preview["markdown"]),
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
    preview = build_cleaning_preview(pd.DataFrame(raw_incidents), processed)
    context.add_output_metadata(
        {
            "num_records": len(processed),
            "ingestion_timestamp": MetadataValue.text(
                datetime.now(timezone.utc).isoformat()
            ),
            "path": MetadataValue.path(str(output_path)),
            "preview": MetadataValue.md(preview["markdown"]),
        }
    )
    return processed


@asset
def raw_communities(context: AssetExecutionContext) -> list[dict[str, Any]]:
    records = ArcGISClient.from_env("MPLS_COMMUNITIES_URL", COMMUNITIES_URL).fetch_features(
        return_geometry=True
    )
    output_path = _data_path("raw", "communities.parquet")
    slim = pd.DataFrame(records).drop(columns=["geometry"], errors="ignore")
    slim.to_parquet(output_path, index=False)
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
def raw_metro_places(context: AssetExecutionContext) -> pd.DataFrame:
    records = ArcGISClient.from_env("METRO_PLACES_URL", METRO_PLACES_URL).fetch_features()
    places = classify_metro_places(records)
    output_path = _data_path("raw", "metro_places.parquet")
    places.to_parquet(output_path, index=False)
    context.add_output_metadata(
        {
            "num_records": len(places),
            "ingestion_timestamp": MetadataValue.text(
                datetime.now(timezone.utc).isoformat()
            ),
            "path": MetadataValue.path(str(output_path)),
            "edina": MetadataValue.md(
                places.loc[places["city"].str.casefold() == "edina"].to_markdown(index=False)
            ),
        }
    )
    return places


@asset
def enriched_incidents(
    context: AssetExecutionContext,
    processed_incidents: pd.DataFrame,
    raw_communities: list[dict[str, Any]],
    raw_metro_places: pd.DataFrame,
) -> pd.DataFrame:
    enriched = enrich_incidents(processed_incidents, raw_communities, raw_metro_places)
    output_path = _data_path("processed", "incidents_enriched.parquet")
    enriched.to_parquet(output_path, index=False)
    preview_cols = [
        "case_number",
        "public_address",
        "neighborhood",
        "community",
        "location_ring",
        "city",
        "location_label",
    ]
    context.add_output_metadata(
        {
            "num_records": len(enriched),
            "communities_matched": int(enriched["community"].notna().sum()),
            "ingestion_timestamp": MetadataValue.text(
                datetime.now(timezone.utc).isoformat()
            ),
            "path": MetadataValue.path(str(output_path)),
            "preview": MetadataValue.md(
                enriched.loc[:, preview_cols].head(8).to_markdown(index=False)
            ),
        }
    )
    return enriched


@asset
def neighborhood_case_counts(
    context: AssetExecutionContext, enriched_incidents: pd.DataFrame
) -> pd.DataFrame:
    counts = aggregate_cases_by_neighborhood(enriched_incidents)
    output_path = _data_path("processed", "neighborhood_case_counts.parquet")
    counts.to_parquet(output_path, index=False)
    context.add_output_metadata(
        {
            "num_neighborhoods": len(counts),
            "num_cases": int(counts["case_count"].sum()),
            "path": MetadataValue.path(str(output_path)),
            "preview": MetadataValue.md(counts.head(15).to_markdown(index=False)),
        }
    )
    return counts


@asset
def neighborhood_case_bubbles(
    context: AssetExecutionContext, neighborhood_case_counts: pd.DataFrame
) -> str:
    geojson_path = _data_path("raw", "neighborhoods.geojson")
    neighborhoods = json.loads(geojson_path.read_text())
    figure = plot_neighborhood_case_bubbles(neighborhood_case_counts, neighborhoods)
    output_path = _data_path("processed", "neighborhood_bubbles.html")
    figure.write_html(
        output_path,
        include_plotlyjs="cdn",
        config={"scrollZoom": True, "displaylogo": False},
    )
    context.add_output_metadata(
        {
            "num_neighborhoods": len(neighborhood_case_counts),
            "path": MetadataValue.path(str(output_path)),
        }
    )
    return str(output_path)
