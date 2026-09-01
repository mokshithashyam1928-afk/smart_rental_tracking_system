"""
URLs for telemetry app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TelemetryViewSet, EquipmentLiveStateViewSet

router = DefaultRouter()
router.register(r'', TelemetryViewSet, basename='telemetry')
router.register(r'live-state', EquipmentLiveStateViewSet, basename='live-state')

app_name = 'telemetry'

urlpatterns = [
    path('', include(router.urls)),
]
