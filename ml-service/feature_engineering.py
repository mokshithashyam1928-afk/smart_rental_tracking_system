"""Feature engineering utilities for forecasting and anomaly models."""
from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def create_forecasting_features(df):
    """
    Create time-series features for demand forecasting.

    Required columns:
        date
        site_id or site_code
        equipment_type
        count
    """
    df = df.copy()
    if "site_id" not in df.columns and "site_code" in df.columns:
        df["site_id"] = df["site_code"]

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["site_id", "equipment_type", "date"]).reset_index(drop=True)

    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_month"] = df["date"].dt.day
    df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)
    df["month"] = df["date"].dt.month
    df["quarter"] = df["date"].dt.quarter
    df["year"] = df["date"].dt.year
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

    # ------------------------------------------------------------------
    # Lag features
    # ------------------------------------------------------------------
    group = df.groupby(["site_id", "equipment_type"])["count"]
    df["lag_1"] = group.shift(1)
    df["lag_7"] = group.shift(7)
    df["lag_14"] = group.shift(14)
    df["lag_30"] = group.shift(30)
    df["lag_60"] = group.shift(60)
    df["lag_90"] = group.shift(90)

    # ------------------------------------------------------------------
    # Rolling statistics (shifted by 1 to avoid leakage)
    # ------------------------------------------------------------------
    shifted = group.shift(1)
    shifted_group = shifted.groupby([df["site_id"], df["equipment_type"]])
    df["rolling_mean_7"] = shifted_group.transform(lambda x: x.rolling(7).mean())
    df["rolling_mean_14"] = shifted_group.transform(lambda x: x.rolling(14).mean())
    df["rolling_mean_30"] = shifted_group.transform(lambda x: x.rolling(30).mean())
    df["rolling_mean_60"] = shifted_group.transform(lambda x: x.rolling(60).mean())
    df["rolling_mean_90"] = shifted_group.transform(lambda x: x.rolling(90).mean())
    df["rolling_std_7"] = shifted_group.transform(lambda x: x.rolling(7).std())
    df["rolling_std_14"] = shifted_group.transform(lambda x: x.rolling(14).std())
    df["rolling_std_30"] = shifted_group.transform(lambda x: x.rolling(30).std())

    # ------------------------------------------------------------------
    # Site-level historical demand averages
    # ------------------------------------------------------------------
    site_stats = (
        df.groupby("site_id")["count"]
        .agg(site_mean_demand="mean", site_std_demand="std")
        .reset_index()
    )
    df = df.merge(site_stats, on="site_id", how="left")

    # ------------------------------------------------------------------
    # Indian public holiday indicator (fixed national holidays)
    # ------------------------------------------------------------------
    _PUBLIC_HOLIDAYS = {
        (1, 26),   # Republic Day
        (8, 15),   # Independence Day
        (10, 2),   # Gandhi Jayanti
        (12, 25),  # Christmas
        (11, 1),   # Kannada Rajyotsava (common in BLR sites)
    }
    df["is_holiday"] = df["date"].apply(
        lambda d: int((d.month, d.day) in _PUBLIC_HOLIDAYS)
    )

    # Fill initial missing lag/rolling values without dropping entire series
    df = df.bfill().fillna(0).reset_index(drop=True)
    return df


def create_anomaly_features(df):
    """
    Create ML features for Isolation Forest.

    Required columns:
        equipment_id
        timestamp
        latitude
        longitude
        engine_hours
        idle_hours
        fuel_level
        speed
    """
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values(["equipment_id", "timestamp"]).reset_index(drop=True)

    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["working_hour"] = (
        (df["hour"] >= 7)
        & (df["hour"] <= 18)
        & (df["day_of_week"] < 6)
    ).astype(int)

    group = df.groupby("equipment_id")
    df["fuel_drop_1h"] = -group["fuel_level"].diff()
    df["engine_increment_1h"] = group["engine_hours"].diff()
    df["idle_increment_1h"] = group["idle_hours"].diff()

    df["rolling_speed_6h"] = group["speed"].transform(
        lambda x: x.rolling(6, min_periods=1).mean()
    )
    df["rolling_speed_std_6h"] = group["speed"].transform(
        lambda x: x.rolling(6, min_periods=2).std()
    )

    df["latitude_change"] = group["latitude"].diff().abs()
    df["longitude_change"] = group["longitude"].diff().abs()

    df = df.replace([np.inf, -np.inf], np.nan)
    return df.fillna(0)


def build_forecasting_features(input_path=None, output_path=None) -> pd.DataFrame:
    """Load raw demand data, create forecasting features, and save processed CSV."""
    input_path = Path(input_path or PROCESSED_DIR / "forecasting_dataset.csv")
    if not input_path.exists():
        input_path = Path(RAW_DIR / "telemetry.csv")
    output_path = Path(output_path or PROCESSED_DIR / "forecasting_dataset.csv")

    df = pd.read_csv(input_path)
    required = {"date", "equipment_type", "count"}
    if "site_id" not in df.columns and "site_code" not in df.columns:
        required.add("site_id")
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing forecasting columns: {sorted(missing)}")

    features = create_forecasting_features(df)
    if "site_code" not in features.columns:
        features["site_code"] = features["site_id"]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_path, index=False)
    return features


def build_anomaly_features(input_path=None, output_path=None) -> pd.DataFrame:
    """Load raw telemetry data, create anomaly features, and save processed CSV."""
    input_path = Path(input_path or RAW_DIR / "telemetry.csv")
    output_path = Path(output_path or PROCESSED_DIR / "anomaly_dataset.csv")

    df = pd.read_csv(input_path)
    required = {
        "equipment_id",
        "timestamp",
        "latitude",
        "longitude",
        "engine_hours",
        "idle_hours",
        "fuel_level",
        "speed",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing telemetry columns: {sorted(missing)}")

    features = create_anomaly_features(df)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_path, index=False)
    return features



if __name__ == "__main__":
    build_forecasting_features()
    build_anomaly_features()
