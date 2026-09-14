"""
Route Optimizer
-----------------
Builds a real graph (networkx) from graph_data.ROADS, finds multiple
candidate paths between origin and destination (k-shortest simple paths,
by distance), scores each candidate on ETA / risk / cost / accessibility,
and returns a ranked list. Nothing here is a hardcoded "Route A = 91".
"""
import itertools
from dataclasses import dataclass, field
from typing import List, Optional

import networkx as nx

from . import risk_model, eta_model, accessibility
from .graph_data import ROADS, RoadSegment, roads_between

# Overall-score weights (documented, adjustable — see docs/architecture.md)
SCORE_WEIGHTS = {
    "accessibility": 0.35,   # higher accessibility -> higher score
    "risk": 0.35,            # lower risk -> higher score
    "eta": 0.20,             # lower ETA -> higher score
    "cost": 0.10,            # lower cost -> higher score
}

COST_PER_KM = {"truck": 32, "mini_truck": 24, "van": 20, "car": 14}  # INR/km, illustrative


def build_graph() -> nx.Graph:
    """Simple graph for pathfinding (shortest_simple_paths needs a simple
    graph, not a MultiGraph). Where two roads connect the same pair of
    towns, keep the shorter distance as the edge weight for path search —
    _pick_best_road() below does the real road-quality tie-break once a
    path is chosen."""
    g = nx.Graph()
    for r in ROADS:
        if r.status == "CLOSED":
            continue
        if g.has_edge(r.a, r.b):
            if r.distance_km < g[r.a][r.b]["weight"]:
                g[r.a][r.b]["weight"] = r.distance_km
        else:
            g.add_edge(r.a, r.b, weight=r.distance_km)
    return g


@dataclass
class RouteLeg:
    road: RoadSegment
    risk: dict
    eta_hours: float
    accessibility: accessibility.AccessibilityBreakdown


@dataclass
class RouteCandidate:
    path_nodes: List[str]
    legs: List[RouteLeg]
    total_distance_km: float = field(init=False)
    total_eta_hours: float = field(init=False)
    avg_risk_probability: float = field(init=False)
    avg_accessibility: float = field(init=False)
    estimated_cost_inr: float = field(init=False)
    overall_score: float = field(init=False)
    risk_level: str = field(init=False)

    def compute(self, vehicle_type: str, weight_tonnes: float):
        self.total_distance_km = round(sum(leg.road.distance_km for leg in self.legs), 1)
        self.total_eta_hours = round(sum(leg.eta_hours for leg in self.legs), 2)
        self.avg_risk_probability = round(
            sum(leg.risk["risk_probability"] for leg in self.legs) / len(self.legs), 3
        )
        self.avg_accessibility = round(
            sum(leg.accessibility.total for leg in self.legs) / len(self.legs), 1
        )
        base_cost = self.total_distance_km * COST_PER_KM.get(vehicle_type, 30)
        weight_surcharge = max(0, weight_tonnes - 5) * 150  # INR per extra tonne
        self.estimated_cost_inr = round(base_cost + weight_surcharge, 0)

        if self.avg_risk_probability >= 0.66:
            self.risk_level = "HIGH"
        elif self.avg_risk_probability >= 0.35:
            self.risk_level = "MODERATE"
        else:
            self.risk_level = "LOW"

    def to_dict(self):
        return {
            "path": self.path_nodes,
            "roads": [leg.road.road_id for leg in self.legs],
            "total_distance_km": self.total_distance_km,
            "eta_hours": self.total_eta_hours,
            "risk_probability": self.avg_risk_probability,
            "risk_level": self.risk_level,
            "accessibility_score": self.avg_accessibility,
            "estimated_cost_inr": self.estimated_cost_inr,
            "overall_score": self.overall_score,
        }


def _pick_best_road(a: str, b: str) -> Optional[RoadSegment]:
    """If multiple parallel roads connect the same two towns, pick the open
    one with the best base condition (a real, explainable tie-break rule)."""
    candidates = [r for r in roads_between(a, b) if r.status == "OPEN"]
    if not candidates:
        return None
    return max(candidates, key=lambda r: r.base_condition)


def find_candidate_routes(origin: str, destination: str, k: int = 4) -> List[List[str]]:
    g = build_graph()
    if origin not in g or destination not in g:
        return []
    try:
        paths_gen = nx.shortest_simple_paths(g, origin, destination, weight="weight")
    except nx.NetworkXNoPath:
        return []
    paths = list(itertools.islice(paths_gen, k))
    return paths


def score_route(path_nodes: List[str], vehicle_type: str, weight_tonnes: float,
                 season_monsoon: bool = False, peak_hour: bool = False) -> Optional[RouteCandidate]:
    legs = []
    for a, b in zip(path_nodes, path_nodes[1:]):
        road = _pick_best_road(a, b)
        if road is None:
            return None
        risk = risk_model.predict_risk(road, season_monsoon=season_monsoon)
        eta = eta_model.predict_eta_hours(road, vehicle_type=vehicle_type, peak_hour=peak_hour)
        acc = accessibility.score_road(road)
        legs.append(RouteLeg(road=road, risk=risk, eta_hours=eta, accessibility=acc))

    candidate = RouteCandidate(path_nodes=path_nodes, legs=legs)
    candidate.compute(vehicle_type=vehicle_type, weight_tonnes=weight_tonnes)
    return candidate


def _normalize(values: List[float], invert: bool = False) -> List[float]:
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi == lo:
        return [1.0 for _ in values]
    norm = [(v - lo) / (hi - lo) for v in values]
    return [1 - n for n in norm] if invert else norm


def rank_routes(origin: str, destination: str, vehicle_type: str = "truck",
                 weight_tonnes: float = 2.0, season_monsoon: bool = False,
                 peak_hour: bool = False, k: int = 4) -> List[RouteCandidate]:
    paths = find_candidate_routes(origin, destination, k=k)
    candidates = []
    for p in paths:
        c = score_route(p, vehicle_type, weight_tonnes, season_monsoon, peak_hour)
        if c:
            candidates.append(c)
    if not candidates:
        return []

    acc_norm = _normalize([c.avg_accessibility for c in candidates])
    risk_norm = _normalize([c.avg_risk_probability for c in candidates], invert=True)
    eta_norm = _normalize([c.total_eta_hours for c in candidates], invert=True)
    cost_norm = _normalize([c.estimated_cost_inr for c in candidates], invert=True)

    for c, a, r, e, co in zip(candidates, acc_norm, risk_norm, eta_norm, cost_norm):
        c.overall_score = round(
            100 * (
                a * SCORE_WEIGHTS["accessibility"]
                + r * SCORE_WEIGHTS["risk"]
                + e * SCORE_WEIGHTS["eta"]
                + co * SCORE_WEIGHTS["cost"]
            ), 1
        )

    candidates.sort(key=lambda c: c.overall_score, reverse=True)
    return candidates
