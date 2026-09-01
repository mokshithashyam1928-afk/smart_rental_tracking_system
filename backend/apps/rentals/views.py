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
