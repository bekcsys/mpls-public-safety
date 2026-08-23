from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd

CORE_CITIES = {"minneapolis", "saint paul", "st. paul", "st paul"}
RING_FROM_THRIVE = {
    "Urban Center": "First-Ring Suburbs",
    "Urban": "First-Ring Suburbs",
    "Suburban": "Second-Ring Suburbs",
    "Suburban Edge": "Suburban Edge",
    "Emerging Suburban Edge": "Suburban Edge",
    "Rural Center": "Rural",
    "Diversified Rural": "Rural",
    "Rural Residential": "Rural",
    "Agricultural": "Rural",
}


def enrich_incidents(
    incidents: pd.DataFrame,
    communities: Sequence[Mapping[str, Any]],
    metro_places: pd.DataFrame,
    city: str = "Minneapolis",
) -> pd.DataFrame:
    enriched = incidents.copy()
    place = _metro_place(metro_places, city)
    enriched["city"] = city
    enriched["metro_designation"] = place["metro_designation"]
    enriched["location_ring"] = place["location_ring"]
    enriched["community"] = [
        _community_for_point(row.get("longitude"), row.get("latitude"), communities)
        for row in enriched.to_dict(orient="records")
    ]
    enriched["location_label"] = [
        _location_label(
            ring=row["location_ring"],
            city=row["city"],
            community=row.get("community"),
            neighborhood=row.get("neighborhood"),
        )
        for row in enriched.to_dict(orient="records")
    ]
    return enriched


def classify_metro_places(records: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame.from_records(list(records))
    if frame.empty:
        return pd.DataFrame(columns=["city", "metro_designation", "location_ring"])
    name_col = "CTU_NAME" if "CTU_NAME" in frame.columns else "city"
    designation_col = "COMDESNAME" if "COMDESNAME" in frame.columns else "metro_designation"
    places = frame.rename(columns={name_col: "city", designation_col: "metro_designation"})
    places = places.loc[:, ["city", "metro_designation"]].dropna(subset=["city"])
    places["city"] = places["city"].astype("string").str.strip()
    places["metro_designation"] = places["metro_designation"].astype("string").str.strip()
    places["location_ring"] = [
        _location_ring(city, designation)
        for city, designation in zip(places["city"], places["metro_designation"], strict=True)
    ]
    return places.drop_duplicates(subset=["city", "location_ring"], keep="first").reset_index(drop=True)


def _metro_place(metro_places: pd.DataFrame, city: str) -> dict[str, str]:
    matches = metro_places.loc[metro_places["city"].str.casefold() == city.casefold()]
    if matches.empty:
        return {"metro_designation": pd.NA, "location_ring": _location_ring(city, "")}
    row = matches.iloc[0]
    return {
        "metro_designation": row["metro_designation"],
        "location_ring": row["location_ring"],
    }


def _location_ring(city: str, thrive_name: str) -> str:
    if str(city).casefold() in CORE_CITIES:
        return "Core Cities"
    return RING_FROM_THRIVE.get(str(thrive_name), "Unknown")


def _location_label(ring: str, city: str, community: Any, neighborhood: Any) -> str:
    parts = [value for value in (community, neighborhood) if pd.notna(value) and str(value).strip()]
    base = f"{ring}: {city}"
    if not parts:
        return base
    return f"{base} — {' — '.join(str(part).strip() for part in parts)}"


def _community_for_point(
    longitude: Any, latitude: Any, communities: Sequence[Mapping[str, Any]]
) -> str | None:
    try:
        lon = float(longitude)
        lat = float(latitude)
    except (TypeError, ValueError):
        return None
    for community in communities:
        geometry = community.get("geometry") or {}
        if _point_in_geometry(lon, lat, geometry):
            name = community.get("CommName") or community.get("community")
            return str(name).strip() if name else None
    return None


def _point_in_geometry(lon: float, lat: float, geometry: Mapping[str, Any]) -> bool:
    kind = geometry.get("type")
    if kind == "Polygon":
        return _point_in_polygon(lon, lat, geometry.get("coordinates") or [])
    if kind == "MultiPolygon":
        return any(_point_in_polygon(lon, lat, polygon) for polygon in geometry.get("coordinates") or [])
    return False


def _point_in_polygon(lon: float, lat: float, rings: Sequence[Sequence[Sequence[float]]]) -> bool:
    if not rings:
        return False
    if not _point_in_ring(lon, lat, rings[0]):
        return False
    return not any(_point_in_ring(lon, lat, hole) for hole in rings[1:])


def _point_in_ring(lon: float, lat: float, ring: Sequence[Sequence[float]]) -> bool:
    inside = False
    if len(ring) < 3:
        return False
    x_prev, y_prev = ring[-1][0], ring[-1][1]
    for x_curr, y_curr in ring:
        crosses = (y_curr > lat) != (y_prev > lat)
        if crosses:
            x_intersect = (x_prev - x_curr) * (lat - y_curr) / (y_prev - y_curr) + x_curr
            if lon < x_intersect:
                inside = not inside
        x_prev, y_prev = x_curr, y_curr
    return inside
