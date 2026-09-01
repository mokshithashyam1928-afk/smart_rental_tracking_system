"""
Forecasting views (Phase 2).
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from common.permissions import CanViewAnalytics
from common.responses import APIResponse


class ForecastingViewSet(viewsets.ViewSet):
    """ViewSet for forecasting (Phase 2)."""
    permission_classes = [IsAuthenticated, CanViewAnalytics]
    
    def list(self, request):
        return APIResponse.success(
            data={},
            message='Forecasting will be available in Phase 2'
        )
