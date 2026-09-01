"""
Custom pagination for Smart Rental Tracking System backend.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    page_size_query_description = 'Number of results per page'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'data': data,
            'pagination': {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'page': self.page.number,
                'page_size': self.page_size,
                'total_pages': self.page.paginator.num_pages,
            }
        })


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class TelemetryPagination(PageNumberPagination):
    """Pagination for telemetry with optional time-based filtering."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500
