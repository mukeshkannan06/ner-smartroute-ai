"""
NER SmartRoute AI — Road Network Data
--------------------------------------
This is a simplified but structurally realistic representation of the NER
(North Eastern Region) inter-city highway network. Coordinates are
approximate real-world lat/lon for each town so the map/GIS layer is
geographically meaningful. Road attributes (distance, surface, max_weight,
terrain, base_condition) are illustrative placeholders you would replace
with actual OSM / PWD data in a production build — but the GRAPH STRUCTURE
(multiple real alternate paths between cities) is real, which is what lets
the optimizer make genuine trade-offs instead of picking a hardcoded route.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Nodes: towns/cities in the network
# ---------------------------------------------------------------------------

NODES: Dict[str, Dict] = {
    "Guwahati":  {"lat": 26.1445, "lon": 91.7362, "population": 963000, "hospitals": 12},
    "Shillong":  {"lat": 25.5788, "lon": 91.8933, "population": 354000, "hospitals": 5},
    "Silchar":   {"lat": 24.8333, "lon": 92.7789, "population": 229000, "hospitals": 4},
    "Dimapur":   {"lat": 25.9091, "lon": 93.7267, "population": 379000, "hospitals": 6},
    "Kohima":    {"lat": 25.6751, "lon": 94.1086, "population": 115000, "hospitals": 3},
    "Imphal":    {"lat": 24.8170, "lon": 93.9368, "population": 268000, "hospitals": 7},
    "Jorhat":    {"lat": 26.7509, "lon": 94.2037, "population": 154000, "hospitals": 4},
    "Aizawl":    {"lat": 23.7271, "lon": 92.7176, "population": 293000, "hospitals": 5},
    "Tezpur":    {"lat": 26.6338, "lon": 92.7837, "population": 102000, "hospitals": 3},
    "Nagaon":    {"lat": 26.3506, "lon": 92.6840, "population": 147000, "hospitals": 3},
    "Agartala":  {"lat": 23.8315, "lon": 91.2868, "population": 400000, "hospitals": 6},
}

# ---------------------------------------------------------------------------
# Edges: named highway/state-highway segments between two nodes.
# road_type: NH (National Highway) / SH (State Highway)
# terrain:   plain / hilly
# base_condition: 0-100 road-surface quality baseline (before weather/traffic)
# ---------------------------------------------------------------------------

@dataclass
class RoadSegment:
    road_id: str
    a: str
    b: str
    distance_km: float
    road_type: str
    surface: str
    max_weight_tonnes: float
    terrain: str
    base_condition: int  # 0-100, higher = better road quality
    lanes: int = 2
    status: str = "OPEN"  # OPEN / CLOSED (mutated by the disruption engine)


ROADS: List[RoadSegment] = [
    RoadSegment("NH-001", "Guwahati", "Silchar", 300, "NH", "paved", 20, "hilly", 82),
    RoadSegment("NH-002", "Silchar", "Imphal", 220, "NH", "paved", 18, "hilly", 74),
    RoadSegment("NH-003", "Guwahati", "Dimapur", 280, "NH", "paved", 20, "plain", 88),
    RoadSegment("SH-004", "Dimapur", "Kohima", 80, "SH", "paved", 15, "hilly", 78),
    RoadSegment("SH-005", "Kohima", "Imphal", 140, "SH", "paved", 15, "hilly", 68),
    RoadSegment("NH-006", "Guwahati", "Shillong", 100, "NH", "paved", 18, "hilly", 87),
    RoadSegment("SH-007", "Shillong", "Silchar", 220, "SH", "paved", 15, "hilly", 63),
    RoadSegment("NH-008", "Guwahati", "Jorhat", 300, "NH", "paved", 20, "plain", 85),
    RoadSegment("SH-009", "Jorhat", "Dimapur", 150, "SH", "paved", 15, "plain", 76),
    RoadSegment("SH-010", "Silchar", "Aizawl", 180, "SH", "paved", 14, "hilly", 66),
    RoadSegment("SH-011", "Aizawl", "Imphal", 260, "SH", "unpaved", 10, "hilly", 45),
    # New roads connecting Tezpur, Nagaon, Agartala
    RoadSegment("NH-012", "Guwahati", "Tezpur", 180, "NH", "paved", 20, "plain", 84),
    RoadSegment("NH-013", "Guwahati", "Nagaon", 120, "NH", "paved", 20, "plain", 86),
    RoadSegment("SH-014", "Nagaon", "Dimapur", 200, "SH", "paved", 16, "hilly", 72),
    RoadSegment("SH-015", "Tezpur", "Nagaon", 70, "SH", "paved", 16, "plain", 80),
    RoadSegment("NH-016", "Silchar", "Agartala", 330, "NH", "paved", 18, "hilly", 70),
    RoadSegment("SH-017", "Aizawl", "Agartala", 400, "SH", "paved", 12, "hilly", 55),
]

# ---------------------------------------------------------------------------
# Prototype incident data for map markers
# ---------------------------------------------------------------------------

@dataclass
class PrototypeIncident:
    incident_id: str
    lat: float
    lon: float
    type: str          # LANDSLIDE_RISK / FLOOD_RISK / HEAVY_RAIN / TRAFFIC / ROAD_CLOSURE / POOR_VISIBILITY
    severity: str      # Low / Medium / High
    road_name: str     # human-readable corridor name
    message: str

PROTOTYPE_INCIDENTS: List[PrototypeIncident] = [
    PrototypeIncident(
        "PI-001", 25.12, 92.40, "LANDSLIDE_RISK", "High",
        "Shillong–Silchar", "Landslide risk elevated on this corridor due to recent heavy rainfall and unstable terrain."
    ),
    PrototypeIncident(
        "PI-002", 25.78, 93.92, "HEAVY_RAIN", "Medium",
        "Kohima–Imphal", "Heavy rainfall expected. Visibility may drop below 2 km. Drive with caution."
    ),
    PrototypeIncident(
        "PI-003", 26.45, 92.20, "TRAFFIC", "Medium",
        "Guwahati–Nagaon", "Moderate traffic congestion near Nagaon bypass due to construction work."
    ),
    PrototypeIncident(
        "PI-004", 24.30, 92.75, "FLOOD_RISK", "High",
        "Silchar–Aizawl", "Flood risk along Barak Valley section. River levels rising near Silchar."
    ),
    PrototypeIncident(
        "PI-005", 25.90, 93.30, "POOR_VISIBILITY", "Medium",
        "Dimapur–Kohima", "Foggy conditions expected during early morning hours. Reduced visibility."
    ),
    PrototypeIncident(
        "PI-006", 26.40, 94.00, "TRAFFIC", "Low",
        "Jorhat–Dimapur", "Minor traffic delays near Jorhat toll plaza."
    ),
    PrototypeIncident(
        "PI-007", 24.82, 93.50, "LANDSLIDE_RISK", "Medium",
        "Silchar–Imphal", "Moderate landslide risk on NH-2. Terrain monitoring in progress."
    ),
    PrototypeIncident(
        "PI-008", 23.80, 91.90, "HEAVY_RAIN", "Low",
        "Agartala region", "Light to moderate rainfall in Agartala area. Roads remain passable."
    ),
]

# quick lookup helpers -------------------------------------------------------

def road_by_id(road_id: str) -> RoadSegment:
    for r in ROADS:
        if r.road_id == road_id:
            return r
    raise KeyError(f"No road with id {road_id}")


def roads_between(a: str, b: str) -> List[RoadSegment]:
    return [r for r in ROADS if {r.a, r.b} == {a, b}]


def all_node_names() -> List[str]:
    return list(NODES.keys())


def all_incidents() -> List[PrototypeIncident]:
    return list(PROTOTYPE_INCIDENTS)


def incident_by_id(incident_id: str) -> PrototypeIncident:
    for inc in PROTOTYPE_INCIDENTS:
        if inc.incident_id == incident_id:
            return inc
    raise KeyError(f"No incident with id {incident_id}")

