from __future__ import annotations

import logging
import os
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)


class ArcGISClient:
    def __init__(
        self,
        url: str,
        page_size: int = 2000,
        timeout: float = 60.0,
        retries: int = 3,
    ) -> None:
        self._url = url
        self._page_size = page_size
        self._timeout = timeout
        self._retries = retries
        self._session = requests.Session()

    @classmethod
    def from_env(cls, url_var: str, default_url: str) -> ArcGISClient:
        return cls(
            url=os.getenv(url_var, default_url),
            page_size=int(os.getenv("MPLS_PAGE_SIZE", "2000")),
            timeout=float(os.getenv("MPLS_REQUEST_TIMEOUT", "60")),
        )

    def fetch_features(self, return_geometry: bool = False) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        offset = 0
        while True:
            payload = self._get(
                {
                    "where": "1=1",
                    "outFields": "*",
                    "returnGeometry": "true" if return_geometry else "false",
                    "outSR": "4326",
                    "resultOffset": offset,
                    "resultRecordCount": self._page_size,
                    "f": "geojson" if return_geometry else "json",
                }
            )
            page = self._page(payload)
            records.extend(page)
            logger.info("retrieved %s records from %s (offset %s)", len(page), self._url, offset)
            if not page or not payload.get("exceededTransferLimit"):
                break
            offset += len(page)
        logger.info("retrieved %s records total from %s", len(records), self._url)
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
    def _page(payload: dict[str, Any]) -> list[dict[str, Any]]:
        if payload.get("type") == "FeatureCollection":
            records = []
            for feature in payload.get("features") or []:
                record = dict(feature.get("properties") or {})
                record["geometry"] = feature.get("geometry")
                records.append(record)
            return records
        records = []
        for feature in payload.get("features") or []:
            record = dict(feature.get("attributes") or {})
            if feature.get("geometry"):
                record["geometry"] = feature["geometry"]
            records.append(record)
        return records
