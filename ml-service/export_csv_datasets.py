"""
Export standard dataset files in ml-service/data matching the required CSV schema:
1. anomaly_dataset.csv
2. equipment.csv
3. equipment_usage_log.csv
4. forecasting_dataset.csv
5. rentals.csv
6. sites.csv
7. telemetry.csv
"""
import random
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Domain Seeds
SITES_DATA = [
    {"site_code": "S-CAT-BLR01", "name": "Bengaluru Metro Underground Line 4", "latitude": 12.9716, "longitude": 77.5946, "status": "ACTIVE"},
    {"site_code": "S-CAT-HYD02", "name": "Hyderabad Airport Expressway Phase 3", "latitude": 17.3850, "longitude": 78.4867, "status": "ACTIVE"},
    {"site_code": "S-CAT-MUM03", "name": "Mumbai Coastal Road Reclamation", "latitude": 18.9870, "longitude": 72.8150, "status": "ACTIVE"},
    {"site_code": "S-CAT-KOL04", "name": "Raniganj Open-Cast Coal Mine", "latitude": 23.6200, "longitude": 87.1300, "status": "ACTIVE"},
    {"site_code": "S-CAT-DEL05", "name": "Delhi-Mumbai Expressway Bridge", "latitude": 28.4595, "longitude": 77.0266, "status": "ACTIVE"},
]

EQUIPMENT_MODELS = [
    {"type": "EXCAVATOR", "model": "Cat 320 GC Hydraulic Excavator", "rate": 150.0},
    {"type": "EXCAVATOR", "model": "Cat 336 Heavy Excavator", "rate": 220.0},
    {"type": "BULLDOZER", "model": "Cat D6T XL Track-Type Tractor", "rate": 180.0},
    {"type": "BULLDOZER", "model": "Cat D8T Heavy Crawler Dozer", "rate": 250.0},
    {"type": "WHEEL_LOADER", "model": "Cat 950M Medium Wheel Loader", "rate": 140.0},
    {"type": "WHEEL_LOADER", "model": "Cat 980M High-Lift Wheel Loader", "rate": 190.0},
    {"type": "DUMP_TRUCK", "model": "Cat 745 Articulated Mining Truck", "rate": 210.0},
    {"type": "DUMP_TRUCK", "model": "Cat 777G Off-Highway Haul Truck", "rate": 300.0},
    {"type": "COMPACTOR", "model": "Cat CS56B Vibratory Soil Compactor", "rate": 120.0},
    {"type": "CRANE", "model": "Cat TL1255D Heavy Duty Telehandler", "rate": 160.0},
]


def create_all_csvs():
    random.seed(42)

    # 1. sites.csv
    sites_df = pd.DataFrame(SITES_DATA)
    sites_df.to_csv(DATA_DIR / "sites.csv", index=False)
    print(f"Exported sites.csv ({len(sites_df)} rows)")

    # 2. equipment.csv
    equipment_records = []
    for idx, item in enumerate(EQUIPMENT_MODELS):
        site = SITES_DATA[idx % len(SITES_DATA)]
        eq_id = f"CAT-EQ-{1001 + idx}"
        status = "RENTED" if idx % 2 == 1 else "AVAILABLE"
        equipment_records.append({
            "equipment_id": eq_id,
            "equipment_type": item["type"],
            "model": item["model"],
            "serial_number": f"CAT000{idx+100}X",
            "site_code": site["site_code"],
            "status": status,
            "hourly_rate_usd": item["rate"]
        })
    equipment_df = pd.DataFrame(equipment_records)
    equipment_df.to_csv(DATA_DIR / "equipment.csv", index=False)
    print(f"Exported equipment.csv ({len(equipment_df)} rows)")

    # 3. rentals.csv
    rental_records = []
    for idx, eq in enumerate(equipment_records):
        checkout = datetime.now() - timedelta(days=random.randint(5, 45))
        due = checkout + timedelta(days=random.randint(10, 30))
        rental_records.append({
            "rental_reference": f"CAT-RNT-{10001 + idx}",
            "equipment_id": eq["equipment_id"],
            "equipment_type": eq["equipment_type"],
            "site_code": eq["site_code"],
            "checkout_at": checkout.strftime("%Y-%m-%d %H:%M:%S"),
            "due_at": due.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "ACTIVE" if due > datetime.now() else "COMPLETED"
        })
    rentals_df = pd.DataFrame(rental_records)
    rentals_df.to_csv(DATA_DIR / "rentals.csv", index=False)
    print(f"Exported rentals.csv ({len(rentals_df)} rows)")

    # 4. equipment_usage_log.csv
    usage_records = []
    for eq in equipment_records:
        start_date = datetime.now() - timedelta(days=60)
        curr_engine = random.randint(300, 1500)
        curr_idle = random.randint(40, 200)

        for day in range(60):
            d = start_date + timedelta(days=day)
            daily_ops = round(random.uniform(4.0, 9.5), 1)
            daily_idle = round(random.uniform(0.5, 2.5), 1)
            fuel = round(daily_ops * random.uniform(12.0, 18.0), 1)
            curr_engine += daily_ops
            curr_idle += daily_idle

            usage_records.append({
                "equipment_id": eq["equipment_id"],
                "date": d.strftime("%Y-%m-%d"),
                "operating_hours": daily_ops,
                "idle_hours": daily_idle,
                "total_engine_hours": round(curr_engine, 1),
                "total_idle_hours": round(curr_idle, 1),
                "fuel_consumed_liters": fuel
            })
    usage_df = pd.DataFrame(usage_records)
    usage_df.to_csv(DATA_DIR / "equipment_usage_log.csv", index=False)
    print(f"Exported equipment_usage_log.csv ({len(usage_df)} rows)")

    # 5. forecasting_dataset.csv
    forecast_records = []
    start_hist = datetime.now() - timedelta(days=120)
    for site in SITES_DATA:
        for eq_model in EQUIPMENT_MODELS:
            base_cnt = random.randint(2, 6)
            for day in range(120):
                d = start_hist + timedelta(days=day)
                is_wknd = d.weekday() >= 5
                cnt = max(0, int((base_cnt + random.randint(-1, 2)) * (0.6 if is_wknd else 1.0)))
                forecast_records.append({
                    "site_code": site["site_code"],
                    "equipment_type": eq_model["type"],
                    "date": d.strftime("%Y-%m-%d"),
                    "count": cnt
                })
    forecasting_df = pd.DataFrame(forecast_records)
    forecasting_df.to_csv(DATA_DIR / "forecasting_dataset.csv", index=False)
    print(f"Exported forecasting_dataset.csv ({len(forecasting_df)} rows)")

    # 6. telemetry.csv & 7. anomaly_dataset.csv
    telemetry_records = []
    anomaly_records = []
    start_tel = datetime.now() - timedelta(days=14)

    for eq in equipment_records:
        site = next(s for s in SITES_DATA if s["site_code"] == eq["site_code"])
        lat = site["latitude"]
        lon = site["longitude"]
        eng_h = random.uniform(400, 1800)
        idle_h = random.uniform(30, 150)
        fuel = 95.0

        for hour in range(14 * 24):
            t_stamp = (start_tel + timedelta(hours=hour)).strftime("%Y-%m-%dT%H:%M:%SZ")
            speed = round(random.uniform(5, 30), 1) if 7 <= (hour % 24) <= 18 else 0.0
            
            # Anomalies
            speed_anom = 0
            fuel_anom = 0
            idle_anom = 0

            if random.random() < 0.015 and speed > 0:
                speed = 94.5
                speed_anom = 1

            if random.random() < 0.015:
                fuel = max(5.0, fuel - 24.0)
                fuel_anom = 1
            else:
                fuel = max(10.0, fuel - random.uniform(0.5, 2.2))

            if fuel < 20.0:
                fuel = 95.0

            eng_h += 0.8 if speed > 0 else 0.0
            idle_h += 0.2 if speed == 0 else 0.0

            if (hour % 24) in [12, 13, 14, 15] and speed == 0 and random.random() < 0.02:
                idle_anom = 1

            telemetry_records.append({
                "equipment_id": eq["equipment_id"],
                "timestamp": t_stamp,
                "latitude": round(lat + random.uniform(-0.002, 0.002), 6),
                "longitude": round(lon + random.uniform(-0.002, 0.002), 6),
                "engine_hours": round(eng_h, 1),
                "idle_hours": round(idle_h, 1),
                "fuel_level": round(fuel, 1),
                "speed": speed
            })

            ml_score = round(random.uniform(0.1, 0.45) + 0.5 * max(speed_anom, fuel_anom, idle_anom), 3)
            anomaly_records.append({
                "equipment_id": eq["equipment_id"],
                "timestamp": t_stamp,
                "speed": speed,
                "fuel_level": round(fuel, 1),
                "idle_hours": round(idle_h, 1),
                "engine_hours": round(eng_h, 1),
                "excessive_speed": speed_anom,
                "rapid_fuel_drop": fuel_anom,
                "excessive_idle": idle_anom,
                "anomaly_score": ml_score,
                "is_anomaly": 1 if ml_score > 0.60 else 0
            })

    telemetry_df = pd.DataFrame(telemetry_records)
    telemetry_df.to_csv(DATA_DIR / "telemetry.csv", index=False)
    print(f"Exported telemetry.csv ({len(telemetry_df)} rows)")

    anomaly_df = pd.DataFrame(anomaly_records)
    anomaly_df.to_csv(DATA_DIR / "anomaly_dataset.csv", index=False)
    print(f"Exported anomaly_dataset.csv ({len(anomaly_df)} rows)")


if __name__ == "__main__":
    create_all_csvs()
