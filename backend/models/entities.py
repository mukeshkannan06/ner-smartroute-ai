"""
Domain models and database entity stubs for NER SmartRoute AI.
These stubs represent the database persistence layer (PostgreSQL / PostGIS / SQLite).
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class ShipmentEntity:
    shipment_id: str
    origin: str
    destination: str
    cargo: str
    weight_tonnes: float
    vehicle_type: str
    status: str = "IN_TRANSIT"  # PENDING, IN_TRANSIT, DELIVERED, REROUTED
    assigned_route_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IncidentEntity:
    incident_id: str
    road_id: str
    incident_type: str  # LANDSLIDE, FLOOD, ROAD_CLOSURE, HEAVY_RAIN
    severity: str       # Low, Medium, High, Critical
    lat: float
    lon: float
    description: str
    is_active: bool = True
    reported_at: datetime = field(default_factory=datetime.utcnow)
    cleared_at: Optional[datetime] = None


@dataclass
class CorridorHealthRecord:
    road_id: str
    accessibility_score: float
    risk_level: str
    average_speed_kmph: float
    recorded_at: datetime = field(default_factory=datetime.utcnow)


# In-memory persistence stores
_SHIPMENT_STORE: Dict[str, ShipmentEntity] = {}
_INCIDENT_STORE: Dict[str, IncidentEntity] = {}


def save_shipment(shipment: ShipmentEntity) -> ShipmentEntity:
    _SHIPMENT_STORE[shipment.shipment_id] = shipment
    return shipment


def get_shipment(shipment_id: str) -> Optional[ShipmentEntity]:
    return _SHIPMENT_STORE.get(shipment_id)


def list_shipments() -> List[ShipmentEntity]:
    return list(_SHIPMENT_STORE.values())


def save_incident(incident: IncidentEntity) -> IncidentEntity:
    _INCIDENT_STORE[incident.incident_id] = incident
    return incident


def list_active_incidents() -> List[IncidentEntity]:
    return [inc for inc in _INCIDENT_STORE.values() if inc.is_active]
