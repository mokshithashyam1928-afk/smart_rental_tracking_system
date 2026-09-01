"""
URL configuration for Smart Rental Tracking System backend.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Health checks
    path('health/live/', include('common.health.urls')),
    
    # OpenAPI schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
    
    # API v1
    path('api/auth/', include('apps.accounts.urls', namespace='accounts')),
    path('api/equipment/', include('apps.equipment.urls', namespace='equipment')),
    path('api/sites/', include('apps.sites.urls', namespace='sites')),
    path('api/operators/', include('apps.operators.urls', namespace='operators')),
    path('api/rentals/', include('apps.rentals.urls', namespace='rentals')),
    path('api/telemetry/', include('apps.telemetry.urls', namespace='telemetry')),
    path('api/dashboard/', include('apps.tracking.urls', namespace='tracking')),
    path('api/notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('api/analytics/', include('apps.analytics.urls', namespace='analytics')),
    path('api/forecasting/', include('apps.forecasting.urls', namespace='forecasting')),
    path('api/anomalies/', include('apps.anomaly_detection.urls', namespace='anomalies')),
    path('api/recommendations/', include('apps.recommendations.urls', namespace='recommendations')),
    path('api/audit/', include('apps.audit.urls', namespace='audit')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
