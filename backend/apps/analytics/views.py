"""
Analytics views (Phase 2) for fleet utilization, idle statistics, fuel metrics, and CSV reporting.
"""
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from common.permissions import CanViewAnalytics
from common.responses import APIResponse
from .services import AnalyticsService
from .serializers import (
    AnalyticsOverviewSerializer,
    FleetUtilizationSerializer,
    IdleAnalyticsSerializer,
    FuelEfficiencySerializer,
    SiteBreakdownSerializer,
)


class AnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for fleet analytics and business intelligence."""
    permission_classes = [IsAuthenticated, CanViewAnalytics]

    def list(self, request):
        """Get full analytics dashboard overview."""
        data = AnalyticsService.get_overview()
        serializer = AnalyticsOverviewSerializer(data)
        return APIResponse.success(
            data=serializer.data,
            message='Analytics overview retrieved successfully'
        )

    @action(detail=False, methods=['get'])
    def utilization(self, request):
        """Get fleet utilization metrics."""
        site_id = request.query_params.get('site_id')
        data = AnalyticsService.get_fleet_utilization(site_id=site_id)
        serializer = FleetUtilizationSerializer(data)
        return APIResponse.success(
            data=serializer.data,
            message='Utilization metrics retrieved successfully'
        )

    @action(detail=False, methods=['get'])
    def idle(self, request):
        """Get idle statistics and estimated financial waste."""
        data = AnalyticsService.get_idle_analytics()
        serializer = IdleAnalyticsSerializer(data)
        return APIResponse.success(
            data=serializer.data,
            message='Idle statistics retrieved successfully'
        )

    @action(detail=False, methods=['get'])
    def fuel(self, request):
        """Get fuel consumption and efficiency by equipment type."""
        data = AnalyticsService.get_fuel_efficiency()
        serializer = FuelEfficiencySerializer(data)
        return APIResponse.success(
            data=serializer.data,
            message='Fuel efficiency analytics retrieved successfully'
        )

    @action(detail=False, methods=['get'])
    def breakdown(self, request):
        """Get site-wise utilization breakdown."""
        data = AnalyticsService.get_site_breakdowns()
        serializer = SiteBreakdownSerializer(data, many=True)
        return APIResponse.success(
            data=serializer.data,
            message='Site breakdown retrieved successfully'
        )

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export analytics data as CSV."""
        report_type = request.query_params.get('type', 'fleet')
        csv_data = AnalyticsService.export_csv_report(report_type=report_type)
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="analytics_{report_type}.csv"'
        return response
