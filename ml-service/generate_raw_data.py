"""Generate synthetic raw datasets for ML model training."""
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

SITES = ["S-CAT-BLR01", "S-CAT-HYD02", "S-CAT-MUM03", "S-CAT-KOL04", "S-CAT-DEL05"]
EQUIPMENT_TYPES = ["EXCAVATOR", "BULLDOZER", "WHEEL_LOADER", "DUMP_TRUCK", "COMPACTOR", "CRANE", "GENERATOR"]


def generate_demand_history(output_path=RAW_DIR / "rental_demand_history.csv"):
    random.seed(42)
    start_date = datetime.now() - timedelta(days=180)
    records = []

    for site in SITES:
        for eq_type in EQUIPMENT_TYPES:
            base_demand = random.randint(2, 8)
            for day_offset in range(180):
                current_date = start_date + timedelta(days=day_offset)
                is_weekend = current_date.weekday() >= 5
                noise = random.randint(-1, 2)
                factor = 0.6 if is_weekend else 1.0
                count = max(0, int((base_demand + noise) * factor))
                
                records.append({
                    "site_code": site,
                    "site_id": site,
                    "equipment_type": eq_type,
                    "date": current_date.strftime("%Y-%m-%d"),
                    "count": count
                })

    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} demand history records at {output_path}")
    return df


def generate_telemetry_history(output_path=RAW_DIR / "telemetry_history.csv"):
    random.seed(42)
    equipment_ids = [f"CAT-EQ-{1001 + i}" for i in range(10)]
    records = []
    start_time = datetime.now() - timedelta(days=7)

    for eq_id in equipment_ids:
        lat = 12.9716 + random.uniform(-0.01, 0.01)
        lon = 77.5946 + random.uniform(-0.01, 0.01)
        engine = round(random.uniform(500, 2000), 1)
        idle = round(random.uniform(20, 100), 1)
        fuel = 95.0

        for h in range(7 * 24):
            timestamp = (start_time + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ")
            speed = round(random.uniform(0, 35), 1) if (h % 24) >= 7 and (h % 24) <= 18 else 0.0
            
            # Inject occasional anomalies
            if random.random() < 0.02:
                speed = 95.0
            elif random.random() < 0.02:
                fuel = max(5.0, fuel - 22.0)
            else:
                fuel = max(10.0, fuel - random.uniform(0.5, 2.5))

            if fuel < 20.0:
                fuel = 95.0  # Refuel

            engine += 0.8 if speed > 0 else 0.0
            idle += 0.2 if speed == 0 else 0.0

            records.append({
                "equipment_id": eq_id,
                "timestamp": timestamp,
                "latitude": lat + random.uniform(-0.001, 0.001),
                "longitude": lon + random.uniform(-0.001, 0.001),
                "engine_hours": round(engine, 1),
                "idle_hours": round(idle, 1),
                "fuel_level": round(fuel, 1),
                "speed": speed
            })

    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} telemetry history records at {output_path}")
    return df


if __name__ == "__main__":
    generate_demand_history()
    generate_telemetry_history()
