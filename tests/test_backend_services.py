import pytest
import asyncio
from backend.services.geocoding import geocode, KNOWN_LOCATIONS
from backend.services.weather_service import get_current_weather, get_route_weather
from backend.services.routing import plan_route
from backend.graph_data import NODES, ROADS


@pytest.mark.anyio
async def test_known_geocoding_lookup():
    res = await geocode("Guwahati")
    assert res is not None
    assert len(res) > 0
    assert res[0].name == "Guwahati"
    assert abs(res[0].lat - 26.1445) < 0.01


@pytest.mark.anyio
async def test_weather_service_current():
    w = get_current_weather("Guwahati")
    assert w["location"] == "Guwahati"
    assert w["temperature_c"] > 0
    assert 0 <= w["weather_risk_score"] <= 100.0



@pytest.mark.anyio
async def test_unified_route_planning_success():
    res = await plan_route(
        origin="Guwahati",
        destination="Imphal",
        vehicle_type="truck",
        weight_tonnes=2.0,
        cargo="Vegetables",
    )
    assert res["success"] is True
    assert "candidates" in res
    assert len(res["candidates"]) > 0
    rec = res["recommended"]
    assert rec["total_distance_km"] > 0
    assert rec["eta_hours"] > 0
    assert 0 <= rec["risk_probability"] <= 1.0
