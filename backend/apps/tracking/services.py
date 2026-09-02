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
        """Get summary of equipment by status based on real registered data."""
        from apps.rentals.models import Rental
        from django.utils import timezone
        equipment = Equipment.objects.all()
        now = timezone.now()
        
        overdue_count = Rental.objects.filter(
            Q(status=Rental.STATUS_OVERDUE) |
            Q(status__in=[Rental.STATUS_ACTIVE, Rental.STATUS_CHECKED_OUT], due_at__lt=now, checkin_at__isnull=True)
        ).count()
        
        rented_count = equipment.filter(status__in=[Equipment.STATUS_RENTED, Equipment.STATUS_IN_USE]).count()
        available_count = equipment.filter(status=Equipment.STATUS_AVAILABLE).count()
        idle_count = equipment.filter(status=Equipment.STATUS_IDLE).count()
        
        return {
            'total': equipment.count(),
            'available': available_count,
            'rented': rented_count,
            'in_use': rented_count,
            'idle': idle_count,
            'maintenance': equipment.filter(status=Equipment.STATUS_MAINTENANCE).count(),
            'overdue': overdue_count,
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
