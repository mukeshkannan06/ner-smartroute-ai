"""
AI Tools — Backend function wrappers for the chatbot
------------------------------------------------------
Each tool calls existing backend functions to get real calculated data.
The chatbot should NEVER invent numbers — these tools are the source of truth.
"""
import asyncio
from typing import Dict, Any, Optional

from .. import optimizer, digital_twin
from ..graph_data import NODES, ROADS, road_by_id, PROTOTYPE_INCIDENTS
from ..services.weather_service import get_current_weather, get_route_weather
from ..services import routing as routing_service


TOOL_DEFINITIONS = [
    {
        "name": "plan_route",
        "description": "Find the best route between two NER cities with risk, accessibility, ETA, and cost analysis",
        "parameters": {
            "origin": "Origin city name",
            "destination": "Destination city name",
            "vehicle_type": "Vehicle type (truck, mini_truck, van, car)",
            "weight_tonnes": "Cargo weight in tonnes",
            "cargo": "Cargo description",
        },
    },
    {
        "name": "get_weather",
        "description": "Get current weather conditions for a location in NER",
        "parameters": {"location": "City or road name"},
    },
    {
        "name": "get_incidents",
        "description": "Get active incidents and alerts in the NER road network",
        "parameters": {"location": "Optional specific location"},
    },
    {
        "name": "get_accessibility",
        "description": "Get road accessibility scores for NER corridors",
        "parameters": {"road_id": "Optional road ID for specific road"},
    },
    {
        "name": "calculate_logistics",
        "description": "Calculate logistics cost for transporting cargo between two cities",
        "parameters": {
            "origin": "Origin city",
            "destination": "Destination city",
            "weight_tonnes": "Weight in tonnes",
            "vehicle_type": "Vehicle type",
        },
    },
    {
        "name": "simulate_closure",
        "description": "Simulate a road closure and see the impact on the network",
        "parameters": {"road_id": "Road segment ID to close"},
    },
]


def plan_route(
    origin: str, destination: str,
    vehicle_type: str = "truck", weight_tonnes: float = 2.0,
    cargo: str = "General",
    season_monsoon: bool = False,
    peak_hour: bool = False,
    mode: str = "balanced",
) -> Dict[str, Any]:
    """
    Plan a route for the assistant.

    For the built-in NER demo network (both endpoints are known nodes), use
    the fast in-memory optimizer directly. For ANY other pair of Indian
    locations, fall back to the full India-wide pipeline (OSRM real road
    geometry + the multi-hazard disaster-risk engine) so the assistant can
    answer requests like "safest route from Chennai to Kolkata" with real,
    backend-calculated numbers rather than refusing or inventing them.
    """
    if origin in NODES and destination in NODES:
        return _plan_route_ner_prototype(
            origin, destination, vehicle_type, weight_tonnes, cargo,
            season_monsoon, peak_hour,
        )

    # India-wide: OSRM + hazard-engine pipeline. This function is only ever
    # invoked from a synchronous request-handling context, so there is no
    # event loop already running and asyncio.run() is safe here.
    result = asyncio.run(
        routing_service.plan_route(
            origin=origin,
            destination=destination,
            vehicle_type=vehicle_type,
            weight_tonnes=weight_tonnes,
            cargo=cargo,
            season_monsoon=season_monsoon,
            peak_hour=peak_hour,
            mode=mode,
        )
    )
    if not result.get("success"):
        return {"error": result.get("error", "Routing failed")}

    routes = result.get("routes", [])
    for i, r in enumerate(routes):
        r["rank"] = i + 1
        r["recommended"] = (i == 0)

    return {
        "origin": origin,
        "destination": destination,
        "cargo": cargo,
        "vehicle_type": vehicle_type,
        "weight_tonnes": weight_tonnes,
        "routes": routes,
        "candidates": routes,
        "recommended": routes[0] if routes else None,
        "data_mode": result.get("data_mode"),
        "routing_source": result.get("routing_source"),
    }


def _plan_route_ner_prototype(
    origin: str, destination: str,
    vehicle_type: str = "truck", weight_tonnes: float = 2.0,
    cargo: str = "General",
    season_monsoon: bool = False,
    peak_hour: bool = False,
) -> Dict[str, Any]:
    """Plan a route using the NER-only in-memory optimizer graph."""
    candidates = optimizer.rank_routes(
        origin, destination,
        vehicle_type=vehicle_type,
        weight_tonnes=weight_tonnes,
        season_monsoon=season_monsoon,
        peak_hour=peak_hour,
    )

    if not candidates:
        return {"error": "No route found. Some roads may be closed."}

    routes = []
    for i, c in enumerate(candidates[:3]):
        d = c.to_dict()
        d["rank"] = i + 1
        d["recommended"] = (i == 0)
        routes.append(d)

    return {
        "origin": origin,
        "destination": destination,
        "cargo": cargo,
        "vehicle_type": vehicle_type,
        "weight_tonnes": weight_tonnes,
        "routes": routes,
        "candidates": routes,
        "recommended": routes[0],
    }


def get_weather_tool(location: str = "") -> Dict[str, Any]:
    """Get weather for a location."""
    if location and location in NODES:
        return get_current_weather(location)

    # Return weather for all major locations
    results = {}
    for city in list(NODES.keys())[:5]:
        results[city] = get_current_weather(city)

    return {"locations": results, "data_mode": "prototype"}


get_weather = get_weather_tool


def get_incidents(location: str = "") -> Dict[str, Any]:
    """Get active incidents."""
    incidents = []
    for inc in PROTOTYPE_INCIDENTS:
        if location and location.lower() not in inc.road_name.lower():
            continue
        incidents.append({
            "id": inc.incident_id,
            "type": inc.type,
            "severity": inc.severity,
            "road": inc.road_name,
            "message": inc.message,
            "lat": inc.lat,
            "lon": inc.lon,
        })

    return {
        "incidents": incidents,
        "total": len(incidents),
        "data_mode": "prototype",
    }


def get_accessibility(road_id: str = "") -> Dict[str, Any]:
    """Get accessibility scores."""
    from .. import accessibility as acc_mod

    if road_id:
        try:
            road = road_by_id(road_id)
            breakdown = acc_mod.score_road(road)
            return {
                "road_id": road_id,
                "road_name": f"{road.a}–{road.b}",
                "accessibility_score": breakdown.total,
                "road_condition": breakdown.road_condition,
                "weather": breakdown.weather,
                "traffic": breakdown.traffic,
                "transport": breakdown.transport,
                "connectivity": breakdown.connectivity,
                "reliability": breakdown.reliability,
            }
        except KeyError:
            return {"error": f"Unknown road: {road_id}"}

    # Return all roads
    scores = []
    for road in ROADS:
        if road.status == "CLOSED":
            continue
        breakdown = acc_mod.score_road(road)
        scores.append({
            "road_id": road.road_id,
            "road_name": f"{road.a}–{road.b}",
            "score": breakdown.total,
            "status": road.status,
        })

    return {"roads": scores, "data_mode": "prototype"}


def calculate_logistics(
    origin: str, destination: str,
    weight_tonnes: float = 2.0, vehicle_type: str = "truck"
) -> Dict[str, Any]:
    """Calculate logistics cost."""
    result = plan_route(origin, destination, vehicle_type, weight_tonnes)
    if "error" in result:
        return result

    rec = result["recommended"]
    return {
        "origin": origin,
        "destination": destination,
        "distance_km": rec["total_distance_km"],
        "eta_hours": rec["eta_hours"],
        "estimated_cost_inr": rec["estimated_cost_inr"],
        "risk_level": rec["risk_level"],
        "vehicle_type": vehicle_type,
        "weight_tonnes": weight_tonnes,
    }


def simulate_closure(road_id: str) -> Dict[str, Any]:
    """Simulate a road closure."""
    try:
        road_by_id(road_id)
    except KeyError:
        return {"error": f"Unknown road: {road_id}. Available roads: {', '.join(r.road_id for r in ROADS)}"}

    result = digital_twin.simulate_disruption(road_id, reason="SIMULATED_CLOSURE")
    return result


# Tool dispatch
TOOLS = {
    "plan_route": plan_route,
    "get_weather": get_weather_tool,
    "get_incidents": get_incidents,
    "get_accessibility": get_accessibility,
    "calculate_logistics": calculate_logistics,
    "simulate_closure": simulate_closure,
}


def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool by name with parameters."""
    if tool_name not in TOOLS:
        return {"error": f"Unknown tool: {tool_name}"}
    try:
        return TOOLS[tool_name](**parameters)
    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}"}
