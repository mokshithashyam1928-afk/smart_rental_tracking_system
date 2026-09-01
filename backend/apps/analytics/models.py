"""
Analytics app (Phase 2).
"""
from django.db import models


class AnalyticsModel(models.Model):
    """Placeholder for analytics."""
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_analytics'
