"""
Digital Mobility Twin
------------------------
Models the NER road network as a live graph. When a disruption is injected
(road closure, flood, landslide...), this module:
  1. Marks the affected road CLOSED
  2. Finds every active shipment/route that used that road
  3. Recomputes the best alternative route for each
  4. Reports accessibility delta, extra distance/time, and a recommendation

This is what lets the system answer: "What happens if this corridor
becomes unavailable for 12 hours?"
"""
from dataclasses import dataclass, field
from typing import List, Optional

from . import optimizer
from . import traffic_incidents as ti_mod
from .graph_data import ROADS, road_by_id, NODES


@dataclass
class Shipment:
    shipment_id: str
    origin: str
    destination: str
    cargo: str
    weight_tonnes: float
    vehicle_type: str
    current_road_id: Optional[str] = None  # which road segment it's currently assumed to be on


_ACTIVE_SHIPMENTS: List[Shipment] = []


def register_shipment(shipment: Shipment) -> Shipment:
    _ACTIVE_SHIPMENTS.append(shipment)
    return shipment


def clear_shipments():
    _ACTIVE_SHIPMENTS.clear()


def close_road(road_id: str, reason: str = "ROAD_CLOSURE") -> dict:
    road = road_by_id(road_id)
    previous_status = road.status
    road.status = "CLOSED"
    return {"road_id": road_id, "previous_status": previous_status, "new_status": "CLOSED", "reason": reason}


def reopen_road(road_id: str) -> dict:
    road = road_by_id(road_id)
    road.status = "OPEN"
    return {"road_id": road_id, "new_status": "OPEN"}


def affected_towns(road_id: str) -> List[str]:
    road = road_by_id(road_id)
    return [road.a, road.b]


def simulate_disruption(road_id: str, reason: str = "ROAD_CLOSURE",
                         vehicle_type: str = "truck", weight_tonnes: float = 2.0) -> dict:
    """
    Full what-if simulation: close a road, find every shipment that
    depended on it, and produce alternative-route recommendations plus a
    government-facing impact summary.
    """
    road = road_by_id(road_id)
    prior_status = road.status

    # 1. Baseline: best route for each active shipment BEFORE closure
    baselines = {}
    for shipment in _ACTIVE_SHIPMENTS:
        ranked = optimizer.rank_routes(shipment.origin, shipment.destination,
                                        vehicle_type=shipment.vehicle_type,
                                        weight_tonnes=shipment.weight_tonnes)
        baselines[shipment.shipment_id] = ranked[0] if ranked else None

    # 2. Apply the disruption
    close_info = close_road(road_id, reason=reason)

    # 3. Find affected shipments: those whose *baseline best route* used this road
    affected = []
    for shipment in _ACTIVE_SHIPMENTS:
        baseline = baselines.get(shipment.shipment_id)
        used_affected_road = baseline is not None and road_id in [leg for leg in baseline.to_dict()["roads"]]
        if not used_affected_road:
            continue

        new_ranked = optimizer.rank_routes(shipment.origin, shipment.destination,
                                            vehicle_type=shipment.vehicle_type,
                                            weight_tonnes=shipment.weight_tonnes)
        new_best = new_ranked[0] if new_ranked else None

        affected.append({
            "shipment_id": shipment.shipment_id,
            "origin": shipment.origin,
            "destination": shipment.destination,
            "cargo": shipment.cargo,
            "baseline_route": baseline.to_dict() if baseline else None,
            "alternative_route": new_best.to_dict() if new_best else None,
            "extra_distance_km": (
                round(new_best.total_distance_km - baseline.total_distance_km, 1)
                if (new_best and baseline) else None
            ),
            "extra_time_hours": (
                round(new_best.total_eta_hours - baseline.total_eta_hours, 2)
                if (new_best and baseline) else None
            ),
            "accessibility_delta": (
                round(new_best.avg_accessibility - baseline.avg_accessibility, 1)
                if (new_best and baseline) else None
            ),
            "reroute_possible": new_best is not None,
        })

    # 4. Network-wide impact: which towns lose direct connectivity via this road
    towns = affected_towns(road_id)

    # 5. Priority classification for the government dashboard
    if len(affected) >= 3 or road.road_type == "NH":
        priority = "HIGH"
    elif len(affected) >= 1:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return {
        "road_id": road_id,
        "road_closed": road.__dict__,
        "reason": reason,
        "affected_towns": towns,
        "prior_status": prior_status,
        "new_status": "CLOSED",
        "affected_shipments": affected,
        "shipments_with_reroute": sum(1 for a in affected if a["reroute_possible"]),
        "shipments_stranded": sum(1 for a in affected if not a["reroute_possible"]),
        "priority": priority,
        "recommendation": (
            f"Activate alternate corridor for {towns[0]}\u2013{towns[1]} traffic. "
            f"{sum(1 for a in affected if a['reroute_possible'])}/{len(affected)} shipments "
            "can be rerouted automatically."
            if affected else
            "No active shipments currently depend on this corridor; monitor for new bookings."
        ),
    }


def network_accessibility_snapshot(vehicle_type: str = "truck") -> dict:
    """Aggregate accessibility across the whole network — powers the
    government dashboard's headline number."""
    from . import accessibility as acc_mod
    scores = []
    critical = 0
    high_risk = 0
    for road in ROADS:
        if road.status == "CLOSED":
            continue
        breakdown = acc_mod.score_road(road)
        scores.append(breakdown.total)
        from . import risk_model as rm
        risk = rm.predict_risk(road)
        if risk["risk_level"] == "HIGH":
            high_risk += 1
        if breakdown.total < 50:
            critical += 1

    avg = round(sum(scores) / len(scores), 1) if scores else 0.0
    return {
        "network_accessibility": avg,
        "critical_corridors": critical,
        "high_risk_routes": high_risk,
        "active_incidents": len(ti_mod.list_incidents()),
        "roads_closed": sum(1 for r in ROADS if r.status == "CLOSED"),
        "total_roads": len(ROADS),
    }


def reopen_road(road_id: str) -> dict:
    """Reopen a previously closed road segment in the network."""
    road = road_by_id(road_id)
    prior_status = road.status
    road.status = "OPEN"
    return {
        "road_id": road_id,
        "road": road.__dict__,
        "prior_status": prior_status,
        "new_status": "OPEN",
    }

