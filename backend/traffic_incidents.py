"""
Traffic + Incident feed. Same seeded-synthetic pattern as weather.py so the
rest of the system (risk model, accessibility, optimizer) has something real
to consume; swap `get_traffic` / `list_incidents` for live feeds later.
"""
import hashlib
import random
from dataclasses import dataclass
from typing import List


def _seeded_random(key: str) -> random.Random:
    seed = int(hashlib.sha256(key.encode()).hexdigest(), 16) % (2**32)
    return random.Random(seed)


@dataclass
class Incident:
    incident_id: str
    road_id: str
    type: str  # LANDSLIDE / ROAD_CLOSURE / FLOOD / TRAFFIC_JAM / BRIDGE_CLOSURE / VEHICLE_RESTRICTION
    severity: int  # 1-10
    description: str


_ACTIVE_INCIDENTS: List[Incident] = []


def get_traffic_congestion(road_id: str) -> float:
    """0-100, higher = more congested."""
    rnd = _seeded_random(road_id + "-traffic-v1")
    return round(rnd.uniform(5, 55), 1)


def raise_incident(road_id: str, itype: str, severity: int, description: str) -> Incident:
    incident = Incident(
        incident_id=f"INC-{len(_ACTIVE_INCIDENTS) + 1:03d}",
        road_id=road_id,
        type=itype,
        severity=severity,
        description=description,
    )
    _ACTIVE_INCIDENTS.append(incident)
    return incident


def clear_incidents() -> None:
    _ACTIVE_INCIDENTS.clear()


def list_incidents(road_id: str = None) -> List[Incident]:
    if road_id is None:
        return list(_ACTIVE_INCIDENTS)
    return [i for i in _ACTIVE_INCIDENTS if i.road_id == road_id]


def incident_risk_contribution(road_id: str) -> float:
    """0-100 additional risk from any active incident on this road."""
    incidents = list_incidents(road_id)
    if not incidents:
        return 0.0
    return round(min(sum(i.severity for i in incidents) * 8, 100), 1)
