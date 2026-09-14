"""
Flood Hazard Intelligence Module
---------------------------------
Calculates flood and waterlogging risks based on:
- Major river basins (Ganga, Brahmaputra, Barak, Mahanadi, Godavari, Krishna, Cauvery)
- Flood-prone coastal and delta districts in India (Assam, Bihar, Odisha, West Bengal, Tamil Nadu, Andhra Pradesh, Gujarat, Kerala)
- Terrain elevation, historical flood recurrence, and live/simulated rainfall
"""
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass


# Defined high-risk flood zones with center coordinates, radius (km), and baseline severity
FLOOD_ZONES = [
    {"name": "Brahmaputra Valley (Assam)", "lat": 26.20, "lon": 92.50, "radius_km": 160, "base_risk": 75, "state": "Assam", "river": "Brahmaputra"},
    {"name": "Barak Valley (Silchar)", "lat": 24.83, "lon": 92.80, "radius_km": 80, "base_risk": 70, "state": "Assam", "river": "Barak"},
    {"name": "Mahanadi Delta (Odisha)", "lat": 20.35, "lon": 86.10, "radius_km": 140, "base_risk": 78, "state": "Odisha", "river": "Mahanadi"},
    {"name": "Balasore-Bhadrak Coastal Belt", "lat": 21.30, "lon": 86.80, "radius_km": 90, "base_risk": 72, "state": "Odisha", "river": "Subarnarekha"},
    {"name": "North Bihar Flood Plain", "lat": 26.10, "lon": 85.90, "radius_km": 150, "base_risk": 82, "state": "Bihar", "river": "Kosi / Gandak"},
    {"name": "Sundarbans & Lower Gangetic Plain", "lat": 22.20, "lon": 88.60, "radius_km": 120, "base_risk": 68, "state": "West Bengal", "river": "Ganga / Hooghly"},
    {"name": "Godavari-Krishna Delta", "lat": 16.60, "lon": 81.30, "radius_km": 110, "base_risk": 60, "state": "Andhra Pradesh", "river": "Godavari / Krishna"},
    {"name": "Chennai Adyar-Cooum Basin", "lat": 13.04, "lon": 80.20, "radius_km": 60, "base_risk": 58, "state": "Tamil Nadu", "river": "Adyar"},
    {"name": "Kuttanad & Central Kerala", "lat": 9.50, "lon": 76.50, "radius_km": 70, "base_risk": 65, "state": "Kerala", "river": "Pamba"},
]


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two lat/lon points."""
    import math
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def evaluate_flood_risk(lat: float, lon: float, rainfall_mm: float = 15.0, elevation_m: float = 30.0) -> Dict[str, Any]:
    """
    Evaluate flood hazard score (0–100) and severity for a specific coordinate.
    """
    max_proximity_risk = 0.0
    active_zone_name = None

    for zone in FLOOD_ZONES:
        dist = _haversine_distance(lat, lon, zone["lat"], zone["lon"])
        if dist <= zone["radius_km"]:
            # Proximity factor: 1.0 at center, fades to 0.2 at radius boundary
            proximity_factor = 1.0 - 0.8 * (dist / zone["radius_km"])
            zone_risk = zone["base_risk"] * proximity_factor
            if zone_risk > max_proximity_risk:
                max_proximity_risk = zone_risk
                active_zone_name = zone["name"]

    # Elevation modifier: Lowlands (< 25m) are heavily prone, highlands (> 300m) have lower standing flood risk
    if elevation_m < 20.0:
        elevation_factor = 1.25
    elif elevation_m < 80.0:
        elevation_factor = 1.0
    else:
        elevation_factor = max(0.2, 1.0 - (elevation_m - 80) / 400.0)

    # Rainfall contribution: >100mm heavily spikes flood risk
    rain_score = min(100.0, (rainfall_mm / 150.0) * 100.0)

    # Calculate combined score
    if max_proximity_risk > 0:
        raw_score = (max_proximity_risk * 0.60 + rain_score * 0.40) * elevation_factor
    else:
        raw_score = (rain_score * 0.70) * elevation_factor

    score = round(max(0.0, min(100.0, raw_score)), 1)

    if score >= 81.0:
        severity = "CRITICAL"
        description = f"Critical flood warning in {active_zone_name or 'low-lying basin'}. Inundation and impassable roads likely."
    elif score >= 61.0:
        severity = "HIGH"
        description = f"High flood hazard near {active_zone_name or 'river basin'}. Waterlogging and reduced speed expected."
    elif score >= 41.0:
        severity = "MODERATE"
        description = "Moderate water accumulation and drainage vulnerability."
    elif score >= 21.0:
        severity = "LOW"
        description = "Minor waterlogging risk during persistent downpours."
    else:
        severity = "VERY_LOW"
        description = "Negligible flood exposure."

    return {
        "score": score,
        "severity": severity,
        "active_zone": active_zone_name,
        "description": description,
        "waterlogging_risk": score >= 50.0,
    }
