"""
Unit tests for anomaly detection engine (Isolation Forest + Rule-Based Engine).
"""
import unittest
from anomaly_engine import AnomalyDetectionEngine


class TestAnomalyDetection(unittest.TestCase):

    def setUp(self):
        self.anomaly_engine = AnomalyDetectionEngine()

    def test_speeding_anomaly(self):
        window = [
            {'equipment_id': 'CAT-TEST-01', 'speed': 10.0, 'fuel_level': 80.0, 'idle_hours': 0.5},
            {'equipment_id': 'CAT-TEST-01', 'speed': 92.0, 'fuel_level': 79.5, 'idle_hours': 0.5}
        ]
        anomalies = self.anomaly_engine.evaluate_telemetry_window(window)
        self.assertTrue(any(a['anomaly_type'] == 'EXCESSIVE_SPEED' for a in anomalies))

    def test_rapid_fuel_drop_anomaly(self):
        window = [
            {'equipment_id': 'CAT-TEST-02', 'speed': 0.0, 'fuel_level': 80.0, 'idle_hours': 0.2},
            {'equipment_id': 'CAT-TEST-02', 'speed': 0.0, 'fuel_level': 61.0, 'idle_hours': 0.2}
        ]
        anomalies = self.anomaly_engine.evaluate_telemetry_window(window)
        self.assertTrue(any(a['anomaly_type'] == 'RAPID_FUEL_DROP' for a in anomalies))

    def test_isolation_forest_outlier(self):
        window = [
            {'equipment_id': 'CAT-TEST-03', 'speed': 8.0 + (i % 3), 'fuel_level': 75.0 - i * 0.2, 'idle_hours': 0.3, 'engine_hours': 100 + i}
            for i in range(12)
        ]
        window.append({'equipment_id': 'CAT-TEST-03', 'speed': 45.0, 'fuel_level': 12.0, 'idle_hours': 2.8, 'engine_hours': 250.0})
        anomalies = self.anomaly_engine.evaluate_telemetry_window(window)
        self.assertTrue(any(a['anomaly_type'] == 'ML_TELEMETRY_OUTLIER' for a in anomalies))


if __name__ == '__main__':
    unittest.main()
