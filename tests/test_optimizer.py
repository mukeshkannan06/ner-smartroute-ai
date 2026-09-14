import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend import optimizer, digital_twin
from backend.graph_data import road_by_id


def teardown_function(_):
    # reset any road closures between tests
    for r in optimizer.ROADS if hasattr(optimizer, "ROADS") else []:
        pass
    from backend.graph_data import ROADS
    for r in ROADS:
        r.status = "OPEN"


def test_finds_multiple_alternate_routes():
    candidates = optimizer.rank_routes("Guwahati", "Imphal")
    assert len(candidates) >= 3, "should find several genuinely different paths"
    paths = {tuple(c.path_nodes) for c in candidates}
    assert len(paths) == len(candidates), "candidate paths should be distinct"


def test_higher_score_beats_lower_score():
    candidates = optimizer.rank_routes("Guwahati", "Imphal")
    scores = [c.overall_score for c in candidates]
    assert scores == sorted(scores, reverse=True), "candidates must be ranked best-first"


def test_closed_road_is_excluded_from_routing():
    road_by_id("NH-003").status = "CLOSED"
    try:
        candidates = optimizer.rank_routes("Guwahati", "Imphal")
        for c in candidates:
            assert "NH-003" not in c.to_dict()["roads"], "closed road must never appear in a route"
    finally:
        road_by_id("NH-003").status = "OPEN"


def test_no_path_when_network_disconnected():
    candidates = optimizer.rank_routes("Atlantis", "Imphal")
    assert candidates == []
