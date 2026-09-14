import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["service"] == "NER SmartRoute AI"


def test_get_nodes_endpoint():
    res = client.get("/api/network/nodes")
    assert res.status_code == 200
    data = res.json()
    assert "Guwahati" in data
    assert "Imphal" in data


def test_get_incidents_endpoint():
    res = client.get("/api/incidents")
    assert res.status_code == 200
    assert len(res.json()) >= 8


def test_routing_best_routes_endpoint():
    res = client.post("/api/routing/best-routes", json={
        "origin": "Guwahati",
        "destination": "Imphal",
        "vehicle_type": "truck",
        "weight_tonnes": 2.0,
        "cargo": "Vegetables",
        "season_monsoon": False,
        "peak_hour": False,
    })
    assert res.status_code == 200
    data = res.json()
    assert len(data["candidates"]) > 0
    assert data["recommended"]["path"][0] == "Guwahati"
    assert data["recommended"]["path"][-1] == "Imphal"


def test_chat_endpoint_multilingual():
    res = client.post("/api/chat", json={
        "message": "Route from Guwahati to Imphal",
        "language": "en",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "route_planning"
    assert data["reply"] != ""


def test_simulate_disruption_and_reopen():
    res = client.post("/api/digital-twin/simulate-disruption", json={
        "road_id": "NH-001",
        "reason": "LANDSLIDE",
        "vehicle_type": "truck",
        "weight_tonnes": 2.0,
    })
    assert res.status_code == 200
    assert res.json()["road_closed"]["road_id"] == "NH-001"

    # Reopen
    res2 = client.post("/api/digital-twin/reopen/NH-001")
    assert res2.status_code == 200
    assert res2.json()["road"]["status"] == "OPEN"
