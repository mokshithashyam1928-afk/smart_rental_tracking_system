"""Train and persist XGBoost demand forecasting model and processed feature dataset."""
import json
import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

from feature_engineering import BASE_DIR, create_forecasting_features
from preprocessing import DataPreprocessor

RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "rental_demand_history.csv"
if not RAW_DATA_PATH.exists():
    RAW_DATA_PATH = BASE_DIR / "data" / "forecasting_dataset.csv"

PROCESSED_DATA_PATH = BASE_DIR / "data" / "processed" / "forecasting_dataset.csv"
MODEL_PKL_PATH = BASE_DIR / "models" / "xgboost_forecasting.pkl"
MODEL_JSON_PATH = BASE_DIR / "models" / "xgboost_demand_model.json"
METADATA_PATH = BASE_DIR / "models" / "model_metadata.json"

PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
MODEL_PKL_PATH.parent.mkdir(parents=True, exist_ok=True)


def train_forecasting_model():
    print("Loading demand dataset...")
    if not RAW_DATA_PATH.exists():
        DataPreprocessor.load_raw_datasets()

    df = pd.read_csv(RAW_DATA_PATH)
    df = DataPreprocessor.clean_demand_data(df)

    print("Engineering demand forecasting features...")
    df_features = create_forecasting_features(df)
    df_features.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"Saved processed forecasting dataset ({len(df_features)} rows) to {PROCESSED_DATA_PATH}")

    # Categorical One-Hot Encoding
    df_encoded = pd.get_dummies(df_features, columns=["site_id", "equipment_type"], dtype=int)
    exclude_cols = ["record_id", "date", "count", "site_code"]
    feature_cols = [c for c in df_encoded.columns if c not in exclude_cols]

    # Time-based split (80% Train, 20% Test)
    unique_dates = sorted(df_encoded["date"].unique())
    split_idx = int(len(unique_dates) * 0.80)
    train_dates = unique_dates[:split_idx]
    test_dates = unique_dates[split_idx:]

    train_df = df_encoded[df_encoded["date"].isin(train_dates)]
    test_df = df_encoded[df_encoded["date"].isin(test_dates)]

    X_train, y_train = train_df[feature_cols], train_df["count"]
    X_test, y_test = test_df[feature_cols], test_df["count"]

    print(f"Training rows: {len(X_train)} | Testing rows: {len(X_test)}")

    # Hyperparameters
    model_params = {
        "n_estimators": 300,
        "learning_rate": 0.03,
        "max_depth": 5,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": 42,
        "n_jobs": -1
    }

    model = XGBRegressor(**model_params)
    model.fit(X_train, y_train)

    # Predictions
    preds = model.predict(X_test).clip(min=0)
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    wape = (np.sum(np.abs(y_test - preds)) / np.sum(np.abs(y_test))) * 100

    print(f"Evaluation -> MAE: {mae:.4f} | RMSE: {rmse:.4f} | WAPE: {wape:.2f}%")

    # Save artifacts
    joblib.dump(model, MODEL_PKL_PATH)
    model.save_model(MODEL_JSON_PATH)

    # Save metadata
    metadata = {
        "model_name": "XGBoost Demand Forecaster",
        "version": "1.0.0",
        "training_date": str(pd.Timestamp.now()),
        "features": feature_cols,
        "hyperparameters": model_params,
        "metrics": {
            "MAE": round(mae, 4),
            "RMSE": round(rmse, 4),
            "WAPE_percent": round(wape, 2)
        }
    }
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Saved model to {MODEL_PKL_PATH} and metadata to {METADATA_PATH}")
    return model, metadata


if __name__ == "__main__":
    train_forecasting_model()
