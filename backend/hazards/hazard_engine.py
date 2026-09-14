"""
Unified Multi-Hazard Intelligence Engine
-----------------------------------------
Aggregates flood, landslide, cyclone, heavy rainfall, and active road hazard incidents
along any route geometry in India.
Applies non-linear critical risk escalation and outputs risk-segmented polylines.
"""
from typing import List, Dict, Any, Tuple
import math

from .flood import evaluate_flood_risk, FLOOD_ZONES
from .landslide import evaluate_landslide_risk, LANDSLIDE_PRONE_REGIONS
from .cyclone import evaluate_cyclone_risk, COASTAL_CYCLONE_CORRIDORS
from .rainfall import evaluate_rainfall_risk


# Active Simulated / Monitored Incidents across India
PAN_INDIA_INCIDENTS = [
    {
        "id": "HAZ-IN-001", "type": "FLOOD", "severity": "HIGH",
        "lat": 20.35, "lon": 85.95, "location": "Bhubaneswar–Cuttack Corridor (Odisha)",
        "message": "Heavy monsoon inflow causing waterlogging on NH-16. Right lanes submerged near Mahanadi bridge.",
        "impact_radius_km": 60, "blocked": False, "speed_reduction_pct": 50,
    },
    {
        "id": "HAZ-IN-002", "type": "LANDSLIDE", "severity": "CRITICAL",
        "lat": 30.15, "lon": 78.35, "location": "Rishikesh–Devprayag (Uttarakhand)",
        "message": "Major rockfall blocking both lanes. Emergency clearance underway by BRO.",
        "impact_radius_km": 40, "blocked": True, "speed_reduction_pct": 100,
    },
    {
        "id": "HAZ-IN-003", "type": "CYCLONE", "severity": "HIGH",
        "lat": 17.75, "lon": 83.25, "location": "Visakhapatnam Coastal Highway (Andhra Pradesh)",
        "message": "Gale winds >75 km/h and high tidal surge. Heavy transport advised to divert inland.",
        "impact_radius_km": 70, "blocked": False, "speed_reduction_pct": 40,
    },
    {
        "id": "HAZ-IN-004", "type": "LANDSLIDE", "severity": "HIGH",
        "lat": 25.18, "lon": 92.35, "location": "Shillong–Silchar NH-06 (Meghalaya)",
        "message": "Mudslide at Sonapur tunnel area. Single-lane movement regulated.",
        "impact_radius_km": 50, "blocked": False, "speed_reduction_pct": 60,
    },
    {
        "id": "HAZ-IN-005", "type": "HEAVY_RAIN", "severity": "MODERATE",
        "lat": 15.80, "lon": 73.80, "location": "Goa–Maharashtra Border Ghat Section",
        "message": "Torrential rain and dense fog. Visibility reduced to 1.5 km.",
        "impact_radius_km": 50, "blocked": False, "speed_reduction_pct": 30,
    },
    {
        "id": "HAZ-IN-006", "type": "ROAD_CLOSURE", "severity": "HIGH",
        "lat": 26.40, "lon": 92.70, "location": "Nagaon Bypass Arterial Segment (Assam)",
        "message": "Bridge maintenance work and temporary diversion in place.",
        "impact_radius_km": 30, "blocked": True, "speed_reduction_pct": 90,
    },
]


def _dist(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def analyze_route_hazards(
    coordinates: List[List[float]],
    season_monsoon: bool = False,
    active_closures: List[str] = None,
) -> Dict[str, Any]:
    """
    Analyze the full list of route coordinates (GeoJSON [lon, lat] or [lat, lon]).
    Returns hazard scores, overall disaster risk %, critical warnings, and segmented risk coordinates.
    """
    active_closures = active_closures or []
    if not coordinates:
        return {
            "flood_risk": 0.0,
            "landslide_risk": 0.0,
            "cyclone_risk": 0.0,
            "rainfall_risk": 0.0,
            "road_closure_risk": 0.0,
            "overall_disaster_risk": 0.0,
            "safety_score": 100.0,
            "hazard_level": "LOW",
            "warnings": [],
            "segments": [],
        }

    # Normalize coordinates to [[lat, lon], ...]
    normalized_coords: List[Tuple[float, float]] = []
    for c in coordinates:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            # Check if [lon, lat] (OSRM) where lon > 60 and lat < 40 for India
            if c[0] > 60.0 and c[1] < 40.0:
                normalized_coords.append((float(c[1]), float(c[0])))
            else:
                normalized_coords.append((float(c[0]), float(c[1])))

    # Subsample points along route (every 10-25 km) for fast & dense hazard checking
    sample_step = max(1, len(normalized_coords) // 40)
    sampled = normalized_coords[::sample_step]
    if normalized_coords[-1] not in sampled:
        sampled.append(normalized_coords[-1])

    max_flood = 0.0
    max_landslide = 0.0
    max_cyclone = 0.0
    max_rain = 0.0
    max_closure = 0.0
    warnings = []
    segment_evaluations = []

    rain_baseline = 40.0 if season_monsoon else 15.0

    for i, (lat, lon) in enumerate(sampled):
        # Calculate elevation proxy by latitude and terrain
        elev_m = 700.0 if (lat > 28.0 or (lat > 10.0 and lat < 19.0 and lon < 75.5)) else 40.0

        flood_res = evaluate_flood_risk(lat, lon, rainfall_mm=rain_baseline, elevation_m=elev_m)
        landslide_res = evaluate_landslide_risk(lat, lon, rainfall_mm=rain_baseline, elevation_m=elev_m)
        cyclone_res = evaluate_cyclone_risk(lat, lon, wind_kmph=35.0 if season_monsoon else 20.0)
        rain_res = evaluate_rainfall_risk(rainfall_mm=rain_baseline)

        # Check incidents proximity
        point_closure_risk = 0.0
        for inc in PAN_INDIA_INCIDENTS:
            dist = _dist(lat, lon, inc["lat"], inc["lon"])
            if dist <= inc["impact_radius_km"]:
                if inc["blocked"]:
                    point_closure_risk = max(point_closure_risk, 95.0)
                    warn_text = f"🚨 {inc['type']} Blockage: {inc['location']} — {inc['message']}"
                    if warn_text not in warnings:
                        warnings.append(warn_text)
                else:
                    if inc["type"] == "FLOOD":
                        flood_res["score"] = max(flood_res["score"], 88.0)
                    elif inc["type"] == "LANDSLIDE":
                        landslide_res["score"] = max(landslide_res["score"], 86.0)
                    elif inc["type"] == "CYCLONE":
                        cyclone_res["score"] = max(cyclone_res["score"], 84.0)

        # Track maximums
        if flood_res["score"] > max_flood:
            max_flood = flood_res["score"]
            if flood_res["severity"] in ["HIGH", "CRITICAL"] and flood_res["description"] not in warnings:
                warnings.append(f"🌊 {flood_res['description']}")

        if landslide_res["score"] > max_landslide:
            max_landslide = landslide_res["score"]
            if landslide_res["severity"] in ["HIGH", "CRITICAL"] and landslide_res["description"] not in warnings:
                warnings.append(f"⛰️ {landslide_res['description']}")

        if cyclone_res["score"] > max_cyclone:
            max_cyclone = cyclone_res["score"]
            if cyclone_res["severity"] in ["HIGH", "CRITICAL"] and cyclone_res["description"] not in warnings:
                warnings.append(f"🌪️ {cyclone_res['description']}")

        max_rain = max(max_rain, rain_res["score"])
        max_closure = max(max_closure, point_closure_risk)

        # Local point combined risk
        local_hazard = max(
            flood_res["score"] * 0.9,
            landslide_res["score"] * 0.9,
            cyclone_res["score"] * 0.85,
            point_closure_risk,
            (flood_res["score"] + landslide_res["score"] + rain_res["score"]) / 3.0
        )
        
        # Segment color
        if local_hazard >= 70.0:
            color = "#C93B3B"  # Critical (Red)
            level = "CRITICAL"
        elif local_hazard >= 45.0:
            color = "#D97350"  # High (Orange)
            level = "HIGH"
        elif local_hazard >= 25.0:
            color = "#D99B26"  # Moderate (Yellow)
            level = "MODERATE"
        else:
            color = "#2E8B57"  # Low / Safe (Green)
            level = "LOW"

        segment_evaluations.append({
            "coord": [lat, lon],
            "risk_score": round(local_hazard, 1),
            "level": level,
            "color": color,
        })

    # Non-linear Overall Disaster Risk calculation
    # If a critical risk exists (e.g. 90+ flood or closure), it dominates the risk score
    highest_single_risk = max(max_flood, max_landslide, max_cyclone, max_closure)
    average_hazard = (max_flood * 0.35 + max_landslide * 0.30 + max_cyclone * 0.20 + max_rain * 0.15)
    
    overall_risk = max(highest_single_risk * 0.75, average_hazard)
    overall_risk = round(min(100.0, max(0.0, overall_risk)), 1)
    
    safety_score = round(max(5.0, 100.0 - overall_risk), 1)

    if overall_risk >= 70.0:
        hazard_level = "CRITICAL"
    elif overall_risk >= 45.0:
        hazard_level = "HIGH"
    elif overall_risk >= 25.0:
        hazard_level = "MODERATE"
    else:
        hazard_level = "LOW"

    return {
        "flood_risk": round(max_flood, 1),
        "landslide_risk": round(max_landslide, 1),
        "cyclone_risk": round(max_cyclone, 1),
        "rainfall_risk": round(max_rain, 1),
        "road_closure_risk": round(max_closure, 1),
        "overall_disaster_risk": overall_risk,
        "safety_score": safety_score,
        "hazard_level": hazard_level,
        "warnings": warnings[:5],
        "segment_points": segment_evaluations,
    }


def list_active_pan_india_hazards() -> List[Dict[str, Any]]:
    """Return all active monitored hazards across India for the map layer."""
    return list(PAN_INDIA_INCIDENTS)
