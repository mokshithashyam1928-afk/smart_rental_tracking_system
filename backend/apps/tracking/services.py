"""
Services for tracking and dashboard.
"""
from django.db.models import Count, Q
from apps.equipment.models import Equipment
from .models import DashboardMetrics


class DashboardService:
    """Service for dashboard metrics."""
    
    @staticmethod
    def get_equipment_summary():
        """Get summary of equipment by status."""
        equipment = Equipment.objects.all()
        
        return {
            'total': equipment.count(),
            'available': equipment.filter(status=Equipment.STATUS_AVAILABLE).count(),
            'rented': equipment.filter(status=Equipment.STATUS_RENTED).count(),
            'in_use': equipment.filter(status=Equipment.STATUS_IN_USE).count(),
            'idle': equipment.filter(status=Equipment.STATUS_IDLE).count(),
            'maintenance': equipment.filter(status=Equipment.STATUS_MAINTENANCE).count(),
            'overdue': equipment.filter(status=Equipment.STATUS_OVERDUE).count(),
            'offline': equipment.filter(status=Equipment.STATUS_OFFLINE).count(),
        }
    
    @staticmethod
    def get_live_assets():
        """Get current live state of all assets."""
        from apps.telemetry.models import EquipmentLiveState
        return EquipmentLiveState.objects.select_related('equipment', 'operator').all()
    
    @staticmethod
    def record_metrics_snapshot():
        """Record a snapshot of current metrics."""
        summary = DashboardService.get_equipment_summary()
        metrics = DashboardMetrics.objects.create(**summary)
        return metrics
