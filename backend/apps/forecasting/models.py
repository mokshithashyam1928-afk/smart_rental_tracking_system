"""
Forecasting, Anomaly Detection, and Recommendations apps (Phase 2).
"""
from django.db import models
from apps.equipment.models import Equipment
from apps.sites.models import Site


class Forecast(models.Model):
    """Model for demand forecasts (Phase 2)."""
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='forecasts')
    equipment_type = models.CharField(max_length=100)
    forecast_date = models.DateField()
    predicted_demand = models.FloatField()
    confidence = models.FloatField()
    model_version = models.CharField(max_length=50)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'forecasting_forecast'


class Anomaly(models.Model):
    """Model for equipment anomalies (Phase 2)."""
    SEVERITY_LOW = 'LOW'
    SEVERITY_MEDIUM = 'MEDIUM'
    SEVERITY_HIGH = 'HIGH'
    
    STATUS_OPEN = 'OPEN'
    STATUS_ACKNOWLEDGED = 'ACKNOWLEDGED'
    STATUS_RESOLVED = 'RESOLVED'
    STATUS_FALSE_POSITIVE = 'FALSE_POSITIVE'
    
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='anomalies')
    detected_at = models.DateTimeField()
    anomaly_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=20)
    score = models.FloatField()
    reason = models.TextField()
    status = models.CharField(max_length=20, default=STATUS_OPEN)
    metadata = models.JSONField(default=dict)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'anomaly_detection_anomaly'


class Recommendation(models.Model):
    """Model for equipment recommendations (Phase 2)."""
    STATUS_PENDING = 'PENDING'
    STATUS_ACCEPTED = 'ACCEPTED'
    STATUS_DISMISSED = 'DISMISSED'
    STATUS_EXPIRED = 'EXPIRED'
    
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='recommendations')
    source_site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='source_recommendations')
    target_site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='target_recommendations')
    reason = models.TextField()
    current_utilization = models.FloatField()
    predicted_target_demand = models.FloatField()
    score = models.FloatField()
    status = models.CharField(max_length=20, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    acted_at = models.DateTimeField(null=True, blank=True)
    acted_by = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        db_table = 'recommendations_recommendation'
