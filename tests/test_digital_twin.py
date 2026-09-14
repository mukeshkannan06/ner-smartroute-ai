import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend import digital_twin
from backend.graph_data import road_by_id


def setup_function(_):
    digital_twin.clear_shipments()
    for r in [road_by_id(x) for x in ["NH-001", "NH-002", "NH-003", "SH-004", "SH-005"]]:
        r.status = "OPEN"


def test_disruption_closes_the_road():
    result = digital_twin.simulate_disruption("NH-003", reason="LANDSLIDE")
    assert road_by_id("NH-003").status == "CLOSED"
    assert result["new_status"] == "CLOSED"
    digital_twin.reopen_road("NH-003")


def test_affected_shipment_gets_a_reroute():
    digital_twin.register_shipment(digital_twin.Shipment(
        shipment_id="TEST-1", origin="Guwahati", destination="Imphal",
        cargo="Vegetables", weight_tonnes=2.0, vehicle_type="truck",
    ))
    result = digital_twin.simulate_disruption("NH-003", reason="LANDSLIDE")
    try:
        assert len(result["affected_shipments"]) == 1
        affected = result["affected_shipments"][0]
        assert affected["reroute_possible"] is True
        assert "NH-003" not in affected["alternative_route"]["roads"]
    finally:
        digital_twin.reopen_road("NH-003")


def test_no_shipments_means_no_affected_list():
    result = digital_twin.simulate_disruption("SH-011", reason="FLOOD")
    try:
        assert result["affected_shipments"] == []
        assert result["priority"] in {"LOW", "MEDIUM", "HIGH"}
    finally:
        digital_twin.reopen_road("SH-011")
