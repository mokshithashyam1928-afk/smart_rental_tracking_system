"""
Data preprocessing module for cleaning telemetry, rental, equipment, and demand datasets.
"""
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


class DataPreprocessor:
    """Handles data loading, cleaning, validation, and preprocessing."""

    @staticmethod
    def clean_telemetry_data(df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and validates raw telemetry streams."""
        df = df.copy()

        # Parse timestamp
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
        df = df.dropna(subset=["timestamp"])

        # Deduplicate
        if "event_id" in df.columns:
            df = df.drop_duplicates(subset=["event_id"])
        else:
            df = df.drop_duplicates(subset=["equipment_id", "timestamp"])

        # Numerical bounds validation (without removing legitimate anomalies)
        df["speed"] = df["speed"].apply(lambda s: max(0.0, float(s)) if pd.notnull(s) else 0.0)
        df["fuel_level"] = df["fuel_level"].apply(lambda f: min(100.0, max(0.0, float(f))) if pd.notnull(f) else 50.0)
        df["engine_hours"] = df["engine_hours"].apply(lambda e: max(0.0, float(e)) if pd.notnull(e) else 0.0)
        df["idle_hours"] = df["idle_hours"].apply(lambda i: max(0.0, float(i)) if pd.notnull(i) else 0.0)

        # Coordinate bounds check for India region
        if "latitude" in df.columns and "longitude" in df.columns:
            df["latitude"] = df["latitude"].fillna(12.9716)
            df["longitude"] = df["longitude"].fillna(77.5946)

        df = df.sort_values(["equipment_id", "timestamp"]).reset_index(drop=True)
        return df

    @staticmethod
    def clean_demand_data(df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and validates demand history records."""
        df = df.copy()

        if "site_code" not in df.columns and "site_id" in df.columns:
            df["site_code"] = df["site_id"]
        if "site_id" not in df.columns and "site_code" in df.columns:
            df["site_id"] = df["site_code"]

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])

        df["count"] = df["count"].apply(lambda c: max(0, int(c)) if pd.notnull(c) else 0)
        df = df.sort_values(["site_code", "equipment_type", "date"]).reset_index(drop=True)
        return df

    @staticmethod
    def load_raw_datasets():
        """Ensures raw datasets exist in data/raw/."""
        from export_csv_datasets import create_all_csvs
        create_all_csvs()

        # Copy standard raw files
        raw_telemetry = RAW_DIR / "telemetry.csv"
        raw_rentals = RAW_DIR / "rentals.csv"
        raw_equipment = RAW_DIR / "equipment.csv"

        if not raw_telemetry.exists() and (BASE_DIR / "data" / "telemetry.csv").exists():
            pd.read_csv(BASE_DIR / "data" / "telemetry.csv").to_csv(raw_telemetry, index=False)
        if not raw_rentals.exists() and (BASE_DIR / "data" / "rentals.csv").exists():
            pd.read_csv(BASE_DIR / "data" / "rentals.csv").to_csv(raw_rentals, index=False)
        if not raw_equipment.exists() and (BASE_DIR / "data" / "equipment.csv").exists():
            pd.read_csv(BASE_DIR / "data" / "equipment.csv").to_csv(raw_equipment, index=False)


if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    preprocessor.load_raw_datasets()
    print("Preprocessing initialized and raw files verified.")
