from django.db import models
from django.db.models import Q
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

    def create(self, request, *args, **kwargs):
        """Create and register new equipment."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return APIResponse.created(
            data=EquipmentSerializer(instance).data,
            message="Equipment registered successfully"
        )
    
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
                cleaned_id = identifier.strip()
                # Strip common prefix formats if scanned from formatted QR (e.g., 'CAT:CAT-336-1001' or 'QR:...')
                if ':' in cleaned_id:
                    cleaned_id = cleaned_id.split(':', 1)[1].strip()
                
                equipment = Equipment.objects.filter(
                    models.Q(qr_code=identifier) |
                    models.Q(qr_code=cleaned_id) |
                    models.Q(equipment_id=identifier) |
                    models.Q(equipment_id=cleaned_id) |
                    models.Q(serial_number=identifier)
                ).first()
                if not equipment:
                    raise Equipment.DoesNotExist
            elif identifier_type == 'RFID':
                equipment = Equipment.objects.get(rfid_uid=identifier)
            else:
                raise EquipmentNotFoundError(detail='Unknown identifier type')
            
            # Check for active rental
            from apps.rentals.models import Rental
            from apps.rentals.serializers import RentalSerializer
            active_rental = Rental.objects.filter(
                equipment=equipment,
                status__in=[Rental.STATUS_CHECKED_OUT, Rental.STATUS_ACTIVE, Rental.STATUS_OVERDUE],
                checkin_at__isnull=True
            ).first()

            data = EquipmentSerializer(equipment).data
            data['active_rental'] = RentalSerializer(active_rental).data if active_rental else None

            return APIResponse.success(
                data=data,
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
