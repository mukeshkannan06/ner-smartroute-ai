"""
Unified Routing Service
-------------------------
Combines OSRM real road routing with existing optimizer scoring.
Falls back to NetworkX graph routing when OSRM is unavailable.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

from .osrm import get_route as osrm_get_route, OSRMRoute
from .geocoding import geocode, KNOWN_LOCATIONS, GeocodingResult
from .. import optimizer
from ..graph_data import NODES, ROADS, all_node_names
from ..hazards.hazard_engine import analyze_route_hazards


@dataclass
class EnrichedRoute:
    """A route enriched with SmartRoute AI analytics."""
    route_index: int
    path: List[str]
    distance_km: float
    duration_hours: float
    geometry: List[List[float]]  # [[lat, lon], ...] for Leaflet
    risk_probability: float
    risk_level: str
    accessibility_score: float
    estimated_cost_inr: float
    overall_score: float
    roads_used: List[str]
    route_summary: str
    source: str  # "osrm" or "prototype"
    legs_detail: List[Dict[str, Any]]
    safety_score: float = 80.0
    disaster_risk: float = 20.0
    hazard_breakdown: Dict[str, float] = None
    hazard_warnings: List[str] = None
    segment_points: List[Dict[str, Any]] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["total_distance_km"] = self.distance_km
        d["eta_hours"] = self.duration_hours
        d["total_eta_hours"] = self.duration_hours
        return d


def _apply_hazard_analysis(
    geometry: List[List[float]],
    season_monsoon: bool,
    base_risk_probability: float,
    base_accessibility: float,
    base_overall_score: float,
    has_prototype_match: bool,
) -> Dict[str, Any]:
    """
    Run the multi-hazard engine over a route's real road geometry and blend the
    result with any prototype (in-memory graph) scoring that is available.

    Returns a dict of fields to merge into an EnrichedRoute.
    """
    hazard = analyze_route_hazards(geometry, season_monsoon=season_monsoon)
    disaster_risk = hazard["overall_disaster_risk"]
    safety_score = hazard["safety_score"]

    if has_prototype_match:
        # Blend: prototype ML risk model + live hazard-engine analysis.
        risk_probability = round(min(1.0, max(base_risk_probability, disaster_risk / 100.0)), 3)
        accessibility_score = round(min(base_accessibility, safety_score), 1)
    else:
        # No prototype graph coverage (route outside the NER demo network) —
        # the hazard engine is the sole source of truth for risk/accessibility.
        risk_probability = round(disaster_risk / 100.0, 3)
        accessibility_score = safety_score

    risk_level = hazard["hazard_level"]

    # Overall score: start from ETA/cost-based prototype score (or a neutral
    # default), then apply a strong penalty for disaster risk so hazardous
    # routes rank below safer alternatives.
    overall_score = round(max(5.0, base_overall_score - disaster_risk * 0.6), 1)

    return {
        "risk_probability": risk_probability,
        "risk_level": risk_level,
        "accessibility_score": accessibility_score,
        "overall_score": overall_score,
        "safety_score": safety_score,
        "disaster_risk": disaster_risk,
        "hazard_breakdown": {
            "flood_risk": hazard["flood_risk"],
            "landslide_risk": hazard["landslide_risk"],
            "cyclone_risk": hazard["cyclone_risk"],
            "rainfall_risk": hazard["rainfall_risk"],
            "road_closure_risk": hazard["road_closure_risk"],
        },
        "hazard_warnings": hazard["warnings"],
        "segment_points": hazard["segment_points"],
    }


async def plan_route(
    origin: str,
    destination: str,
    vehicle_type: str = "truck",
    weight_tonnes: float = 2.0,
    cargo: str = "",
    season_monsoon: bool = False,
    peak_hour: bool = False,
    mode: str = "balanced",
) -> Dict[str, Any]:
    """
    Plan a route with full SmartRoute AI analysis.
    Tries OSRM first, falls back to prototype graph routing.
    """
    # Step 1: Resolve locations to coordinates
    origin_coords = await _resolve_location(origin)
    dest_coords = await _resolve_location(destination)

    if not origin_coords:
        return {"error": f"Could not find location: {origin}", "success": False}
    if not dest_coords:
        return {"error": f"Could not find location: {destination}", "success": False}

    # Step 2: Try OSRM for real road geometry
    osrm_routes = await osrm_get_route(
        origin_coords["lat"], origin_coords["lon"],
        dest_coords["lat"], dest_coords["lon"],
        alternatives=3,
    )

    # Step 3: Get prototype scoring data
    origin_node = _find_nearest_node(origin_coords["lat"], origin_coords["lon"], origin)
    dest_node = _find_nearest_node(dest_coords["lat"], dest_coords["lon"], destination)

    prototype_candidates = []
    if origin_node and dest_node:
        prototype_candidates = optimizer.rank_routes(
            origin_node, dest_node,
            vehicle_type=vehicle_type,
            weight_tonnes=weight_tonnes,
            season_monsoon=season_monsoon,
            peak_hour=peak_hour,
        )

    # Step 4: Build enriched routes
    enriched_routes = []

    if osrm_routes:
        # Use OSRM geometry + prototype scoring
        for idx, osrm_route in enumerate(osrm_routes):
            # Match with prototype candidate if available
            proto = prototype_candidates[idx] if idx < len(prototype_candidates) else None
            if proto is None and prototype_candidates:
                proto = prototype_candidates[0]

            hazard_fields = _apply_hazard_analysis(
                geometry=osrm_route.geometry,
                season_monsoon=season_monsoon,
                base_risk_probability=proto.avg_risk_probability if proto else 0.2,
                base_accessibility=proto.avg_accessibility if proto else 75.0,
                base_overall_score=proto.overall_score if proto else 70.0,
                has_prototype_match=proto is not None,
            )

            enriched = EnrichedRoute(
                route_index=idx,
                path=proto.path_nodes if proto else [origin, destination],
                distance_km=osrm_route.distance_km,
                duration_hours=osrm_route.duration_hours,
                geometry=osrm_route.geometry,
                risk_probability=hazard_fields["risk_probability"],
                risk_level=hazard_fields["risk_level"],
                accessibility_score=hazard_fields["accessibility_score"],
                estimated_cost_inr=proto.estimated_cost_inr if proto else round(osrm_route.distance_km * 32, 0),
                overall_score=hazard_fields["overall_score"],
                roads_used=[l.road.road_id for l in proto.legs] if proto else [],
                route_summary=osrm_route.route_summary,
                source="osrm",
                legs_detail=[
                    {
                        "distance_km": leg["distance_km"],
                        "duration_hours": leg["duration_hours"],
                        "summary": leg["summary"],
                    }
                    for leg in osrm_route.legs
                ],
                safety_score=hazard_fields["safety_score"],
                disaster_risk=hazard_fields["disaster_risk"],
                hazard_breakdown=hazard_fields["hazard_breakdown"],
                hazard_warnings=hazard_fields["hazard_warnings"],
                segment_points=hazard_fields["segment_points"],
            )
            enriched_routes.append(enriched)
    elif prototype_candidates:
        # Fallback: OSRM unreachable — use prototype graph routing.
        # Geometry is still node-to-node (no real road shape is available
        # without OSRM), but this path is now clearly labeled as prototype
        # data rather than presented as a real road route.
        for idx, proto in enumerate(prototype_candidates):
            geometry = _generate_prototype_geometry(proto.path_nodes)
            hazard_fields = _apply_hazard_analysis(
                geometry=geometry,
                season_monsoon=season_monsoon,
                base_risk_probability=proto.avg_risk_probability,
                base_accessibility=proto.avg_accessibility,
                base_overall_score=proto.overall_score,
                has_prototype_match=True,
            )
            enriched = EnrichedRoute(
                route_index=idx,
                path=proto.path_nodes,
                distance_km=proto.total_distance_km,
                duration_hours=proto.total_eta_hours,
                geometry=geometry,
                risk_probability=hazard_fields["risk_probability"],
                risk_level=hazard_fields["risk_level"],
                accessibility_score=hazard_fields["accessibility_score"],
                estimated_cost_inr=proto.estimated_cost_inr,
                overall_score=hazard_fields["overall_score"],
                roads_used=[l.road.road_id for l in proto.legs],
                route_summary=" → ".join(proto.path_nodes),
                source="prototype",
                legs_detail=[
                    {
                        "road_id": leg.road.road_id,
                        "from": leg.road.a,
                        "to": leg.road.b,
                        "distance_km": leg.road.distance_km,
                        "duration_hours": leg.eta_hours,
                        "risk": leg.risk,
                        "accessibility": leg.accessibility.total,
                    }
                    for leg in proto.legs
                ],
                safety_score=hazard_fields["safety_score"],
                disaster_risk=hazard_fields["disaster_risk"],
                hazard_breakdown=hazard_fields["hazard_breakdown"],
                hazard_warnings=hazard_fields["hazard_warnings"],
                segment_points=hazard_fields["segment_points"],
            )
            enriched_routes.append(enriched)
    else:
        return {
            "error": "No route found between these locations",
            "success": False,
        }

    # Rank routes according to the requested mode.
    mode = (mode or "balanced").lower()
    if mode == "fastest":
        enriched_routes.sort(key=lambda r: r.duration_hours)
    elif mode == "safest" or mode == "emergency":
        enriched_routes.sort(key=lambda r: (-r.safety_score, r.duration_hours))
    elif mode == "lowest_cost":
        enriched_routes.sort(key=lambda r: r.estimated_cost_inr)
    else:  # balanced
        enriched_routes.sort(key=lambda r: r.overall_score, reverse=True)

    for i, r in enumerate(enriched_routes):
        r.route_index = i

    routing_source = "osrm" if osrm_routes else "prototype"
    # OSRM/Nominatim provide live road geometry & real-world coordinates;
    # the hazard/weather layer is prototype/simulated data (see section 33).
    data_mode = "live_roads_prototype_hazards" if osrm_routes else "prototype"

    return {
        "success": True,
        "origin": {"name": origin, **origin_coords},
        "destination": {"name": destination, **dest_coords},
        "cargo": cargo,
        "vehicle_type": vehicle_type,
        "weight_tonnes": weight_tonnes,
        "mode": mode,
        "routing_source": routing_source,
        "data_mode": data_mode,
        "routes": [r.to_dict() for r in enriched_routes],
        "candidates": [r.to_dict() for r in enriched_routes],
        "recommended": enriched_routes[0].to_dict() if enriched_routes else None,
        "total_routes": len(enriched_routes),
    }


async def _resolve_location(name: str) -> Optional[Dict[str, float]]:
    """Resolve a location name to lat/lon coordinates."""
    # Check if it's a known node first
    name_lower = name.strip().lower()
    for node_name, data in NODES.items():
        if node_name.lower() == name_lower:
            return {"lat": data["lat"], "lon": data["lon"]}

    # Try geocoding
    results = await geocode(name)
    if results:
        return {"lat": results[0].lat, "lon": results[0].lon}

    return None


def _find_nearest_node(lat: float, lon: float, name: str = "") -> Optional[str]:
    """Find the nearest node in the prototype graph to given coordinates."""
    # Exact name match first
    name_lower = name.strip().lower()
    for node_name in NODES:
        if node_name.lower() == name_lower:
            return node_name

    # Distance-based match
    best_node = None
    best_dist = float("inf")
    for node_name, data in NODES.items():
        dist = ((lat - data["lat"]) ** 2 + (lon - data["lon"]) ** 2) ** 0.5
        if dist < best_dist:
            best_dist = dist
            best_node = node_name

    # Only match if within ~1 degree (~100km)
    return best_node if best_dist < 1.5 else None


def _generate_prototype_geometry(path_nodes: List[str]) -> List[List[float]]:
    """Generate geometry from prototype node coordinates (straight lines between nodes)."""
    geometry = []
    for node in path_nodes:
        if node in NODES:
            geometry.append([NODES[node]["lat"], NODES[node]["lon"]])
    return geometry
