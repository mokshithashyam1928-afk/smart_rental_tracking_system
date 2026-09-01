"""
URLs for rentals app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RentalViewSet

router = DefaultRouter()
router.register(r'', RentalViewSet, basename='rental')

app_name = 'rentals'

urlpatterns = [
    path('', include(router.urls)),
]
