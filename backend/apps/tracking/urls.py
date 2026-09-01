"""
URLs for tracking app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardViewSet, DashboardMetricsViewSet

router = DefaultRouter()
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'metrics', DashboardMetricsViewSet, basename='metrics')

app_name = 'tracking'

urlpatterns = [
    path('', include(router.urls)),
]
