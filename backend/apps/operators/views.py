"""
Views for operators app.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Operator
from .serializers import OperatorSerializer, OperatorCreateUpdateSerializer
from common.permissions import CanManageOperators
from common.responses import APIResponse


class OperatorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing operators."""
    queryset = Operator.objects.all()
    serializer_class = OperatorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['employee_id', 'name', 'phone', 'email']
    ordering_fields = ['created_at', 'name', 'employee_id']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action in ['create', 'update', 'partial_update']:
            return OperatorCreateUpdateSerializer
        return OperatorSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new operator."""
        permission_classes = [IsAuthenticated, CanManageOperators]
        for perm in permission_classes:
            if not perm().has_permission(request, self):
                return APIResponse.error(
                    code='PERMISSION_DENIED',
                    message='You do not have permission to create operators',
                    status_code=status.HTTP_403_FORBIDDEN
                )
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Update an operator."""
        permission_classes = [IsAuthenticated, CanManageOperators]
        for perm in permission_classes:
            if not perm().has_permission(request, self):
                return APIResponse.error(
                    code='PERMISSION_DENIED',
                    message='You do not have permission to update operators',
                    status_code=status.HTTP_403_FORBIDDEN
                )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Delete an operator."""
        permission_classes = [IsAuthenticated, CanManageOperators]
        for perm in permission_classes:
            if not perm().has_permission(request, self):
                return APIResponse.error(
                    code='PERMISSION_DENIED',
                    message='You do not have permission to delete operators',
                    status_code=status.HTTP_403_FORBIDDEN
                )
        return super().destroy(request, *args, **kwargs)
