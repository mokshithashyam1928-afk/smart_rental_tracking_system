"""
URLs for equipment app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EquipmentViewSet

router = DefaultRouter()
router.register(r'', EquipmentViewSet, basename='equipment')

app_name = 'equipment'

urlpatterns = [
    path('', include(router.urls)),
]
