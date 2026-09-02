# ML Service

Standalone intelligence layer for the Smart Rental Tracking System.

## Structure

```text
ml-service/
├── data/
│   ├── raw/
│   │   ├── rental_demand_history.csv
│   │   └── telemetry_history.csv
│   └── processed/
│       ├── forecasting_features.csv
│       └── anomaly_features.csv
├── models/
│   ├── xgboost_demand_model.json
│   └── isolation_forest.pkl
├── outputs/
│   ├── demand_predictions.csv
│   └── anomaly_predictions.csv
├── feature_engineering.py
├── forecasting.py
├── anomaly_engine.py
├── train_forecasting.py
├── train_anomaly.py
├── service.py
├── requirements.txt
└── README.md
```

## Implemented Capabilities

- Demand forecasting by `site_code` and `equipment_type`
- Time-series feature engineering from date, weekday seasonality, and business-day signals
- Random Forest regression when enough history exists, with Linear Regression and seasonal baseline fallbacks
- Isolation Forest anomaly detection for unusual telemetry windows
- Rule-based anomaly detection for excessive speed, excessive idle time, and rapid fuel loss
- Forecast-aware asset reallocation recommendations based on site/equipment demand gaps

## Input Contracts

Historical demand records:

```json
{
  "site_code": "S1",
  "equipment_type": "EXCAVATOR",
  "date": "2026-08-01",
  "count": 4
}
```

Telemetry records:

```json
{
  "equipment_id": "EQX1001",
  "speed": 18.5,
  "fuel_level": 72.0,
  "idle_hours": 0.4,
  "engine_hours": 540.2
}
```

Equipment inventory records:

```json
{
  "equipment_id": "EQX1001",
  "equipment_type": "EXCAVATOR",
  "site_code": "S1",
  "status": "AVAILABLE"
}
```

## Run Tests

```powershell
pip install -r ml-service/requirements.txt
python ml-service/feature_engineering.py
python ml-service/train_forecasting.py
python ml-service/train_anomaly.py
python -m pytest ml-service -q
```
