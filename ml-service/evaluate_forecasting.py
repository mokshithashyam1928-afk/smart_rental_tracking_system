"""Evaluate saved demand forecasting predictions."""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


PREDICTION_PATH = (
    Path(__file__).resolve().parent
    / "outputs"
    / "demand_predictions.csv"
)


df = pd.read_csv(
    PREDICTION_PATH
)

actual = df["count"]

predicted = df["predicted_demand"]

# ============================================================
# MAE
# ============================================================

mae = mean_absolute_error(
    actual,
    predicted
)

# ============================================================
# RMSE
# ============================================================

rmse = np.sqrt(
    mean_squared_error(
        actual,
        predicted
    )
)

# ============================================================
# WAPE
# ============================================================

wape = (
    np.sum(
        np.abs(
            actual - predicted
        )
    )
    /
    np.sum(
        np.abs(actual)
    )
) * 100

print(
    "\n========== FORECASTING RESULTS =========="
)

print(
    f"MAE  : {mae:.4f}"
)

print(
    f"RMSE : {rmse:.4f}"
)

print(
    f"WAPE : {wape:.2f}%"
)

print(
    "=========================================="
)
