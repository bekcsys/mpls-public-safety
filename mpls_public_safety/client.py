from __future__ import annotations

import logging
import os
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)

DEFAULT_API_URL = (
    "https://services.arcgis.com/afSMGVsC7QlRK1kZ/arcgis/rest/services/"
    "Police_Incidents_Last_2Years/FeatureServer/0/query"
)


class MinneapolisIncidentClient:
    def __init__(
        self,
        url: str = DEFAULT_API_URL,
        page_size: int = 2000,
        timeout: float = 60.0,
        max_records: int | None = None,
        retries: int = 3,
    ) -> None:
        self._url = url
        self._page_size = page_size
        self._timeout = timeout
        self._max_records = max_records
        self._retries = retries
        self._session = requests.Session()

    @classmethod
    def from_env(cls) -> MinneapolisIncidentClient:
        max_records_raw = os.getenv("MPLS_MAX_RECORDS", "").strip()
        return cls(
            url=os.getenv("MPLS_API_URL", DEFAULT_API_URL),
            page_size=int(os.getenv("MPLS_PAGE_SIZE", "2000")),
            timeout=float(os.getenv("MPLS_REQUEST_TIMEOUT", "60")),
            max_records=int(max_records_raw) if max_records_raw else None,
        )

    def fetch_incidents(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        offset = 0
        while True:
            remaining = None
            if self._max_records is not None:
                remaining = self._max_records - len(records)
                if remaining <= 0:
                    break
            page_size = self._page_size if remaining is None else min(self._page_size, remaining)
            payload = self._get(
                {
                    "where": "1=1",
                    "outFields": "*",
                    "returnGeometry": "true",
                    "outSR": "4326",
                    "resultOffset": offset,
                    "resultRecordCount": page_size,
                    "f": "json",
                }
            )
            features = payload.get("features") or []
            records.extend(self._flatten(feature) for feature in features)
            logger.info("retrieved %s records (offset %s)", len(features), offset)
            if not features or not payload.get("exceededTransferLimit"):
                break
            offset += len(features)
        logger.info("retrieved %s records total", len(records))
        return records

    def _get(self, params: dict[str, Any]) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(1, self._retries + 1):
            try:
                response = self._session.get(self._url, params=params, timeout=self._timeout)
                response.raise_for_status()
                payload = response.json()
                if payload.get("error"):
                    raise RuntimeError(payload["error"])
                return payload
            except (requests.RequestException, ValueError, RuntimeError) as exc:
                last_error = exc
                logger.warning("request failed (attempt %s/%s): %s", attempt, self._retries, exc)
                time.sleep(attempt)
        raise RuntimeError(f"API request failed after {self._retries} attempts") from last_error

    @staticmethod
    def _flatten(feature: dict[str, Any]) -> dict[str, Any]:
        record = dict(feature.get("attributes") or {})
        geometry = feature.get("geometry") or {}
        if record.get("centerLat") is None and geometry.get("y") is not None:
            record["centerLat"] = geometry["y"]
        if record.get("centerLong") is None and geometry.get("x") is not None:
            record["centerLong"] = geometry["x"]
        return record
