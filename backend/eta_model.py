"""
ETA Prediction
---------------
A trained GradientBoostingRegressor over distance/traffic/weather/road
condition/vehicle-type/time-of-day, instead of a naive distance/speed
calculation. Same synthetic-but-structured-training pattern as risk_model.py.
"""
import os
import pickle
import random

import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

from . import weather as weather_mod
from . import traffic_incidents as ti_mod
from .graph_data import RoadSegment

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml_models", "eta_model.pkl")

VEHICLE_BASE_SPEED = {  # km/h, in ideal conditions
    "truck": 45,
    "mini_truck": 50,
    "van": 55,
    "car": 65,
}

FEATURE_COLUMNS = [
    "distance_km", "traffic_congestion", "rainfall_mm", "visibility_km",
    "road_condition", "terrain_hilly", "vehicle_base_speed", "time_of_day_peak",
]


def generate_synthetic_training_data(n=4000, seed=7) -> pd.DataFrame:
    rnd = random.Random(seed)
    rows = []
    for _ in range(n):
        distance = rnd.uniform(50, 700)
        traffic = rnd.uniform(0, 100)
        rainfall = rnd.uniform(0, 120)
        visibility = rnd.uniform(1, 10)
        road_condition = rnd.uniform(30, 95)
        terrain_hilly = rnd.choice([0, 1])
        vehicle_speed = rnd.choice(list(VEHICLE_BASE_SPEED.values()))
        peak = rnd.choice([0, 1])

        effective_speed = vehicle_speed
        effective_speed -= (traffic / 100) * 15
        effective_speed -= (rainfall / 120) * 12
        effective_speed -= terrain_hilly * 8
        effective_speed -= (1 - road_condition / 100) * 10
        effective_speed -= peak * 5
        effective_speed = max(15, effective_speed)
        travel_hours = distance / effective_speed
        travel_hours += rnd.uniform(-0.3, 0.3)  # noise (breaks, checkposts etc.)

        rows.append(dict(
            distance_km=distance, traffic_congestion=traffic, rainfall_mm=rainfall,
            visibility_km=visibility, road_condition=road_condition,
            terrain_hilly=terrain_hilly, vehicle_base_speed=vehicle_speed,
            time_of_day_peak=peak, travel_hours=max(travel_hours, 0.5),
        ))
    return pd.DataFrame(rows)


def train_and_save_model(verbose=True) -> dict:
    df = generate_synthetic_training_data()
    X = df[FEATURE_COLUMNS]
    y = df["travel_hours"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=7)

    model = GradientBoostingRegressor(n_estimators=200, max_depth=3, random_state=7)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mae = round(mean_absolute_error(y_test, preds), 3)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    if verbose:
        print(f"ETA model trained. MAE = {mae} hours on held-out synthetic test set.")
    return {"mae_hours": mae, "n_train": len(X_train), "n_test": len(X_test)}


_model_cache = None


def _load_model():
    global _model_cache
    if _model_cache is not None:
        return _model_cache
    if not os.path.exists(MODEL_PATH):
        train_and_save_model(verbose=False)
    try:
        with open(MODEL_PATH, "rb") as f:
            _model_cache = pickle.load(f)
    except Exception as e:
        # Pickled model is incompatible with the installed scikit-learn
        # version (or corrupted) — retrain instead of crashing the request.
        print(f"[ETA model] Could not load cached model ({e}); retraining...")
        train_and_save_model(verbose=False)
        with open(MODEL_PATH, "rb") as f:
            _model_cache = pickle.load(f)
    return _model_cache


def predict_eta_hours(road: RoadSegment, vehicle_type: str = "truck", peak_hour: bool = False) -> float:
    if road.status == "CLOSED":
        return float("inf")

    w = weather_mod.get_weather(road.road_id)
    traffic = ti_mod.get_traffic_congestion(road.road_id)
    model = _load_model()

    row = {
        "distance_km": road.distance_km,
        "traffic_congestion": traffic,
        "rainfall_mm": w.rainfall_mm,
        "visibility_km": w.visibility_km,
        "road_condition": road.base_condition,
        "terrain_hilly": 1 if road.terrain == "hilly" else 0,
        "vehicle_base_speed": VEHICLE_BASE_SPEED.get(vehicle_type, 45),
        "time_of_day_peak": 1 if peak_hour else 0,
    }
    X = pd.DataFrame([row])[FEATURE_COLUMNS]
    hours = float(model.predict(X)[0])
    return round(max(hours, 0.5), 2)
