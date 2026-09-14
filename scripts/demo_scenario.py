"""
Runs the exact end-to-end scenario the prototype is built to demonstrate:

  1. A logistics user wants to move 2 tonnes of vegetables, Guwahati -> Imphal
  2. The system finds real alternate routes and recommends the best one
  3. A sudden road closure hits the recommended route's first leg
  4. The Digital Mobility Twin computes the impact and finds an alternative
  5. The government dashboard reflects the new network state

Run:  python scripts/demo_scenario.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend import optimizer, digital_twin, risk_model, eta_model
from backend.graph_data import road_by_id


def line(title=""):
    print("\n" + "=" * 78)
    if title:
        print(title)
        print("=" * 78)


def show_route(route_dict, label):
    print(f"\n{label}")
    print(f"  Path:          {' -> '.join(route_dict['path'])}")
    print(f"  Roads used:    {', '.join(route_dict['roads'])}")
    print(f"  Distance:      {route_dict['total_distance_km']} km")
    print(f"  ETA:           {route_dict['eta_hours']} hours")
    print(f"  Risk:          {route_dict['risk_probability']*100:.1f}%  ({route_dict['risk_level']})")
    print(f"  Accessibility: {route_dict['accessibility_score']}/100")
    print(f"  Est. cost:     \u20b9{route_dict['estimated_cost_inr']:,.0f}")
    print(f"  Overall score: {route_dict['overall_score']}/100")


def main():
    # make sure models exist / are freshly trained for this demo run
    line("STEP 0 — Training ML models (RandomForest risk + GradientBoosting ETA)")
    risk_model.train_and_save_model()
    eta_model.train_and_save_model()

    line("STEP 1 — Smart Logistics request")
    print("User:  \"Transport 2 tonnes of vegetables from Guwahati to Imphal.\"")

    digital_twin.clear_shipments()
    shipment = digital_twin.register_shipment(digital_twin.Shipment(
        shipment_id="SHIP-001", origin="Guwahati", destination="Imphal",
        cargo="Vegetables", weight_tonnes=2.0, vehicle_type="truck",
    ))
    print(f"Registered shipment: {shipment}")

    candidates = optimizer.rank_routes("Guwahati", "Imphal", vehicle_type="truck", weight_tonnes=2.0)
    line("STEP 2 — AI evaluates every real alternate route")
    for i, c in enumerate(candidates, start=1):
        show_route(c.to_dict(), f"Candidate #{i}")

    best = candidates[0]
    line("STEP 3 — AI Recommendation")
    show_route(best.to_dict(), "RECOMMENDED ROUTE")

    disrupted_road = best.to_dict()["roads"][0]
    line(f"STEP 4 — Sudden disruption: {disrupted_road} is closed (landslide)")
    result = digital_twin.simulate_disruption(disrupted_road, reason="LANDSLIDE")
    print(f"Priority classification: {result['priority']}")
    print(f"Affected towns:          {result['affected_towns']}")
    print(f"Shipments affected:      {len(result['affected_shipments'])}")
    print(f"Shipments rerouted:      {result['shipments_with_reroute']}")
    print(f"Shipments stranded:      {result['shipments_stranded']}")

    for affected in result["affected_shipments"]:
        show_route(affected["baseline_route"], f"  Was using (shipment {affected['shipment_id']})")
        show_route(affected["alternative_route"], f"  New recommended alternative")
        print(f"\n  Extra distance: {affected['extra_distance_km']} km")
        print(f"  Extra time:     {affected['extra_time_hours']} hours")
        print(f"  Accessibility change: {affected['accessibility_delta']}")

    line("STEP 5 — Government Dashboard")
    snapshot = digital_twin.network_accessibility_snapshot()
    print(json.dumps(snapshot, indent=2))
    print(f"\nRecommendation to authorities:\n  \"{result['recommendation']}\"")

    digital_twin.reopen_road(disrupted_road)
    line("Road reopened — demo complete.")


if __name__ == "__main__":
    main()
