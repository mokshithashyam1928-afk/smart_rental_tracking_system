"""
Views for rentals app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Rental
from .serializers import (
    RentalSerializer, RentalCheckoutSerializer,
    RentalCheckinSerializer, RentalCancelSerializer, RentalHistorySerializer
)
from .services import RentalService
from common.permissions import CanManageRentals
from common.exceptions import (
    RentalNotFoundError, InvalidRentalStateError,
    EquipmentNotAvailableError, OperatorNotActiveError, SiteNotActiveError
)
from common.responses import APIResponse


class RentalViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for managing rentals."""
    queryset = Rental.objects.select_related('equipment', 'operator', 'site', 'created_by').all()
    serializer_class = RentalSerializer
    permission_classes = [IsAuthenticated, CanManageRentals]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'equipment', 'operator', 'site']
    search_fields = ['rental_reference', 'equipment__equipment_id', 'operator__employee_id']
    ordering_fields = ['created_at', 'due_at', 'rental_reference']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, CanManageRentals])
    def checkout(self, request):
        """Checkout equipment for rental."""
        serializer = RentalCheckoutSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                code='VALIDATION_ERROR',
                message='Invalid checkout request',
                details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            rental = RentalService.checkout_equipment(
                equipment_id=serializer.validated_data['equipment_id'],
                operator_id=serializer.validated_data['operator_id'],
                site_id=serializer.validated_data['site_id'],
                due_at=serializer.validated_data['due_at'],
                user=request.user
            )
            return APIResponse.created(
                data=RentalSerializer(rental).data,
                message='Equipment checked out successfully'
            )
        except (EquipmentNotAvailableError, OperatorNotActiveError, SiteNotActiveError) as e:
            return APIResponse.error(
                code=e.code,
                message=str(e.detail),
                status_code=e.status_code
            )
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, CanManageRentals])
    def checkin(self, request):
        """Check in rented equipment."""
        serializer = RentalCheckinSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                code='VALIDATION_ERROR',
                message='Invalid check-in request',
                details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            rental = RentalService.checkin_equipment(
                rental_id=serializer.validated_data['rental_id'],
                user=request.user
            )
            return APIResponse.success(
                data=RentalSerializer(rental).data,
                message='Equipment checked in successfully'
            )
        except (RentalNotFoundError, InvalidRentalStateError) as e:
            return APIResponse.error(
                code=e.code,
                message=str(e.detail),
                status_code=e.status_code
            )
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, CanManageRentals])
    def cancel(self, request):
        """Cancel a rental."""
        serializer = RentalCancelSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                code='VALIDATION_ERROR',
                message='Invalid cancellation request',
                details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            rental = RentalService.cancel_rental(
                rental_id=serializer.validated_data['rental_id'],
                user=request.user
            )
            return APIResponse.success(
                data=RentalSerializer(rental).data,
                message='Rental cancelled successfully'
            )
        except (RentalNotFoundError, InvalidRentalStateError) as e:
            return APIResponse.error(
                code=e.code,
                message=str(e.detail),
                status_code=e.status_code
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def history(self, request):
        """Get rental history for the current user or operator."""
        queryset = self.get_queryset()
        
        # Filter by created_by user if not admin
        if request.user.role != 'ADMIN':
            queryset = queryset.filter(created_by=request.user)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RentalHistorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = RentalHistorySerializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message='Rental history retrieved successfully'
        )

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, CanManageRentals])
    def qr_scan(self, request):
        """
        Unified atomic QR scan endpoint:
        - Takes vehicle QR code / registration number
        - If vehicle is in yard (AVAILABLE/IDLE) -> Automatically Check Out to specified/default operator & site
        - If vehicle is deployed (RENTED/ACTIVE/OVERDUE) -> Automatically Check In & return to yard
        """
        qr_code = request.data.get('qr_code', '').strip()
        if not qr_code:
            return APIResponse.error(
                code='VALIDATION_ERROR',
                message='QR code is required',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        cleaned_id = qr_code
        if ':' in cleaned_id:
            cleaned_id = cleaned_id.split(':', 1)[1].strip()
        
        from apps.equipment.models import Equipment
        from apps.equipment.serializers import EquipmentSerializer
        from apps.operators.models import Operator
        from apps.sites.models import Site
        from django.db.models import Q
        import datetime
        from django.utils import timezone
        
        equipment = Equipment.objects.filter(
            Q(qr_code=qr_code) |
            Q(qr_code=cleaned_id) |
            Q(equipment_id=qr_code) |
            Q(equipment_id=cleaned_id) |
            Q(serial_number=qr_code)
        ).first()
        
        if not equipment:
            return APIResponse.error(
                code='EQUIPMENT_NOT_FOUND',
                message=f'Vehicle with registration / QR "{qr_code}" not found in system.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Check active rental
        active_rental = Rental.objects.filter(
            equipment=equipment,
            status__in=[Rental.STATUS_CHECKED_OUT, Rental.STATUS_ACTIVE, Rental.STATUS_OVERDUE],
            checkin_at__isnull=True
        ).first()

        is_currently_checked_out = (
            active_rental is not None or
            equipment.status in [Equipment.STATUS_RENTED, Equipment.STATUS_IN_USE, Equipment.STATUS_OVERDUE]
        )

        if is_currently_checked_out:
            # 2nd Scan: Vehicle is deployed -> Automatically CHECK-IN
            if active_rental:
                rental = RentalService.checkin_equipment(rental_id=active_rental.id, user=request.user)
            else:
                rental = None
            
            equipment.status = Equipment.STATUS_AVAILABLE
            equipment.current_operator = None
            equipment.save()
            equipment.refresh_from_db()

            return APIResponse.success(
                data={
                    'action': 'CHECK_IN',
                    'equipment': EquipmentSerializer(equipment).data,
                    'rental': RentalSerializer(rental).data if rental else None,
                },
                message=f'Checked In: {equipment.equipment_id} returned and marked AVAILABLE'
            )
        else:
            # 1st Scan: Vehicle is in yard (AVAILABLE) -> Automatically CHECK-OUT
            operator_id = request.data.get('operator_id')
            site_id = request.data.get('site_id')
            due_hours = int(request.data.get('due_hours', 24))
            
            if operator_id:
                operator = Operator.objects.filter(id=operator_id).first()
            else:
                operator = Operator.objects.filter(status=Operator.STATUS_ACTIVE).first()
            
            if site_id:
                site = Site.objects.filter(id=site_id).first()
            elif equipment.site:
                site = equipment.site
            else:
                site = Site.objects.filter(status=Site.STATUS_ACTIVE).first()
            
            if not operator:
                return APIResponse.error(
                    code='OPERATOR_NOT_FOUND',
                    message='No active operator found for checkout assignment.',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            if not site:
                return APIResponse.error(
                    code='SITE_NOT_FOUND',
                    message='No active destination site found for checkout assignment.',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            due_at = timezone.now() + datetime.timedelta(hours=due_hours)
            
            rental = RentalService.checkout_equipment(
                equipment_id=equipment.id,
                operator_id=operator.id,
                site_id=site.id,
                due_at=due_at,
                user=request.user
            )
            equipment.refresh_from_db()

            return APIResponse.success(
                data={
                    'action': 'CHECK_OUT',
                    'equipment': EquipmentSerializer(equipment).data,
                    'rental': RentalSerializer(rental).data,
                },
                message=f'Checked Out: {equipment.equipment_id} dispatched to {site.name}'
            )
