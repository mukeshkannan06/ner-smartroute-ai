"""
Landslide Hazard Intelligence Module
-------------------------------------
Analyzes terrain slope, elevation, historical landslide inventory, and precipitation triggers across:
- Himalayas & Sub-Himalayas (Jammu & Kashmir, Ladakh, Himachal Pradesh, Uttarakhand, Sikkim, Darjeeling)
- Western Ghats (Maharashtra Konkan Ghats, Goa border, Coorg, Nilgiris, Wayanad, Idukki)
- Northeast Mountainous Corridors (Meghalaya, Nagaland, Manipur, Mizoram, Arunachal Pradesh)
"""
import math
from typing import Dict, Any, List


LANDSLIDE_PRONE_REGIONS = [
    # Himalayas
    {"name": "Jammu-Srinagar NH-44 Corridor", "lat": 33.20, "lon": 75.10, "radius_km": 100, "base_risk": 85, "terrain": "Himalayan steep slope"},
    {"name": "Rishikesh-Badrinath-Kedarnath Highway", "lat": 30.40, "lon": 78.80, "radius_km": 90, "base_risk": 88, "terrain": "Fragile Garhwal Himalayas"},
    {"name": "Shimla-Kinnaur NH-05", "lat": 31.40, "lon": 77.80, "radius_km": 80, "base_risk": 80, "terrain": "Himachal steep slopes"},
    {"name": "Darjeeling & Sikkim NH-10 (Sevoke–Gangtok)", "lat": 27.10, "lon": 88.50, "radius_km": 70, "base_risk": 84, "terrain": "Teesta gorge slope"},
    
    # Northeast Hills
    {"name": "Shillong-Silchar (Meghalaya Plateau Edge)", "lat": 25.20, "lon": 92.30, "radius_km": 80, "base_risk": 82, "terrain": "High rainfall sandstone slope"},
    {"name": "Kohima-Imphal (NH-02 Naga-Manipur Hills)", "lat": 25.20, "lon": 93.90, "radius_km": 90, "base_risk": 78, "terrain": "Clay-rich hill cuttings"},
    {"name": "Aizawl–Silchar Mountain Highway", "lat": 24.10, "lon": 92.70, "radius_km": 80, "base_risk": 74, "terrain": "Mizo fold mountain belt"},
    
    # Western Ghats
    {"name": "Mumbai-Goa NH-66 (Kashedi & Parshuram Ghats)", "lat": 17.80, "lon": 73.50, "radius_km": 80, "base_risk": 76, "terrain": "Laterite coastal escarpment"},
    {"name": "Wayanad-Idukki Ghat Pass (Kerala)", "lat": 10.80, "lon": 76.50, "radius_km": 80, "base_risk": 80, "terrain": "Western Ghats heavy downpour belt"},
    {"name": "Charmadi & Shiradi Ghat (Karnataka)", "lat": 12.90, "lon": 75.60, "radius_km": 60, "base_risk": 72, "terrain": "Ghat slope cutting"},
]


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def evaluate_landslide_risk(lat: float, lon: float, rainfall_mm: float = 15.0, elevation_m: float = 300.0) -> Dict[str, Any]:
    """
    Calculate landslide hazard score (0–100) and warning details.
    """
    max_proximity_risk = 0.0
    active_zone_name = None
    terrain_type = "plain"

    for zone in LANDSLIDE_PRONE_REGIONS:
        dist = _haversine(lat, lon, zone["lat"], zone["lon"])
        if dist <= zone["radius_km"]:
            proximity = 1.0 - 0.75 * (dist / zone["radius_km"])
            zone_risk = zone["base_risk"] * proximity
            if zone_risk > max_proximity_risk:
                max_proximity_risk = zone_risk
                active_zone_name = zone["name"]
                terrain_type = zone["terrain"]

    # General slope/mountain indicator by latitude and elevation
    is_mountainous = elevation_m > 600.0 or lat > 27.0 or (lat > 8.0 and lat < 21.0 and lon < 75.8)
    
    if is_mountainous and max_proximity_risk == 0.0:
        base_slope_risk = min(50.0, (elevation_m / 2000.0) * 50.0)
    else:
        base_slope_risk = max_proximity_risk

    # Rain trigger: Landslides in India strongly correlate with >70mm rainfall in 24h
    if rainfall_mm > 100.0:
        rain_multiplier = 1.5
    elif rainfall_mm > 50.0:
        rain_multiplier = 1.2
    else:
        rain_multiplier = 0.75

    raw_score = base_slope_risk * rain_multiplier
    score = round(max(0.0, min(100.0, raw_score)), 1)

    if score >= 75.0:
        severity = "HIGH"
        description = f"High landslide risk on {active_zone_name or 'mountain highway'}. Unstable slopes & rockfall alerts active."
    elif score >= 50.0:
        severity = "MODERATE"
        description = f"Moderate landslide vulnerability in {active_zone_name or 'hilly terrain'}. Drive cautiously during rain."
    elif score >= 25.0:
        severity = "LOW"
        description = "Low slope failure hazard."
    else:
        severity = "VERY_LOW"
        description = "Stable plain terrain."

    return {
        "score": score,
        "severity": severity,
        "active_zone": active_zone_name,
        "terrain": terrain_type,
        "description": description,
        "high_slope": is_mountainous,
    }
