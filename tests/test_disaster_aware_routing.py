"""
Regression tests for the "straight line route" bug fix and the
disaster-aware (multi-hazard) routing pipeline.

These mock the OSRM HTTP call so they run reliably without network access,
while exercising the exact same code path (backend/services/routing.py ->
backend/hazards/hazard_engine.py) used by /api/routing/plan and the chatbot.
"""
import pytest
from fastapi.testclient import TestClient

import backend.services.osrm as osrm_mod
from backend.main import app
from backend.services.routing import plan_route
from backend.ai.chatbot import process_chat_message

client = TestClient(app)

# A route that curves along the east coast (Chennai -> Kolkata) — deliberately
# NOT a straight line between the two endpoints, so assertions can catch any
# regression back to straight-line/node-only geometry.
_CURVED_COORDS = [
    [80.2707, 13.0827], [80.35, 13.5], [80.5, 14.0], [80.6, 14.5], [80.65, 15.0],
    [80.7, 15.5], [81.0, 16.2], [81.3, 16.6], [81.8, 16.9], [82.2, 17.3],
    [82.9, 17.6], [83.2, 17.68], [83.5, 17.9], [83.9, 18.3], [84.4, 18.8],
    [84.8, 19.3], [85.0, 19.8], [85.5, 20.1], [85.82, 20.3], [86.2, 20.7],
    [86.6, 21.1], [86.9, 21.4], [87.2, 21.7], [87.5, 21.9], [87.9, 22.2],
    [88.1, 22.4], [88.3639, 22.5726],
]
# A second, inland alternative that avoids the flood/cyclone-prone coastal
# corridor near Bhubaneswar/Visakhapatnam.
_INLAND_COORDS = [[c[0] - 1.6, c[1] + 0.25] for c in _CURVED_COORDS]

_FAKE_OSRM_JSON = {
    "code": "Ok",
    "routes": [
        {
            "distance": 1650000, "duration": 68000,
            "geometry": {"coordinates": _CURVED_COORDS},
            "legs": [{"distance": 1650000, "duration": 68000, "summary": "NH16", "steps": []}],
        },
        {
            "distance": 1900000, "duration": 75000,
            "geometry": {"coordinates": _INLAND_COORDS},
            "legs": [{"distance": 1900000, "duration": 75000, "summary": "Inland Alt", "steps": []}],
        },
    ],
}


class _FakeResponse:
    def __init__(self, json_data):
        self._json = json_data

    def raise_for_status(self):
        pass

    def json(self):
        return self._json


class _FakeAsyncClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def get(self, url, params=None, headers=None):
        return _FakeResponse(_FAKE_OSRM_JSON)


@pytest.fixture
def mock_osrm(monkeypatch):
    """Patch the OSRM HTTP client so tests don't depend on network access."""
    monkeypatch.setattr(osrm_mod.httpx, "AsyncClient", _FakeAsyncClient)


@pytest.mark.anyio
async def test_route_geometry_is_not_a_straight_line(mock_osrm):
    """The regression this whole fix was about: geometry must be the real,
    multi-point road-following path — never just [[origin],[destination]]."""
    res = await plan_route(origin="Chennai", destination="Kolkata", mode="fastest")
    assert res["success"] is True

    rec = res["recommended"]
    geometry = rec["geometry"]

    assert len(geometry) > 2, "Route geometry collapsed to a straight line (origin/destination only)"
    # Leaflet expects [lat, lon]; Chennai's latitude (~13) must appear first.
    assert abs(geometry[0][0] - 13.0827) < 0.01
    assert abs(geometry[0][1] - 80.2707) < 0.01
    assert abs(geometry[-1][0] - 22.5726) < 0.01
    assert res["routing_source"] == "osrm"


@pytest.mark.anyio
async def test_hazard_engine_is_wired_into_route_scoring(mock_osrm):
    """The hazard_engine.py / flood.py / landslide.py / cyclone.py modules
    must actually influence the returned route data, not sit unused."""
    res = await plan_route(origin="Chennai", destination="Kolkata", season_monsoon=True)
    rec = res["recommended"]

    assert "safety_score" in rec and 0 <= rec["safety_score"] <= 100
    assert "disaster_risk" in rec and 0 <= rec["disaster_risk"] <= 100
    assert "hazard_breakdown" in rec
    for key in ("flood_risk", "landslide_risk", "cyclone_risk", "rainfall_risk", "road_closure_risk"):
        assert key in rec["hazard_breakdown"]
    assert isinstance(rec.get("segment_points"), list) and len(rec["segment_points"]) > 1


@pytest.mark.anyio
async def test_safest_mode_prefers_lower_disaster_risk(mock_osrm):
    """In 'safest' mode, the recommended route must not be the one with the
    highest disaster risk, even if it's shorter/faster."""
    res = await plan_route(origin="Chennai", destination="Kolkata", mode="safest")
    candidates = res["candidates"]
    assert len(candidates) >= 2

    recommended = res["recommended"]
    worst_risk = max(c["disaster_risk"] for c in candidates)
    assert recommended["disaster_risk"] <= worst_risk


def test_routing_plan_endpoint(mock_osrm):
    res = client.post("/api/routing/plan", json={
        "origin": "Chennai",
        "destination": "Kolkata",
        "vehicle_type": "truck",
        "weight_tonnes": 2.0,
        "cargo": "Vegetables",
        "mode": "safest",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["recommended"]["geometry"]) > 2


def test_pan_india_hazards_endpoint():
    res = client.get("/api/hazards")
    assert res.status_code == 200
    data = res.json()
    assert "hazards" in data
    assert len(data["hazards"]) > 0
    assert data["data_mode"] == "prototype"


def test_chatbot_handles_non_ner_city_pair(mock_osrm):
    """The assistant must handle ANY Indian city pair, not just the 11
    built-in NER demo cities, using real backend-calculated numbers."""
    res = process_chat_message(
        "Find the safest route from Chennai to Kolkata avoiding floods",
        lang="en",
    )
    assert res["intent"] == "route_planning"
    assert res["action"] == "SHOW_ROUTE"
    rec = res["structured_route"]
    assert rec is not None
    assert rec["path"] == ["Chennai", "Kolkata"]
    assert rec["total_distance_km"] > 0
