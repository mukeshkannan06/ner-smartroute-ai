"""
Weather Service — Abstraction layer for weather data
------------------------------------------------------
Wraps the existing weather.py prototype data.
Designed to support a real weather API (IMD/OpenWeatherMap) later
via environment variable configuration.
"""
import os
from typing import Dict, Any, List, Optional

from ..weather import get_weather, weather_risk_score, WeatherReading
from ..graph_data import NODES, ROADS


# Check if a real weather API is configured
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
DATA_MODE = "live" if WEATHER_API_KEY else "prototype"


def get_current_weather(location: str) -> Dict[str, Any]:
    """
    Get current weather for a location.
    Falls back to prototype data if no API key is configured.
    """
    # Find the closest road to this location for prototype data
    if location in NODES:
        # Find all roads connected to this node
        connected_roads = [r for r in ROADS if r.a == location or r.b == location]
        if connected_roads:
            road = connected_roads[0]
            reading = get_weather(road.road_id)
            risk = weather_risk_score(reading)
            return {
                "location": location,
                "data_mode": DATA_MODE,
                "temperature_c": reading.temperature_c,
                "rainfall_mm": reading.rainfall_mm,
                "wind_kmph": reading.wind_kmph,
                "visibility_km": reading.visibility_km,
                "weather_risk_score": round(risk, 1),
                "risk_level": "High" if risk > 60 else "Medium" if risk > 30 else "Low",
                "conditions": _describe_conditions(reading),
            }

    # Default fallback
    return {
        "location": location,
        "data_mode": DATA_MODE,
        "temperature_c": 25.0,
        "rainfall_mm": 10.0,
        "wind_kmph": 15.0,
        "visibility_km": 8.0,
        "weather_risk_score": 20.0,
        "risk_level": "Low",
        "conditions": "Partly cloudy",
    }


def get_route_weather(route_roads: List[str]) -> Dict[str, Any]:
    """
    Get weather conditions along a route.
    Returns aggregate weather info for all road segments.
    """
    segments = []
    total_risk = 0

    for road_id in route_roads:
        reading = get_weather(road_id)
        risk = weather_risk_score(reading)
        total_risk += risk
        segments.append({
            "road_id": road_id,
            "rainfall_mm": reading.rainfall_mm,
            "wind_kmph": reading.wind_kmph,
            "visibility_km": reading.visibility_km,
            "temperature_c": reading.temperature_c,
            "risk_score": round(risk, 1),
        })

    avg_risk = round(total_risk / len(segments), 1) if segments else 0

    return {
        "data_mode": DATA_MODE,
        "segments": segments,
        "average_risk": avg_risk,
        "overall_risk_level": "High" if avg_risk > 60 else "Medium" if avg_risk > 30 else "Low",
    }


def calculate_weather_risk(reading: WeatherReading) -> float:
    """Calculate weather risk score (0-100) from a reading."""
    return weather_risk_score(reading)


def _describe_conditions(reading: WeatherReading) -> str:
    """Generate a human-readable weather description."""
    conditions = []
    if reading.rainfall_mm > 40:
        conditions.append("Heavy rain")
    elif reading.rainfall_mm > 15:
        conditions.append("Moderate rain")
    elif reading.rainfall_mm > 5:
        conditions.append("Light rain")

    if reading.wind_kmph > 35:
        conditions.append("strong winds")
    elif reading.wind_kmph > 20:
        conditions.append("moderate winds")

    if reading.visibility_km < 3:
        conditions.append("poor visibility")
    elif reading.visibility_km < 5:
        conditions.append("reduced visibility")

    if not conditions:
        if reading.temperature_c > 30:
            conditions.append("Hot and clear")
        else:
            conditions.append("Fair weather")

    return ", ".join(conditions)
