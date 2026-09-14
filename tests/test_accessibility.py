import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend import accessibility
from backend.graph_data import road_by_id


def test_closed_road_has_zero_accessibility():
    road = road_by_id("NH-001")
    road.status = "CLOSED"
    try:
        result = accessibility.score_road(road)
        assert result.total == 0.0
    finally:
        road.status = "OPEN"


def test_accessibility_is_between_0_and_100():
    for road_id in ["NH-001", "NH-002", "SH-011"]:
        result = accessibility.score_road(road_by_id(road_id))
        assert 0 <= result.total <= 100


def test_weights_sum_to_one():
    assert abs(sum(accessibility.WEIGHTS.values()) - 1.0) < 1e-9
