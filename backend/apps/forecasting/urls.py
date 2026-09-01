"""
URLs for forecasting app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ForecastingViewSet

router = DefaultRouter()
router.register(r'', ForecastingViewSet, basename='forecasting')

app_name = 'forecasting'

urlpatterns = [
    path('', include(router.urls)),
]
