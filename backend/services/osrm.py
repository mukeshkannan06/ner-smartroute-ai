"""
OSRM Service — Real road routing via OpenStreetMap / OSRM
-----------------------------------------------------------
Uses the public OSRM demo server for the prototype.
Returns real road geometry, distance, and duration.
Falls back gracefully when the service is unavailable.
"""
import os
import asyncio
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

import httpx

OSRM_BASE_URL = os.getenv("OSRM_BASE_URL", "https://router.project-osrm.org")
OSRM_TIMEOUT = float(os.getenv("OSRM_TIMEOUT", "10"))


@dataclass
class OSRMRoute:
    distance_km: float
    duration_hours: float
    geometry: List[List[float]]  # [[lat, lon], ...]
    legs: List[Dict[str, Any]]
    route_summary: str


async def get_route(
    origin_lat: float, origin_lon: float,
    dest_lat: float, dest_lon: float,
    alternatives: int = 3
) -> Optional[List[OSRMRoute]]:
    """
    Get route(s) from OSRM.
    Returns a list of OSRMRoute objects, or None if the service is unavailable.
    """
    url = (
        f"{OSRM_BASE_URL}/route/v1/driving/"
        f"{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
    )
    params = {
        "overview": "full",
        "geometries": "geojson",
        "alternatives": str(min(alternatives, 3)),
        "steps": "true",
    }

    try:
        async with httpx.AsyncClient(timeout=OSRM_TIMEOUT) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        if data.get("code") != "Ok":
            return None

        routes = []
        for route_data in data.get("routes", []):
            geometry = route_data.get("geometry", {}).get("coordinates", [])
            # OSRM returns [lon, lat]; convert to [lat, lon] for Leaflet
            geometry_latlon = [[coord[1], coord[0]] for coord in geometry]

            legs = []
            for leg in route_data.get("legs", []):
                leg_info = {
                    "distance_km": round(leg.get("distance", 0) / 1000, 1),
                    "duration_hours": round(leg.get("duration", 0) / 3600, 2),
                    "summary": leg.get("summary", ""),
                    "steps": [
                        {
                            "instruction": step.get("maneuver", {}).get("type", ""),
                            "name": step.get("name", ""),
                            "distance_km": round(step.get("distance", 0) / 1000, 2),
                        }
                        for step in leg.get("steps", [])[:10]  # limit steps
                    ],
                }
                legs.append(leg_info)

            route = OSRMRoute(
                distance_km=round(route_data.get("distance", 0) / 1000, 1),
                duration_hours=round(route_data.get("duration", 0) / 3600, 2),
                geometry=geometry_latlon,
                legs=legs,
                route_summary=route_data.get("legs", [{}])[0].get("summary", "via road"),
            )
            routes.append(route)

        return routes if routes else None

    except (httpx.HTTPError, httpx.TimeoutException, Exception) as e:
        print(f"[OSRM] Service unavailable: {e}")
        return None


def get_route_sync(
    origin_lat: float, origin_lon: float,
    dest_lat: float, dest_lon: float,
    alternatives: int = 3
) -> Optional[List[OSRMRoute]]:
    """Synchronous wrapper for get_route."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already in an async context, we can't use run_until_complete
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run,
                    get_route(origin_lat, origin_lon, dest_lat, dest_lon, alternatives)
                )
                return future.result(timeout=OSRM_TIMEOUT + 2)
        else:
            return loop.run_until_complete(
                get_route(origin_lat, origin_lon, dest_lat, dest_lon, alternatives)
            )
    except Exception:
        return None
