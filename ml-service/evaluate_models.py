"""
Comprehensive Evaluation Script for Person 3 ML Pipeline:
1. Demand Forecasting (Baseline vs XGBoost Regressor) -> MAE, RMSE, WAPE
2. Anomaly Detection (Isolation Forest + Rule-Based Engine) -> Severity breakdown & Detection stats
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

from feature_engineering import (
    BASE_DIR,
    create_forecasting_features,
    create_anomaly_features
)
from anomaly_engine import AnomalyDetectionEngine

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
MODEL_DIR = BASE_DIR / "models"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def evaluate_demand_forecasting():
    print("\n" + "=" * 60)
    print(" 1. RUNNING DEMAND FORECASTING (BASELINE vs XGBOOST)")
    print("=" * 60)

    input_path = DATA_DIR / "forecasting_dataset.csv"
    if not input_path.exists():
        input_path = DATA_DIR / "raw" / "rental_demand_history.csv"

    df = pd.read_csv(input_path)
    if "site_id" not in df.columns and "site_code" in df.columns:
        df["site_id"] = df["site_code"]

    df = create_forecasting_features(df)
    
    # One-hot encode categoricals
    df_encoded = pd.get_dummies(df, columns=["site_id", "equipment_type"], dtype=int)
    exclude_cols = ["record_id", "date", "count", "site_code"]
    feature_cols = [c for c in df_encoded.columns if c not in exclude_cols]

    # Time-series chronological split (80% Train, 20% Test)
    unique_dates = sorted(df_encoded["date"].unique())
    split_idx = int(len(unique_dates) * 0.80)
    train_dates = unique_dates[:split_idx]
    test_dates = unique_dates[split_idx:]

    train_df = df_encoded[df_encoded["date"].isin(train_dates)]
    test_df = df_encoded[df_encoded["date"].isin(test_dates)]

    X_train = train_df[feature_cols]
    y_train = train_df["count"]
    X_test = test_df[feature_cols]
    y_test = test_df["count"]

    # 1. Baseline Model (7-day Moving Average)
    baseline_pred = test_df["rolling_mean_7"].clip(lower=0)

    # 2. XGBoost Regressor
    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.03,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    xgb_pred = model.predict(X_test).clip(min=0)

    # Save trained XGBoost model
    model.save_model(MODEL_DIR / "xgboost_demand_model.json")

    # Save Predictions
    res_df = test_df[["date", "count"]].copy()
    if "site_code" in test_df.columns:
        res_df["site_code"] = test_df["site_code"]
    res_df["baseline_pred"] = baseline_pred.values
    res_df["predicted_demand"] = xgb_pred
    res_df.to_csv(OUTPUT_DIR / "demand_predictions.csv", index=False)

    # Calculate Metrics
    def calc_metrics(y_true, y_pred):
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        wape = (np.sum(np.abs(y_true - y_pred)) / np.sum(np.abs(y_true))) * 100
        return mae, rmse, wape

    b_mae, b_rmse, b_wape = calc_metrics(y_test, baseline_pred)
    x_mae, x_rmse, x_wape = calc_metrics(y_test, xgb_pred)

    print(f"Dataset Rows  : {len(df)} total ({len(X_train)} train, {len(X_test)} test)")
    print(f"Train Period  : {train_dates[0].strftime('%Y-%m-%d')} to {train_dates[-1].strftime('%Y-%m-%d')}")
    print(f"Test Period   : {test_dates[0].strftime('%Y-%m-%d')} to {test_dates[-1].strftime('%Y-%m-%d')}\n")
    print("Forecasting Metric Comparison:")
    print(f" {'Model':<15} | {'MAE':<8} | {'RMSE':<8} | {'WAPE':<8}")
    print("-" * 50)
    print(f" {'7-Day Baseline':<15} | {b_mae:<8.4f} | {b_rmse:<8.4f} | {b_wape:.2f}%")
    print(f" {'XGBoost Regressor':<15} | {x_mae:<8.4f} | {x_rmse:<8.4f} | {x_wape:.2f}%")
    print("-" * 50)
    print(f"Improvement   : {((b_wape - x_wape) / b_wape * 100):.2f}% WAPE error reduction with XGBoost.")
    return x_mae, x_rmse, x_wape


def evaluate_isolation_forest_and_rules():
    print("\n" + "=" * 60)
    print(" 2. RUNNING ANOMALY DETECTION (ISOLATION FOREST + RULES)")
    print("=" * 60)

    input_path = DATA_DIR / "telemetry.csv"
    if not input_path.exists():
        input_path = DATA_DIR / "raw" / "telemetry_history.csv"

    df = pd.read_csv(input_path)
    engine = AnomalyDetectionEngine(speed_threshold_kmh=80.0, fuel_drop_threshold=15.0)

    telemetry_window = df.to_dict(orient="records")
    
    # Evaluate windows by equipment_id efficiently
    anomalies = []
    groups = df.groupby("equipment_id")
    for eq_id, group in groups:
        window = group.to_dict(orient="records")
        indices = list(range(12, len(window) + 1, 3))
        if len(window) not in indices:
            indices.append(len(window))
        for i in indices:
            sub_window = window[max(0, i - 12):i]
            detected = engine.evaluate_telemetry_window(sub_window)
            anomalies.extend(detected)

    # Deduplicate anomaly outputs
    anomaly_df = pd.DataFrame(anomalies)
    if not anomaly_df.empty:
        anomaly_df = anomaly_df.drop_duplicates(subset=["equipment_id", "anomaly_type", "reason"])
        anomaly_df.to_csv(OUTPUT_DIR / "anomaly_predictions.csv", index=False)

    print(f"Telemetry Records Processed : {len(df)}")
    print(f"Detected Anomalies Count    : {len(anomaly_df)}")
    if not anomaly_df.empty:
        print("\nAnomaly Breakdown by Type:")
        print(anomaly_df["anomaly_type"].value_counts().to_string())
        print("\nAnomaly Breakdown by Severity:")
        print(anomaly_df["severity"].value_counts().to_string())
    print("=" * 60)


if __name__ == "__main__":
    evaluate_demand_forecasting()
    evaluate_isolation_forest_and_rules()
