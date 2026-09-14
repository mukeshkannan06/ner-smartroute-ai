import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend import risk_model
from backend.graph_data import road_by_id


def test_risk_probability_in_valid_range():
    for road_id in ["NH-001", "NH-002", "SH-011"]:
        result = risk_model.predict_risk(road_by_id(road_id))
        assert 0.0 <= result["risk_probability"] <= 1.0
        assert result["risk_level"] in {"LOW", "MODERATE", "HIGH"}


def test_closed_road_is_maximum_risk():
    road = road_by_id("NH-001")
    road.status = "CLOSED"
    try:
        result = risk_model.predict_risk(road)
        assert result["risk_probability"] == 1.0
        assert result["risk_level"] == "CLOSED"
    finally:
        road.status = "OPEN"


def test_monsoon_season_does_not_decrease_risk():
    road = road_by_id("NH-001")
    normal = risk_model.predict_risk(road, season_monsoon=False)["risk_probability"]
    monsoon = risk_model.predict_risk(road, season_monsoon=True)["risk_probability"]
    # season_monsoon was a strong positive weight in training data
    assert monsoon >= normal - 1e-6
