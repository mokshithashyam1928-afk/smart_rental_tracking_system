"""
Forecasting views (Phase 2) for demand forecasts and ML predictions.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from common.permissions import CanViewAnalytics
from common.responses import APIResponse
from .models import Forecast
from .serializers import ForecastSerializer, ForecastGenerateSerializer
from .services import ForecastingService


class ForecastingViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for demand forecasting."""
    queryset = Forecast.objects.select_related('site').all()
    serializer_class = ForecastSerializer
    permission_classes = [IsAuthenticated, CanViewAnalytics]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['site', 'equipment_type', 'forecast_date']
    ordering_fields = ['forecast_date', 'predicted_demand', 'confidence']
    ordering = ['forecast_date']

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Trigger generation of new demand forecasts."""
        serializer = ForecastGenerateSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                code='VALIDATION_ERROR',
                message='Invalid generation parameters',
                details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        site_id = serializer.validated_data.get('site_id')
        days_ahead = serializer.validated_data.get('days_ahead', 14)
        forecasts = ForecastingService.generate_forecasts(site_id=site_id, days_ahead=days_ahead)

        return APIResponse.success(
            data=ForecastSerializer(forecasts[:20], many=True).data,
            message=f'Successfully generated {len(forecasts)} forecast data points.'
        )

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summarized forecast intelligence."""
        summary = ForecastingService.get_forecast_summary()
        return APIResponse.success(
            data=summary,
            message='Forecast summary retrieved successfully'
        )
