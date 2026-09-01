"""
Response utilities for Smart Rental Tracking System backend.
"""
from rest_framework.response import Response
from rest_framework import status


class APIResponse:
    """Helper class for consistent API responses."""
    
    @staticmethod
    def success(data=None, message="Success", status_code=status.HTTP_200_OK):
        """Return a successful response."""
        return Response({
            'success': True,
            'data': data,
            'message': message
        }, status=status_code)
    
    @staticmethod
    def created(data=None, message="Resource created successfully"):
        """Return a created response."""
        return APIResponse.success(data, message, status.HTTP_201_CREATED)
    
    @staticmethod
    def error(code, message, details=None, status_code=status.HTTP_400_BAD_REQUEST):
        """Return an error response."""
        return Response({
            'success': False,
            'error': {
                'code': code,
                'message': message,
                'details': details or {}
            }
        }, status=status_code)
