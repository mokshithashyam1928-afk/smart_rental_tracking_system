"""
Custom middleware for Smart Rental Tracking System backend.
"""
import uuid
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestIDMiddleware(MiddlewareMixin):
    """Add a unique request ID to each request for tracking."""
    
    def process_request(self, request):
        request.id = str(uuid.uuid4())
        return None
    
    def process_response(self, request, response):
        response['X-Request-ID'] = getattr(request, 'id', 'unknown')
        return response
