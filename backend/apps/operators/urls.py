"""
URLs for operators app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OperatorViewSet

router = DefaultRouter()
router.register(r'', OperatorViewSet, basename='operator')

app_name = 'operators'

urlpatterns = [
    path('', include(router.urls)),
]
