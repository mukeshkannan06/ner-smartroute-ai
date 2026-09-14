"""
Pydantic Schemas for NER SmartRoute AI API
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class RouteRequest(BaseModel):
    origin: str = Field(..., description="Origin city name (e.g. Guwahati)")
    destination: str = Field(..., description="Destination city name (e.g. Imphal)")
    vehicle_type: str = Field("truck", description="Vehicle type: truck, mini_truck, van, car")
    weight_tonnes: float = Field(2.0, ge=0.1, le=50.0, description="Cargo weight in metric tonnes")
    cargo: Optional[str] = Field("General Goods", description="Cargo description (e.g. Vegetables, Medicine)")
    season_monsoon: bool = Field(False, description="Whether monsoon season conditions apply")
    peak_hour: bool = Field(False, description="Whether peak traffic hour conditions apply")


class RoutePlanRequest(RouteRequest):
    use_osrm: bool = Field(True, description="Whether to query OSRM for live road geometry")
    mode: str = Field(
        "balanced",
        description="Route ranking mode: safest, fastest, balanced, lowest_cost, emergency",
    )


class ShipmentRequest(BaseModel):
    origin: str = Field(..., description="Origin city")
    destination: str = Field(..., description="Destination city")
    cargo: str = Field("General Goods", description="Cargo description")
    weight_tonnes: float = Field(2.0, description="Cargo weight in tonnes")
    vehicle_type: str = Field("truck", description="Vehicle type")


class DisruptionRequest(BaseModel):
    road_id: str = Field(..., description="Road segment ID (e.g. NH-001, SH-004)")
    reason: str = Field("LANDSLIDE", description="Disruption reason: LANDSLIDE, FLOOD, ROAD_CLOSURE, BRIDGE_CLOSURE")
    vehicle_type: str = Field("truck", description="Vehicle type")
    weight_tonnes: float = Field(2.0, description="Cargo weight in tonnes")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message or voice transcription")
    language: str = Field("en", description="Language code: en, hi, ta, as, mni, brx, kha, lus")
    session_id: Optional[str] = Field(None, description="Optional session tracking ID")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="UI context (current route, map view, etc.)")


class ChatResponse(BaseModel):
    reply: str
    intent: str
    language: str
    action: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    structured_route: Optional[Dict[str, Any]] = None
    suggestions: List[str] = Field(default_factory=list)


class IncidentResponse(BaseModel):
    incident_id: str
    lat: float
    lon: float
    type: str
    severity: str
    road_name: str
    message: str


class WeatherQueryResponse(BaseModel):
    location: str
    rainfall_mm: float
    wind_kmph: float
    visibility_km: float
    temperature_c: float
    weather_risk_score: float
    condition_description: str
    is_live: bool = False
