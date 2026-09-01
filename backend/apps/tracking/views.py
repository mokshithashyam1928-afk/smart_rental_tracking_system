"""
Views for tracking app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DashboardMetrics
from .serializers import DashboardMetricsSerializer, DashboardSummarySerializer
from .services import DashboardService
from common.responses import APIResponse


class DashboardViewSet(viewsets.ViewSet):
    """ViewSet for dashboard endpoints."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get current equipment summary."""
        summary = DashboardService.get_equipment_summary()
        serializer = DashboardSummarySerializer(summary)
        return APIResponse.success(
            data=serializer.data,
            message='Dashboard summary retrieved successfully'
        )
    
    @action(detail=False, methods=['get'])
    def live_assets(self, request):
        """Get current live asset state."""
        live_assets = DashboardService.get_live_assets()
        from apps.telemetry.serializers import EquipmentLiveStateSerializer
        serializer = EquipmentLiveStateSerializer(live_assets, many=True)
        return APIResponse.success(
            data=serializer.data,
            message='Live assets retrieved successfully'
        )


class DashboardMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for dashboard metrics history."""
    queryset = DashboardMetrics.objects.all()
    serializer_class = DashboardMetricsSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
