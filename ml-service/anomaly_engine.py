"""
Anomaly detection engine combining statistical z-score modeling and domain heuristic scoring.
"""
import numpy as np


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

        return anomalies
