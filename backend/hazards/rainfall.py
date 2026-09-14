"""
Heavy Rainfall & Atmospheric Hazard Module
-------------------------------------------
Evaluates localized heavy downpours, visibility reduction, and road traction degradation.
"""
from typing import Dict, Any


def evaluate_rainfall_risk(rainfall_mm: float, visibility_km: float = 8.0) -> Dict[str, Any]:
    """
    Score rainfall hazard (0–100) and identify visibility issues.
    """
    # IMD classification:
    # Heavy rain: 64.5 to 115.5 mm
    # Very heavy: 115.6 to 204.4 mm
    # Extremely heavy: > 204.4 mm
    if rainfall_mm >= 120.0:
        score = min(100.0, 75.0 + (rainfall_mm - 120.0) * 0.25)
        severity = "HIGH"
        impact = "Extremely heavy precipitation, severe visibility drop (<2 km), extreme aquaplaning risk."
    elif rainfall_mm >= 65.0:
        score = 50.0 + (rainfall_mm - 65.0) * 0.45
        severity = "MODERATE"
        impact = "Heavy rainfall, waterlogging on highway margins, reduced speeds."
    elif rainfall_mm >= 25.0:
        score = 25.0 + (rainfall_mm - 25.0) * 0.6
        severity = "LOW"
        impact = "Moderate showers, wet road surface."
    else:
        score = (rainfall_mm / 25.0) * 20.0
        severity = "VERY_LOW"
        impact = "Light or negligible precipitation."

    # Visibility penalty: < 3 km in fog/rain adds hazard
    if visibility_km < 3.0:
        score = min(100.0, score + (3.0 - visibility_km) * 8.0)

    score = round(score, 1)

    return {
        "score": score,
        "severity": severity,
        "rainfall_mm": rainfall_mm,
        "visibility_km": visibility_km,
        "description": impact,
    }
