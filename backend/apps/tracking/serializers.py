"""
Serializers for tracking app.
"""
from rest_framework import serializers
from .models import DashboardMetrics
from apps.telemetry.serializers import EquipmentLiveStateSerializer


class DashboardMetricsSerializer(serializers.ModelSerializer):
    """Serializer for DashboardMetrics."""
    
    class Meta:
        model = DashboardMetrics
        fields = [
            'id', 'timestamp', 'total_equipment', 'available_equipment',
            'rented_equipment', 'in_use_equipment', 'idle_equipment',
            'maintenance_equipment', 'overdue_equipment', 'offline_equipment'
        ]
        read_only_fields = ['id', 'timestamp']


class DashboardSummarySerializer(serializers.Serializer):
    """Serializer for dashboard summary."""
    total = serializers.IntegerField()
    available = serializers.IntegerField()
    rented = serializers.IntegerField()
    in_use = serializers.IntegerField()
    idle = serializers.IntegerField()
    maintenance = serializers.IntegerField()
    overdue = serializers.IntegerField()
    offline = serializers.IntegerField()
