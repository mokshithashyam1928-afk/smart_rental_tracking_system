"""Anomaly detection using Isolation Forest plus domain safety rules."""
from typing import Optional

import numpy as np
from sklearn.ensemble import IsolationForest


class AnomalyDetectionEngine:
    """Detects multi-variate telemetry anomalies on equipment operations."""

    def __init__(self, speed_threshold_kmh: float = 80.0, fuel_drop_threshold: float = 15.0):
        self.speed_threshold_kmh = speed_threshold_kmh
        self.fuel_drop_threshold = fuel_drop_threshold

    def evaluate_telemetry_window(self, telemetry_window: list) -> list:
        """
        Evaluates a window of telemetry data points for an asset and returns detected anomaly events.
        """
        if not telemetry_window:
            return []

        anomalies = []
        # Check latest telemetry point
        latest = telemetry_window[-1]
        equipment_id = latest.get('equipment_id', 'UNKNOWN')
        speed = float(latest.get('speed', 0.0))
        idle_hours = float(latest.get('idle_hours', 0.0))

        # 1. High Speed / Reckless Operation
        if speed > self.speed_threshold_kmh:
            anomalies.append({
                'equipment_id': equipment_id,
                'anomaly_type': 'EXCESSIVE_SPEED',
                'severity': 'HIGH',
                'score': round(min(1.0, 0.85 + (speed - self.speed_threshold_kmh) * 0.01), 2),
                'reason': f"Operating speed of {speed:.1f} km/h exceeds equipment safe limit of {self.speed_threshold_kmh:.1f} km/h."
            })

        # 2. Excessive Continuous Idling
        if idle_hours > 3.0:
            anomalies.append({
                'equipment_id': equipment_id,
                'anomaly_type': 'EXCESSIVE_IDLE',
                'severity': 'MEDIUM',
                'score': 0.76,
                'reason': f"Continuous idling of {idle_hours:.1f} hours detected without productive engine load."
            })

        # 3. Sudden Fuel Loss / Siphon
        if len(telemetry_window) >= 2:
            prev = telemetry_window[-2]
            f_prev = float(prev.get('fuel_level', 0.0))
            f_curr = float(latest.get('fuel_level', 0.0))
            drop = f_prev - f_curr
            if drop >= self.fuel_drop_threshold:
                anomalies.append({
                    'equipment_id': equipment_id,
                    'anomaly_type': 'RAPID_FUEL_DROP',
                    'severity': 'HIGH',
                    'score': 0.96,
                    'reason': f"Sudden fuel loss of {drop:.1f}% detected between consecutive readings. Potential fuel leak or theft."
                })

        # 4. Multivariate anomaly model for unusual combined telemetry behavior.
        model_anomaly = self._detect_isolation_forest_anomaly(telemetry_window)
        if model_anomaly:
            known_types = {item["anomaly_type"] for item in anomalies}
            if model_anomaly["anomaly_type"] not in known_types:
                anomalies.append(model_anomaly)

        return anomalies

    @staticmethod
    def _safe_float(row: dict, key: str, default: float = 0.0) -> float:
        try:
            return float(row.get(key, default) or default)
        except (TypeError, ValueError):
            return default

    def _detect_isolation_forest_anomaly(self, telemetry_window: list) -> Optional[dict]:
        if len(telemetry_window) < 8:
            return None

        features = np.array(
            [
                [
                    self._safe_float(row, "speed"),
                    self._safe_float(row, "fuel_level"),
                    self._safe_float(row, "idle_hours"),
                    self._safe_float(row, "engine_hours"),
                ]
                for row in telemetry_window
            ],
            dtype=float,
        )

        if np.std(features, axis=0).sum() == 0:
            return None

        model = IsolationForest(contamination="auto", random_state=42)
        labels = model.fit_predict(features)
        scores = -model.score_samples(features)

        latest_label = int(labels[-1])
        if latest_label != -1:
            return None

        latest = telemetry_window[-1]
        score = float(scores[-1])
        percentile = float(np.mean(scores <= score))
        severity = "HIGH" if percentile >= 0.95 else "MEDIUM"

        return {
            "equipment_id": latest.get("equipment_id", "UNKNOWN"),
            "anomaly_type": "ML_TELEMETRY_OUTLIER",
            "severity": severity,
            "score": round(min(0.99, max(0.60, percentile)), 2),
            "reason": "Telemetry pattern is unusual compared with the recent operating window.",
            "metadata": {
                "model": "IsolationForest",
                "speed": self._safe_float(latest, "speed"),
                "fuel_level": self._safe_float(latest, "fuel_level"),
                "idle_hours": self._safe_float(latest, "idle_hours"),
                "engine_hours": self._safe_float(latest, "engine_hours"),
            },
        }
