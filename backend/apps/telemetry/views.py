"""
Views for telemetry app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Telemetry, EquipmentLiveState
from .serializers import TelemetrySerializer, TelemetryIngestSerializer, EquipmentLiveStateSerializer
from .services import TelemetryService
from common.exceptions import InvalidTelemetryError, DuplicateTelemetryError
from common.responses import APIResponse
from common.pagination import TelemetryPagination


class TelemetryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for reading telemetry data."""
    queryset = Telemetry.objects.all()
    serializer_class = TelemetrySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['equipment']
    ordering_fields = ['timestamp', 'created_at']
    ordering = ['-timestamp']
    pagination_class = TelemetryPagination
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def ingest(self, request):
        """Ingest telemetry event from equipment/MQTT."""
        serializer = TelemetryIngestSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                code='VALIDATION_ERROR',
                message='Invalid telemetry data',
                details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            telemetry = TelemetryService.process_event(serializer.validated_data)
            return APIResponse.created(
                data=TelemetrySerializer(telemetry).data,
                message='Telemetry event processed successfully'
            )
        except InvalidTelemetryError as e:
            return APIResponse.error(
                code='INVALID_TELEMETRY',
                message=str(e.detail),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        except DuplicateTelemetryError as e:
            return APIResponse.success(
                message=str(e.detail)
            )
        except Exception as e:
            return APIResponse.error(
                code='TELEMETRY_PROCESSING_ERROR',
                message=f'Error processing telemetry: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def latest(self, request):
        """Get latest telemetry for all equipment."""
        live_states = EquipmentLiveState.objects.select_related('equipment').all()
        serializer = EquipmentLiveStateSerializer(live_states, many=True)
        return APIResponse.success(
            data=serializer.data,
            message='Latest telemetry retrieved successfully'
        )


class EquipmentLiveStateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for reading equipment live state."""
    queryset = EquipmentLiveState.objects.select_related('equipment', 'operator').all()
    serializer_class = EquipmentLiveStateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['equipment']
