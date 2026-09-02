"""
Evaluation runner for Demand Forecasting and Anomaly Detection models.
"""
from evaluate_models import evaluate_demand_forecasting, evaluate_isolation_forest_and_rules

if __name__ == "__main__":
    evaluate_demand_forecasting()
    evaluate_isolation_forest_and_rules()
