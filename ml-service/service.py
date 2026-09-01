"""
Main entry point for ML intelligence service.
"""
import logging
from forecasting import DemandForecaster
from anomaly_engine import AnomalyDetectionEngine
from optimizer import AssetReallocationOptimizer

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [ML-SERVICE] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class MachineLearningService:
    def __init__(self):
        self.forecaster = DemandForecaster()
        self.anomaly_engine = AnomalyDetectionEngine()
        self.optimizer = AssetReallocationOptimizer()

    def run_pipeline(self, sites_data, equipment_data, historical_demand, telemetry_streams):
        logger.info("Running ML Intelligence Pipeline...")
        # 1. Demand Forecasts
        forecasts = self.forecaster.forecast_demand(historical_demand, days_ahead=14)
        logger.info(f"Generated {len(forecasts)} forecast horizons.")

        # 2. Anomaly Detection
        anomalies = []
        for eq_id, stream in telemetry_streams.items():
            anom = self.anomaly_engine.evaluate_telemetry_window(stream)
            anomalies.extend(anom)
        logger.info(f"Detected {len(anomalies)} anomalies across telemetry streams.")

        # 3. Asset Reallocations
        reallocations = self.optimizer.optimize_allocations(sites_data, equipment_data, forecasts)
        logger.info(f"Generated {len(reallocations)} asset reallocation plans.")

        return {
            'forecasts': forecasts,
            'anomalies': anomalies,
            'reallocations': reallocations
        }


if __name__ == '__main__':
    service = MachineLearningService()
    logger.info("ML Service is ready.")
