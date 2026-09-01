"""
URLs for anomaly detection app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnomalyViewSet

router = DefaultRouter()
router.register(r'', AnomalyViewSet, basename='anomaly')

app_name = 'anomaly_detection'

urlpatterns = [
    path('', include(router.urls)),
]
