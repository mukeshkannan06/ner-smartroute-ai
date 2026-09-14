"""
Accessibility Score
--------------------
Accessibility = weighted blend of:
    road condition, weather, traffic, transport availability,
    connectivity, reliability

Weights are DOCUMENTED here (not claimed to be scientifically derived —
see README for how you'd calibrate them against real incident/delay data).
"""
from dataclasses import dataclass

from . import weather as weather_mod
from . import traffic_incidents as ti_mod
from .graph_data import RoadSegment

# Documented, adjustable weights (must sum to 1.0)
WEIGHTS = {
    "road_condition": 0.30,
    "weather": 0.20,
    "traffic": 0.15,
    "transport": 0.10,
    "connectivity": 0.10,
    "reliability": 0.15,
}


@dataclass
class AccessibilityBreakdown:
    road_condition: float
    weather: float
    traffic: float
    transport: float
    connectivity: float
    reliability: float
    total: float


def _transport_availability(road: RoadSegment) -> float:
    """Higher lane count + NH classification = more transport options."""
    base = 60 if road.road_type == "SH" else 80
    base += (road.lanes - 2) * 10
    if road.surface == "unpaved":
        base -= 20
    return max(0, min(100, base))


def _connectivity(road: RoadSegment) -> float:
    """Proxy: max_weight capacity + surface quality as a stand-in for how
    well this segment connects into the wider freight network."""
    weight_score = min(road.max_weight_tonnes / 20 * 100, 100)
    surface_score = 100 if road.surface == "paved" else 40
    return round(weight_score * 0.5 + surface_score * 0.5, 1)


def _reliability(road: RoadSegment) -> float:
    """Penalize hilly terrain and active incidents (more prone to sudden
    disruption)."""
    base = 90 if road.terrain == "plain" else 70
    base -= ti_mod.incident_risk_contribution(road.road_id) * 0.3
    return max(0, round(base, 1))


def score_road(road: RoadSegment) -> AccessibilityBreakdown:
    if road.status == "CLOSED":
        return AccessibilityBreakdown(0, 0, 0, 0, 0, 0, 0.0)

    w = weather_mod.get_weather(road.road_id)
    road_condition = road.base_condition
    weather_score = weather_mod.weather_accessibility_component(w)
    traffic_score = round(100 - ti_mod.get_traffic_congestion(road.road_id), 1)
    transport_score = _transport_availability(road)
    connectivity_score = _connectivity(road)
    reliability_score = _reliability(road)

    total = (
        road_condition * WEIGHTS["road_condition"]
        + weather_score * WEIGHTS["weather"]
        + traffic_score * WEIGHTS["traffic"]
        + transport_score * WEIGHTS["transport"]
        + connectivity_score * WEIGHTS["connectivity"]
        + reliability_score * WEIGHTS["reliability"]
    )

    return AccessibilityBreakdown(
        road_condition=road_condition,
        weather=weather_score,
        traffic=traffic_score,
        transport=transport_score,
        connectivity=connectivity_score,
        reliability=reliability_score,
        total=round(total, 1),
    )
