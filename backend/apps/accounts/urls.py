"""
URLs for accounts app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

app_name = 'accounts'

urlpatterns = [
    path('register/', AuthViewSet.as_view({'post': 'register'}), name='register'),
    path('login/', AuthViewSet.as_view({'post': 'login'}), name='login'),
    path('logout/', AuthViewSet.as_view({'post': 'logout'}), name='logout'),
    path('refresh/', AuthViewSet.as_view({'post': 'refresh'}), name='refresh'),
    path('me/', AuthViewSet.as_view({'get': 'me'}), name='me'),
    path('change-password/', AuthViewSet.as_view({'post': 'change_password'}), name='change-password'),
    path('', include(router.urls)),
]
