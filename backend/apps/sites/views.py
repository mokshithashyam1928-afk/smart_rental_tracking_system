"""
Views for sites app.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Site
from .serializers import SiteSerializer, SiteCreateUpdateSerializer
from common.permissions import CanManageSites
from common.responses import APIResponse


class SiteViewSet(viewsets.ModelViewSet):
    """ViewSet for managing sites."""
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['site_code', 'name', 'address']
    ordering_fields = ['created_at', 'name', 'site_code']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action in ['create', 'update', 'partial_update']:
            return SiteCreateUpdateSerializer
        return SiteSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new site."""
        permission_classes = [IsAuthenticated, CanManageSites]
        for perm in permission_classes:
            if not perm().has_permission(request, self):
                return APIResponse.error(
                    code='PERMISSION_DENIED',
                    message='You do not have permission to create sites',
                    status_code=status.HTTP_403_FORBIDDEN
                )
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Update a site."""
        permission_classes = [IsAuthenticated, CanManageSites]
        for perm in permission_classes:
            if not perm().has_permission(request, self):
                return APIResponse.error(
                    code='PERMISSION_DENIED',
                    message='You do not have permission to update sites',
                    status_code=status.HTTP_403_FORBIDDEN
                )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a site."""
        permission_classes = [IsAuthenticated, CanManageSites]
        for perm in permission_classes:
            if not perm().has_permission(request, self):
                return APIResponse.error(
                    code='PERMISSION_DENIED',
                    message='You do not have permission to delete sites',
                    status_code=status.HTTP_403_FORBIDDEN
                )
        return super().destroy(request, *args, **kwargs)
