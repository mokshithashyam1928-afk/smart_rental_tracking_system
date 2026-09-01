"""
Tracking app for dashboard and real-time monitoring.
"""
from django.db import models


class DashboardMetrics(models.Model):
    """Store dashboard metrics snapshots."""
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    total_equipment = models.IntegerField(default=0)
    available_equipment = models.IntegerField(default=0)
    rented_equipment = models.IntegerField(default=0)
    in_use_equipment = models.IntegerField(default=0)
    idle_equipment = models.IntegerField(default=0)
    maintenance_equipment = models.IntegerField(default=0)
    overdue_equipment = models.IntegerField(default=0)
    offline_equipment = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'tracking_dashboard_metrics'
        indexes = [
            models.Index(fields=['-timestamp']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Metrics at {self.timestamp}"
