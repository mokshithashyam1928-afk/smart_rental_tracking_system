"""
Anomaly detection views (Phase 2).
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from common.permissions import CanViewAnalytics, CanManageRentals
from common.responses import APIResponse
from apps.forecasting.models import Anomaly
from .serializers import (
    AnomalySerializer,
    AnomalyAcknowledgeSerializer,
    AnomalyResolveSerializer,
    AnomalyScanSerializer
)
from .services import AnomalyDetectionService


class AnomalyViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for reviewing and resolving equipment anomalies."""
    queryset = Anomaly.objects.select_related('equipment', 'equipment__site').all()
    serializer_class = AnomalySerializer
    permission_classes = [IsAuthenticated, CanViewAnalytics]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['severity', 'status', 'anomaly_type', 'equipment']
    search_fields = ['equipment__equipment_id', 'anomaly_type', 'reason']
    ordering_fields = ['detected_at', 'score', 'severity']
    ordering = ['-detected_at']

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanManageRentals])
    def acknowledge(self, request, pk=None):
        """Acknowledge an anomaly."""
        serializer = AnomalyAcknowledgeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notes = serializer.validated_data.get('notes', '')

        try:
            anomaly = AnomalyDetectionService.acknowledge_anomaly(
                anomaly_id=pk,
                user=request.user,
                notes=notes
            )
            return APIResponse.success(
                data=AnomalySerializer(anomaly).data,
                message='Anomaly acknowledged successfully'
            )
        except Anomaly.DoesNotExist:
            return APIResponse.error(
                code='NOT_FOUND',
                message='Anomaly not found',
                status_code=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanManageRentals])
    def resolve(self, request, pk=None):
        """Resolve an anomaly."""
        serializer = AnomalyResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resolution_type = serializer.validated_data.get('resolution_type', Anomaly.STATUS_RESOLVED)
        notes = serializer.validated_data.get('notes', '')

        try:
            anomaly = AnomalyDetectionService.resolve_anomaly(
                anomaly_id=pk,
                user=request.user,
                resolution_type=resolution_type,
                notes=notes
            )
            return APIResponse.success(
                data=AnomalySerializer(anomaly).data,
                message='Anomaly resolved successfully'
            )
        except Anomaly.DoesNotExist:
            return APIResponse.error(
                code='NOT_FOUND',
                message='Anomaly not found',
                status_code=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def scan(self, request):
        """Trigger immediate telemetry scan across equipment for anomalies."""
        serializer = AnomalyScanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        equipment_id = serializer.validated_data.get('equipment_id')

        detected = AnomalyDetectionService.scan_for_anomalies(equipment_id=equipment_id)
        return APIResponse.success(
            data=AnomalySerializer(detected, many=True).data,
            message=f'Scan complete. {len(detected)} anomaly issues detected.'
        )
