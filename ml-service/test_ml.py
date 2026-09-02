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
        synthetic_history = [
            {'site_code': 'S1', 'equipment_type': 'EXCAVATOR', 'date': f'2026-08-{day:02d}', 'count': 3 + (day % 4)}
            for day in range(1, 16)
        ]
        forecasts = self.forecaster.forecast_demand(synthetic_history, days_ahead=7)
        self.assertEqual(len(forecasts), 7)
        for f in forecasts:
            self.assertEqual(f['site_code'], 'S1')
            self.assertEqual(f['equipment_type'], 'EXCAVATOR')
            self.assertGreater(f['predicted_demand'], 0)
            self.assertGreater(f['confidence'], 0.5)
            self.assertIn('model_family', f)

    def test_demand_forecast_groups_by_site_and_equipment(self):
        synthetic_history = []
        for day in range(1, 8):
            synthetic_history.extend([
                {'site_code': 'S1', 'equipment_type': 'EXCAVATOR', 'date': f'2026-08-{day:02d}', 'count': 2 + day % 2},
                {'site_code': 'S2', 'equipment_type': 'LOADER', 'date': f'2026-08-{day:02d}', 'count': 5 + day % 3},
            ])
        forecasts = self.forecaster.forecast_demand(synthetic_history, days_ahead=3)
        groups = {(f['site_code'], f['equipment_type']) for f in forecasts}
        self.assertEqual(groups, {('S1', 'EXCAVATOR'), ('S2', 'LOADER')})
        self.assertEqual(len(forecasts), 6)

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

    def test_isolation_forest_detects_telemetry_outlier(self):
        window = [
            {'equipment_id': 'CAT-TEST-03', 'speed': 8.0 + (i % 3), 'fuel_level': 75.0 - i * 0.2, 'idle_hours': 0.3, 'engine_hours': 100 + i}
            for i in range(12)
        ]
        window.append({'equipment_id': 'CAT-TEST-03', 'speed': 45.0, 'fuel_level': 12.0, 'idle_hours': 2.8, 'engine_hours': 250.0})
        anomalies = self.anomaly_engine.evaluate_telemetry_window(window)
        self.assertTrue(any(a['anomaly_type'] == 'ML_TELEMETRY_OUTLIER' for a in anomalies))

    def test_asset_reallocation_optimization(self):
        sites = [
            {'site_code': 'S1', 'name': 'Site 1'},
            {'site_code': 'S2', 'name': 'Site 2'}
        ]
        equipment = [
            {'equipment_id': 'EQ1', 'equipment_type': 'EXCAVATOR', 'site_code': 'S1', 'status': 'AVAILABLE'},
            {'equipment_id': 'EQ2', 'equipment_type': 'EXCAVATOR', 'site_code': 'S1', 'status': 'IDLE'}
        ]
        forecasts = [
            {'site_code': 'S2', 'equipment_type': 'EXCAVATOR', 'predicted_demand': 5.5, 'confidence': 0.9}
        ]
        reallocations = self.optimizer.optimize_allocations(sites, equipment, forecasts)
        self.assertGreaterEqual(len(reallocations), 1)
        self.assertEqual(reallocations[0]['equipment_id'], 'EQ1')
        self.assertEqual(reallocations[0]['target_site_code'], 'S2')


if __name__ == '__main__':
    unittest.main()
