"""
NER SmartRoute AI — FastAPI Application
----------------------------------------
Run with:  uvicorn backend.main:app --reload --port 8000
Docs at:   http://localhost:8000/docs
"""
from typing import Optional, List, Dict, Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import optimizer, digital_twin, weather as weather_mod, risk_model, eta_model
from .graph_data import NODES, ROADS, PROTOTYPE_INCIDENTS, road_by_id, incident_by_id, all_incidents
from .schemas import (
    RouteRequest,
    RoutePlanRequest,
    ShipmentRequest,
    DisruptionRequest,
    ChatRequest,
    ChatResponse,
    IncidentResponse,
    WeatherQueryResponse,
)
from .ai.chatbot import process_chat_message
from .services.routing import plan_route
from .services.weather_service import get_current_weather
from .services.geocoding import geocode, KNOWN_LOCATIONS
from .hazards.hazard_engine import list_active_pan_india_hazards

app = FastAPI(
    title="NER SmartRoute AI",
    description="Real-time accessibility, GIS routing, digital mobility twin, and multi-lingual AI assistant for North-East India.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Network / GIS Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/network/nodes")
def get_nodes():
    """Get all NER network nodes (cities/towns) with coordinates and attributes."""
    return {name: attrs for name, attrs in NODES.items()}


@app.get("/api/network/roads")
def get_roads():
    """Get all NER road segments with current status and quality metrics."""
    return [r.__dict__ for r in ROADS]


@app.get("/api/network/accessibility-snapshot")
def accessibility_snapshot():
    """Get comprehensive network-wide accessibility snapshot."""
    return digital_twin.network_accessibility_snapshot()


# ---------------------------------------------------------------------------
# Incidents & Hazards
# ---------------------------------------------------------------------------

@app.get("/api/incidents")
def get_incidents():
    """Get all active and prototype road network incidents/hazards."""
    return [inc.__dict__ for inc in all_incidents()]


@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str):
    """Get a specific incident by ID."""
    try:
        inc = incident_by_id(incident_id)
        return inc.__dict__
    except KeyError:
        raise HTTPException(404, f"Unknown incident_id: {incident_id}")


@app.get("/api/hazards")
def get_pan_india_hazards():
    """
    Pan-India multi-hazard incidents (flood, landslide, cyclone, road closure)
    used for the map hazard layer. This is simulated/prototype data — see
    'data_mode' on route-planning responses for the live-vs-prototype flag.
    """
    return {
        "hazards": list_active_pan_india_hazards(),
        "data_mode": "prototype",
    }


# ---------------------------------------------------------------------------
# Weather & Geocoding
# ---------------------------------------------------------------------------

@app.get("/api/weather/current")
def current_weather(location: str = Query("Guwahati", description="City or corridor name")):
    """Get real/synthetic weather for a location."""
    return get_current_weather(location)


@app.get("/api/geocoding/search")
async def search_locations(q: str = Query(..., description="Location search query")):
    """Search for locations and coordinates in NER."""
    results = await geocode(q)
    if not results:
        return []
    return [
        {
            "name": r.name,
            "display_name": r.display_name,
            "lat": r.lat,
            "lon": r.lon,
            "type": r.type,
        }
        for r in results
    ]


# ---------------------------------------------------------------------------
# Routing & Logistics
# ---------------------------------------------------------------------------

@app.post("/api/routing/plan")
async def plan_unified_route(req: RoutePlanRequest):
    """
    Plan a unified SmartRoute: combines OSRM road geometry with
    multi-factor risk, accessibility, ETA, and cost scoring.
    """
    res = await plan_route(
        origin=req.origin,
        destination=req.destination,
        vehicle_type=req.vehicle_type,
        weight_tonnes=req.weight_tonnes,
        cargo=req.cargo or "General Goods",
        season_monsoon=req.season_monsoon,
        peak_hour=req.peak_hour,
        mode=req.mode,
    )
    if not res.get("success", False):
        raise HTTPException(400, res.get("error", "Routing failed"))
    return res


@app.post("/api/routing/best-routes")
def best_routes(req: RouteRequest):
    """Candidate route optimizer using the core in-memory network graph."""
    if req.origin not in NODES or req.destination not in NODES:
        raise HTTPException(400, "Unknown origin or destination town")
    candidates = optimizer.rank_routes(
        req.origin, req.destination,
        vehicle_type=req.vehicle_type, weight_tonnes=req.weight_tonnes,
        season_monsoon=req.season_monsoon, peak_hour=req.peak_hour,
    )
    if not candidates:
        raise HTTPException(404, "No route found between these towns")
    return {
        "origin": req.origin,
        "destination": req.destination,
        "cargo": req.cargo,
        "candidates": [c.to_dict() for c in candidates],
        "recommended": candidates[0].to_dict(),
    }


@app.get("/api/risk/road/{road_id}")
def road_risk(road_id: str):
    """ML Random Forest risk prediction for a road segment."""
    try:
        road = road_by_id(road_id)
    except KeyError:
        raise HTTPException(404, "Unknown road_id")
    return risk_model.predict_risk(road)


@app.get("/api/weather/road/{road_id}")
def road_weather(road_id: str):
    """Weather condition & weather risk score for a road segment."""
    try:
        road = road_by_id(road_id)
    except KeyError:
        raise HTTPException(404, "Unknown road_id")
    w = weather_mod.get_weather(road_id)
    return {
        "road_id": road_id, "rainfall_mm": w.rainfall_mm, "wind_kmph": w.wind_kmph,
        "visibility_km": w.visibility_km, "temperature_c": w.temperature_c,
        "weather_risk_score": weather_mod.weather_risk_score(w),
    }


# ---------------------------------------------------------------------------
# Shipments & Logistics Tracking
# ---------------------------------------------------------------------------

@app.post("/api/logistics/shipments")
def create_shipment(req: ShipmentRequest):
    """Register an active shipment in the Digital Mobility Twin."""
    if req.origin not in NODES or req.destination not in NODES:
        raise HTTPException(400, "Unknown origin or destination town")
    shipment = digital_twin.Shipment(
        shipment_id=f"SHIP-{uuid4().hex[:6].upper()}",
        origin=req.origin, destination=req.destination,
        cargo=req.cargo, weight_tonnes=req.weight_tonnes, vehicle_type=req.vehicle_type,
    )
    digital_twin.register_shipment(shipment)
    return shipment.__dict__


@app.get("/api/logistics/shipments")
def list_shipments():
    """List all currently tracked active shipments."""
    return [s.__dict__ for s in digital_twin._ACTIVE_SHIPMENTS]


# ---------------------------------------------------------------------------
# Digital Mobility Twin & Disruption Simulation
# ---------------------------------------------------------------------------

@app.post("/api/digital-twin/simulate-disruption")
def simulate_disruption(req: DisruptionRequest):
    """Simulate a hazard/landslide closure on a road and compute network impact."""
    try:
        road_by_id(req.road_id)
    except KeyError:
        raise HTTPException(404, "Unknown road_id")
    return digital_twin.simulate_disruption(req.road_id, reason=req.reason)


@app.post("/api/digital-twin/reopen/{road_id}")
def reopen_road(road_id: str):
    """Reopen a previously closed road segment."""
    try:
        return digital_twin.reopen_road(road_id)
    except KeyError:
        raise HTTPException(404, "Unknown road_id")


@app.post("/api/digital-twin/reopen-all")
def reopen_all():
    """Reopen all road segments in the network."""
    for road in ROADS:
        road.status = "OPEN"
    return {"status": "ALL_ROADS_OPEN", "open_count": len(ROADS)}


# ---------------------------------------------------------------------------
# Government Analytics Dashboard
# ---------------------------------------------------------------------------

@app.get("/api/government/dashboard")
def government_dashboard():
    """Aggregate government view: accessibility index, critical corridors, high-risk routes."""
    snapshot = digital_twin.network_accessibility_snapshot()
    return {
        **snapshot,
        "network_accessibility_score": snapshot.get("network_accessibility", 82.4),
        "vehicles_tracked": len(digital_twin._ACTIVE_SHIPMENTS),
        "active_incidents_count": len(PROTOTYPE_INCIDENTS),
    }


# ---------------------------------------------------------------------------
# AI Conversational Chatbot
# ---------------------------------------------------------------------------

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    """
    Multilingual conversational AI endpoint with tool dispatching,
    actionable UI payloads, and speech-ready text.
    """
    res = process_chat_message(
        message=req.message,
        lang=req.language,
        context=req.context,
    )
    return ChatResponse(**res)


# ---------------------------------------------------------------------------
# Health / Root
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "NER SmartRoute AI",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            "/api/routing/plan",
            "/api/chat",
            "/api/incidents",
            "/api/weather/current",
            "/api/government/dashboard",
            "/api/digital-twin/simulate-disruption",
        ],
    }
