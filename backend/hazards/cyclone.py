"""
Cyclone & Coastal Storm Hazard Intelligence Module
---------------------------------------------------
Evaluates coastal cyclone risk, gale force winds, and tidal storm surge along:
- East Coast: Tamil Nadu, Andhra Pradesh, Odisha, West Bengal (Bay of Bengal cyclone belt)
- West Coast: Gujarat (Kutch/Saurashtra), Maharashtra, Kerala (Arabian Sea cyclonic tracks)
"""
import math
from typing import Dict, Any, List


COASTAL_CYCLONE_CORRIDORS = [
    {"name": "Odisha & North Andhra Coastal Belt (Puri–Balasore–Visakhapatnam)", "lat": 19.80, "lon": 85.80, "radius_km": 180, "base_risk": 75, "coast": "East"},
    {"name": "West Bengal Coastal Sunderbans (Digha–Kolkata)", "lat": 21.80, "lon": 88.10, "radius_km": 140, "base_risk": 70, "coast": "East"},
    {"name": "South Andhra & North Tamil Nadu Coast (Chennai–Nellore)", "lat": 14.00, "lon": 80.10, "radius_km": 150, "base_risk": 68, "coast": "East"},
    {"name": "Nagapattinam–Cuddalore Delta (Tamil Nadu)", "lat": 11.20, "lon": 79.80, "radius_km": 120, "base_risk": 72, "coast": "East"},
    {"name": "Gujarat Saurashtra & Kutch Coast", "lat": 22.30, "lon": 69.80, "radius_km": 160, "base_risk": 64, "coast": "West"},
    {"name": "Konkan Coast (Mumbai–Ratnagiri)", "lat": 18.00, "lon": 73.00, "radius_km": 130, "base_risk": 55, "coast": "West"},
]


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def evaluate_cyclone_risk(lat: float, lon: float, wind_kmph: float = 25.0) -> Dict[str, Any]:
    """
    Calculate cyclone exposure risk score (0–100) and severity.
    """
    max_proximity_risk = 0.0
    active_corridor_name = None

    for zone in COASTAL_CYCLONE_CORRIDORS:
        dist = _haversine(lat, lon, zone["lat"], zone["lon"])
        if dist <= zone["radius_km"]:
            proximity = 1.0 - 0.7 * (dist / zone["radius_km"])
            corridor_risk = zone["base_risk"] * proximity
            if corridor_risk > max_proximity_risk:
                max_proximity_risk = corridor_risk
                active_corridor_name = zone["name"]

    # Wind speed multiplier: > 60 km/h indicates active gale warning
    if wind_kmph > 70.0:
        wind_factor = 1.6
    elif wind_kmph > 45.0:
        wind_factor = 1.25
    else:
        wind_factor = 0.8

    raw_score = max_proximity_risk * wind_factor
    score = round(max(0.0, min(100.0, raw_score)), 1)

    if score >= 75.0:
        severity = "HIGH"
        description = f"Severe cyclone impact alert along {active_corridor_name}. Strong gales and tidal inundation warning."
    elif score >= 45.0:
        severity = "MODERATE"
        description = f"Moderate coastal storm/cyclone exposure near {active_corridor_name}."
    elif score >= 20.0:
        severity = "LOW"
        description = "Low coastal wind alert."
    else:
        severity = "VERY_LOW"
        description = "Inland or protected corridor with minimal cyclone exposure."

    return {
        "score": score,
        "severity": severity,
        "active_zone": active_corridor_name,
        "description": description,
        "is_coastal": max_proximity_risk > 0.0,
    }
