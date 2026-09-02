"""
Inference interface for ML demand forecasting and anomaly detection.
"""
from pathlib import Path
import joblib
import pandas as pd

from forecasting import DemandForecaster
from anomaly_engine import AnomalyDetectionEngine

BASE_DIR = Path(__file__).resolve().parent


class MLPredictor:
    def __init__(self):
        self.forecaster = DemandForecaster()
        self.anomaly_engine = AnomalyDetectionEngine()

    def predict_demand(self, historical_data: list, days_ahead: int = 7):
        return self.forecaster.forecast_demand(historical_data, days_ahead=days_ahead)

    def detect_anomalies(self, telemetry_window: list):
        return self.anomaly_engine.evaluate_telemetry_window(telemetry_window)


if __name__ == "__main__":
    predictor = MLPredictor()
    sample_demand = [
        {"site_code": "S-CAT-BLR01", "equipment_type": "EXCAVATOR", "date": "2026-08-01", "count": 4},
        {"site_code": "S-CAT-BLR01", "equipment_type": "EXCAVATOR", "date": "2026-08-02", "count": 5},
    ]
    forecast = predictor.predict_demand(sample_demand, days_ahead=3)
    print("Demand Forecast Sample:", forecast)
