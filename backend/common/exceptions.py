"""
Custom exceptions for Smart Rental Tracking System backend.
"""
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


class APIError(APIException):
    """Base custom API error."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "An error occurred."
    default_code = "error"
    
    def __init__(self, detail=None, code=None, status_code=None):
        self.detail = detail or self.default_detail
        self.code = code or self.default_code
        if status_code is not None:
            self.status_code = status_code


class EquipmentNotFoundError(APIError):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Equipment not found."
    default_code = "EQUIPMENT_NOT_FOUND"


class EquipmentNotAvailableError(APIError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Equipment is not available for checkout."
    default_code = "EQUIPMENT_NOT_AVAILABLE"


class RentalNotFoundError(APIError):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Rental not found."
    default_code = "RENTAL_NOT_FOUND"


class InvalidRentalStateError(APIError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Invalid rental state transition."
    default_code = "INVALID_RENTAL_STATE"


class OperatorNotActiveError(APIError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Operator is not active."
    default_code = "OPERATOR_NOT_ACTIVE"


class SiteNotActiveError(APIError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Site is not active."
    default_code = "SITE_NOT_ACTIVE"


class InvalidTelemetryError(APIError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Invalid telemetry data."
    default_code = "INVALID_TELEMETRY"


class DuplicateTelemetryError(APIError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Telemetry event already processed."
    default_code = "DUPLICATE_TELEMETRY"


class PermissionDeniedError(APIError):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Permission denied."
    default_code = "PERMISSION_DENIED"


class InvalidIdentifierError(APIError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid identifier."
    default_code = "INVALID_IDENTIFIER"


def custom_exception_handler(exc, context):
    """
    Custom exception handler for consistent error response format.
    """
    response = drf_exception_handler(exc, context)
    
    if response is None:
        return None
    
    # Build custom response structure
    if isinstance(exc, APIError):
        data = {
            'success': False,
            'error': {
                'code': exc.code,
                'message': str(exc.detail),
                'details': {}
            }
        }
    else:
        # Handle standard DRF exceptions
        error_detail = response.data
        data = {
            'success': False,
            'error': {
                'code': exc.__class__.__name__,
                'message': str(error_detail.get('detail', 'An error occurred.')),
                'details': error_detail if isinstance(error_detail, dict) else {}
            }
        }
    
    response.data = data
    return response
