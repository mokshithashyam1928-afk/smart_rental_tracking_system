"""Train and persist Isolation Forest model and processed anomaly dataset."""
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

from feature_engineering import BASE_DIR, build_anomaly_features
from preprocessing import DataPreprocessor
from anomaly_engine import AnomalyDetectionEngine

RAW_TELEMETRY_PATH = BASE_DIR / "data" / "raw" / "telemetry.csv"
if not RAW_TELEMETRY_PATH.exists():
    RAW_TELEMETRY_PATH = BASE_DIR / "data" / "raw" / "telemetry_history.csv"

PROCESSED_ANOMALY_PATH = BASE_DIR / "data" / "processed" / "anomaly_dataset.csv"
MODEL_PATH = BASE_DIR / "models" / "isolation_forest.pkl"

PROCESSED_ANOMALY_PATH.parent.mkdir(parents=True, exist_ok=True)
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

FEATURE_COLUMNS = [
    "speed",
    "fuel_level",
    "idle_hours",
    "engine_hours",
    "fuel_drop_1h",
    "engine_increment_1h",
    "idle_increment_1h",
    "rolling_speed_6h",
    "rolling_speed_std_6h",
    "latitude_change",
    "longitude_change",
]


def train_anomaly_model() -> pd.DataFrame:
    print("Loading raw telemetry data...")
    if not RAW_TELEMETRY_PATH.exists():
        DataPreprocessor.load_raw_datasets()

    features = build_anomaly_features(input_path=RAW_TELEMETRY_PATH)
    
    print("Training Isolation Forest model...")
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    labels = model.fit_predict(features[FEATURE_COLUMNS])
    scores = -model.score_samples(features[FEATURE_COLUMNS])

    # Rule-Based Engine integration for complete anomaly dataset
    engine = AnomalyDetectionEngine()
    
    dataset_df = features[["equipment_id", "timestamp", "speed", "fuel_level", "idle_hours", "engine_hours"]].copy()
    dataset_df["excessive_speed"] = (dataset_df["speed"] > 80.0).astype(int)
    dataset_df["rapid_fuel_drop"] = (features["fuel_drop_1h"] >= 15.0).astype(int)
    dataset_df["excessive_idle"] = (dataset_df["idle_hours"] > 3.0).astype(int)
    dataset_df["anomaly_score"] = scores.round(4)
    dataset_df["is_anomaly"] = (labels == -1).astype(int)

    # Save outputs
    joblib.dump(model, MODEL_PATH)
    dataset_df.to_csv(PROCESSED_ANOMALY_PATH, index=False)
    print(f"Saved Isolation Forest model to {MODEL_PATH}")
    print(f"Saved processed anomaly dataset ({len(dataset_df)} rows) to {PROCESSED_ANOMALY_PATH}")
    return dataset_df


if __name__ == "__main__":
    train_anomaly_model()
