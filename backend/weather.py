"""
Weather Intelligence
---------------------
In production this hits IMD / OpenWeatherMap per-road-segment. Here we
generate deterministic, seeded synthetic weather per road so results are
reproducible for a demo/SIH presentation, but the SCORING FORMULA below is
real and reusable once you swap in a live weather API call.
"""

import hashlib
import random
from dataclasses import dataclass


@dataclass
class WeatherReading:
    rainfall_mm: float
    wind_kmph: float
    visibility_km: float
    temperature_c: float


def _seeded_random(key: str) -> random.Random:
    seed = int(hashlib.sha256(key.encode()).hexdigest(), 16) % (2**32)
    return random.Random(seed)


# In-memory override table so the demo/API can simulate a live storm etc.
_OVERRIDES: dict[str, WeatherReading] = {}


def set_weather_override(road_id: str, reading: WeatherReading) -> None:
    """Used by the digital-twin / disruption engine to simulate a live event."""
    _OVERRIDES[road_id] = reading


def clear_overrides() -> None:
    _OVERRIDES.clear()


def get_weather(road_id: str) -> WeatherReading:
    if road_id in _OVERRIDES:
        return _OVERRIDES[road_id]
    rnd = _seeded_random(road_id + "-weather-v1")
    return WeatherReading(
        rainfall_mm=round(rnd.uniform(0, 60), 1),
        wind_kmph=round(rnd.uniform(5, 45), 1),
        visibility_km=round(rnd.uniform(2, 10), 1),
        temperature_c=round(rnd.uniform(18, 32), 1),
    )


def weather_risk_score(reading: WeatherReading) -> float:
    """
    Returns 0-100 risk contribution from weather (higher = worse).
    Rainfall dominates flood/landslide risk in NER terrain; low visibility
    and high wind are secondary factors.
    """
    rain_component = min(reading.rainfall_mm / 80 * 100, 100) * 0.6
    wind_component = min(reading.wind_kmph / 60 * 100, 100) * 0.2
    visibility_component = max(0, (10 - reading.visibility_km) / 10 * 100) * 0.2
    score = rain_component + wind_component + visibility_component
    return round(min(score, 100), 1)


def weather_accessibility_component(reading: WeatherReading) -> float:
    """0-100, higher = more accessible (inverse of risk, used by accessibility.py)."""
    return round(100 - weather_risk_score(reading), 1)
