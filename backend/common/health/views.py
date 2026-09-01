"""
Health check views for Smart Rental Tracking System backend.
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis
from rest_framework import status


def liveness_check(request):
    """Liveness probe - application is running."""
    return JsonResponse({
        'status': 'alive',
        'service': 'smart-rental-tracking-backend'
    }, status=status.HTTP_200_OK)


def readiness_check(request):
    """Readiness probe - all dependencies are available."""
    checks = {
        'database': False,
        'redis': False,
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks['database'] = True
    except Exception as e:
        checks['database'] = str(e)
    
    # Check Redis
    try:
        cache.set('readiness_check', 'ok', 1)
        cache.get('readiness_check')
        checks['redis'] = True
    except Exception as e:
        checks['redis'] = str(e)
    
    all_ok = all(v is True for v in checks.values())
    status_code = status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JsonResponse({
        'status': 'ready' if all_ok else 'not_ready',
        'checks': checks
    }, status=status_code)
