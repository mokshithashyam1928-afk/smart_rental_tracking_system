"""
Views for equipment app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Equipment
from .serializers import (
    EquipmentSerializer, EquipmentCreateUpdateSerializer,
    EquipmentStatusUpdateSerializer, EquipmentIdentifierResolutionSerializer
)
from common.permissions import CanManageEquipment, IsViewer
from common.exceptions import EquipmentNotFoundError
from common.responses import APIResponse


class EquipmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing equipment."""
    queryset = Equipment.objects.select_related('site', 'current_operator').all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated, IsViewer]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'equipment_type', 'site', 'current_operator']
    search_fields = ['equipment_id', 'manufacturer', 'model', 'serial_number']
    ordering_fields = ['created_at', 'equipment_id', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action in ['create', 'update', 'partial_update']:
            return EquipmentCreateUpdateSerializer
        return EquipmentSerializer
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, CanManageEquipment]
        return super().get_permissions()
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def resolve_identifier(self, request):
        """Resolve equipment by QR or RFID identifier."""
        serializer = EquipmentIdentifierResolutionSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                code='VALIDATION_ERROR',
                message='Invalid identifier resolution request',
                details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        identifier_type = serializer.validated_data['identifier_type']
        identifier = serializer.validated_data['identifier']
        
        try:
            if identifier_type == 'QR':
                equipment = Equipment.objects.get(qr_code=identifier)
            elif identifier_type == 'RFID':
                equipment = Equipment.objects.get(rfid_uid=identifier)
            else:
                raise EquipmentNotFoundError(detail='Unknown identifier type')
            
            return APIResponse.success(
                data=EquipmentSerializer(equipment).data,
                message='Equipment resolved successfully'
            )
        except Equipment.DoesNotExist:
            raise EquipmentNotFoundError(
                detail=f'Equipment with {identifier_type} identifier "{identifier}" not found'
            )
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, CanManageEquipment])
    def update_status(self, request, pk=None):
        """Update equipment status."""
        equipment = self.get_object()
        serializer = EquipmentStatusUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return APIResponse.error(
                code='VALIDATION_ERROR',
                message='Invalid status update request',
                details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        equipment.status = serializer.validated_data['status']
        equipment.save()
        
        return APIResponse.success(
            data=EquipmentSerializer(equipment).data,
            message='Equipment status updated successfully'
        )
