from __future__ import annotations

import os
from pathlib import Path

from dagster import Definitions, ScheduleDefinition, define_asset_job, load_assets_from_modules
from dotenv import load_dotenv

from mpls_public_safety import assets

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

incident_job = define_asset_job(
    name="incident_ingestion",
    selection=[
        "raw_incidents",
        "processed_incidents",
        "raw_communities",
        "raw_metro_places",
        "enriched_incidents",
        "neighborhood_case_counts",
        "neighborhood_case_bubbles",
    ],
)

incident_schedule = ScheduleDefinition(
    name="incident_ingestion_every_6_hours",
    cron_schedule=os.getenv("SCHEDULE_CRON", "0 */6 * * *"),
    job=incident_job,
)

defs = Definitions(
    assets=load_assets_from_modules([assets]),
    jobs=[incident_job],
    schedules=[incident_schedule],
)
