"""
Risk Prediction Model
-----------------------
A real, trained scikit-learn RandomForestClassifier — not a hardcoded
number. Since no historical incident dataset is available yet, this module
generates a synthetic-but-structured training set using domain rules (heavy
rain + hilly terrain + old surface => higher disruption probability), trains
a RandomForest on it, and persists the model to ml_models/risk_model.pkl.

Swap `generate_synthetic_training_data()` for a query against your real
`incidents` + `weather_records` + `roads` tables once you have historical
data, and everything downstream (features.py-equivalent, predict()) keeps
working unchanged.
"""
import os
import pickle
import random

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score

from . import weather as weather_mod
from . import traffic_incidents as ti_mod
from .graph_data import RoadSegment

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml_models", "risk_model.pkl")

FEATURE_COLUMNS = [
    "rainfall_mm",
    "wind_kmph",
    "visibility_km",
    "traffic_congestion",
    "road_condition",
    "distance_km",
    "terrain_hilly",
    "road_type_nh",
    "surface_paved",
    "season_monsoon",
    "incident_severity_sum",
]


def generate_synthetic_training_data(n=4000, seed=42) -> pd.DataFrame:
    rnd = random.Random(seed)
    rows = []
    for _ in range(n):
        rainfall = rnd.uniform(0, 120)
        wind = rnd.uniform(5, 60)
        visibility = rnd.uniform(1, 10)
        traffic = rnd.uniform(0, 100)
        road_condition = rnd.uniform(30, 95)
        distance = rnd.uniform(50, 350)
        terrain_hilly = rnd.choice([0, 1])
        road_type_nh = rnd.choice([0, 1])
        surface_paved = rnd.choice([0, 1]) if road_condition < 70 else 1
        season_monsoon = rnd.choice([0, 1])
        incident_sev = rnd.choice([0, 0, 0, 1, 2, 3, 5, 8])

        # Rule-based ground truth (mirrors real-world disruption drivers).
        disruption_score = (
            0.30 * (rainfall / 120)
            + 0.10 * (wind / 60)
            + 0.10 * (1 - visibility / 10)
            + 0.10 * (traffic / 100)
            + 0.15 * (1 - road_condition / 100)
            + 0.10 * terrain_hilly
            + 0.05 * (1 - surface_paved)
            + 0.10 * season_monsoon
            + 0.10 * (incident_sev / 8)
        )
        disruption_score += rnd.uniform(-0.07, 0.07)  # noise
        label = 1 if disruption_score > 0.45 else 0

        rows.append(dict(
            rainfall_mm=rainfall, wind_kmph=wind, visibility_km=visibility,
            traffic_congestion=traffic, road_condition=road_condition,
            distance_km=distance, terrain_hilly=terrain_hilly,
            road_type_nh=road_type_nh, surface_paved=surface_paved,
            season_monsoon=season_monsoon, incident_severity_sum=incident_sev,
            disrupted=label,
        ))
    return pd.DataFrame(rows)


def train_and_save_model(verbose=True) -> dict:
    df = generate_synthetic_training_data()
    X = df[FEATURE_COLUMNS]
    y = df["disrupted"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    probs = clf.predict_proba(X_test)[:, 1]
    metrics = {
        "accuracy": round(accuracy_score(y_test, preds), 4),
        "roc_auc": round(roc_auc_score(y_test, probs), 4),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "feature_importances": dict(zip(FEATURE_COLUMNS, [round(x, 4) for x in clf.feature_importances_])),
    }
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)

    if verbose:
        print("Risk model trained.")
        print(f"  accuracy: {metrics['accuracy']}   roc_auc: {metrics['roc_auc']}")
        print(f"  train/test size: {metrics['n_train']}/{metrics['n_test']}")
        print("  top features:", sorted(metrics["feature_importances"].items(), key=lambda x: -x[1])[:4])
    return metrics


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
        print(f"[Risk model] Could not load cached model ({e}); retraining...")
        train_and_save_model(verbose=False)
        with open(MODEL_PATH, "rb") as f:
            _model_cache = pickle.load(f)
    return _model_cache


def build_features(road: RoadSegment, season_monsoon: bool = False) -> pd.DataFrame:
    w = weather_mod.get_weather(road.road_id)
    traffic = ti_mod.get_traffic_congestion(road.road_id)
    incident_sev = sum(i.severity for i in ti_mod.list_incidents(road.road_id))

    row = {
        "rainfall_mm": w.rainfall_mm,
        "wind_kmph": w.wind_kmph,
        "visibility_km": w.visibility_km,
        "traffic_congestion": traffic,
        "road_condition": road.base_condition,
        "distance_km": road.distance_km,
        "terrain_hilly": 1 if road.terrain == "hilly" else 0,
        "road_type_nh": 1 if road.road_type == "NH" else 0,
        "surface_paved": 1 if road.surface == "paved" else 0,
        "season_monsoon": 1 if season_monsoon else 0,
        "incident_severity_sum": incident_sev,
    }
    return pd.DataFrame([row])[FEATURE_COLUMNS]


def predict_risk(road: RoadSegment, season_monsoon: bool = False) -> dict:
    if road.status == "CLOSED":
        return {"road_id": road.road_id, "risk_probability": 1.0, "risk_level": "CLOSED"}

    model = _load_model()
    X = build_features(road, season_monsoon=season_monsoon)
    prob = float(model.predict_proba(X)[0, 1])

    if prob >= 0.66:
        level = "HIGH"
    elif prob >= 0.35:
        level = "MODERATE"
    else:
        level = "LOW"

    return {"road_id": road.road_id, "risk_probability": round(prob, 3), "risk_level": level}
