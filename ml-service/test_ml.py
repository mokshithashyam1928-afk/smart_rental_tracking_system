"""
Deterministic unit tests for ML service components using synthetic fixtures.
"""
import unittest
from forecasting import DemandForecaster
from anomaly_engine import AnomalyDetectionEngine
from optimizer import AssetReallocationOptimizer


class TestMLService(unittest.TestCase):

    def setUp(self):
        self.forecaster = DemandForecaster()
        self.anomaly_engine = AnomalyDetectionEngine()
        self.optimizer = AssetReallocationOptimizer()

    def test_demand_forecast_generation(self):
        synthetic_history = [{'count': 3}, {'count': 4}, {'count': 5}, {'count': 4}, {'count': 6}]
        forecasts = self.forecaster.forecast_demand(synthetic_history, days_ahead=7)
        self.assertEqual(len(forecasts), 7)
        for f in forecasts:
            self.assertGreater(f['predicted_demand'], 0)
            self.assertGreater(f['confidence'], 0.5)

    def test_anomaly_detection_speeding(self):
        window = [
            {'equipment_id': 'CAT-TEST-01', 'speed': 10.0, 'fuel_level': 80.0, 'idle_hours': 0.5},
            {'equipment_id': 'CAT-TEST-01', 'speed': 92.0, 'fuel_level': 79.5, 'idle_hours': 0.5}
        ]
        anomalies = self.anomaly_engine.evaluate_telemetry_window(window)
        self.assertTrue(any(a['anomaly_type'] == 'EXCESSIVE_SPEED' for a in anomalies))

    def test_anomaly_detection_fuel_drop(self):
        window = [
            {'equipment_id': 'CAT-TEST-02', 'speed': 0.0, 'fuel_level': 80.0, 'idle_hours': 0.2},
            {'equipment_id': 'CAT-TEST-02', 'speed': 0.0, 'fuel_level': 61.0, 'idle_hours': 0.2}  # 19% drop
        ]
        anomalies = self.anomaly_engine.evaluate_telemetry_window(window)
        self.assertTrue(any(a['anomaly_type'] == 'RAPID_FUEL_DROP' for a in anomalies))

    def test_asset_reallocation_optimization(self):
        sites = [
            {'site_code': 'S1', 'name': 'Site 1'},
            {'site_code': 'S2', 'name': 'Site 2'}
        ]
        equipment = [
            {'equipment_id': 'EQ1', 'equipment_type': 'EXCAVATOR', 'site_code': 'S1', 'status': 'AVAILABLE'}
        ]
        forecasts = [
            {'site_code': 'S2', 'equipment_type': 'EXCAVATOR', 'predicted_demand': 5.5}
        ]
        reallocations = self.optimizer.optimize_allocations(sites, equipment, forecasts)
        self.assertEqual(len(reallocations), 1)
        self.assertEqual(reallocations[0]['equipment_id'], 'EQ1')
        self.assertEqual(reallocations[0]['target_site_code'], 'S2')


if __name__ == '__main__':
    unittest.main()
