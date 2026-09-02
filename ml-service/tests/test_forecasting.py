"""
Unit tests for demand forecasting module.
"""
import unittest
from forecasting import DemandForecaster


class TestDemandForecasting(unittest.TestCase):

    def setUp(self):
        self.forecaster = DemandForecaster()

    def test_forecast_demand_generation(self):
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

    def test_demand_forecast_groups(self):
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


if __name__ == '__main__':
    unittest.main()
