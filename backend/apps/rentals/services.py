"""
Services for rental business logic.
"""
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Rental
from apps.equipment.models import Equipment
from apps.sites.models import Site
from apps.operators.models import Operator
from apps.audit.models import AuditLog
from common.exceptions import (
    EquipmentNotAvailableError, OperatorNotActiveError,
    SiteNotActiveError, InvalidRentalStateError, RentalNotFoundError
)
from common.utilities import get_utc_now
import uuid

User = get_user_model()


class RentalService:
    """Service for managing rental operations."""
    
    @staticmethod
    @transaction.atomic
    def checkout_equipment(equipment_id, operator_id, site_id, due_at, user):
        """
        Checkout equipment for rental.
        
        Args:
            equipment_id: Equipment ID to checkout
            operator_id: Operator ID performing checkout
            site_id: Site ID where rental occurs
            due_at: DateTime when rental is due
            user: User performing the action
        
        Returns:
            Rental object
        
        Raises:
            EquipmentNotAvailableError
            OperatorNotActiveError
            SiteNotActiveError
        """
        # Get and validate equipment
        try:
            equipment = Equipment.objects.select_for_update().get(id=equipment_id)
        except Equipment.DoesNotExist:
            raise EquipmentNotAvailableError(detail='Equipment not found')
        
        if not equipment.is_available_for_checkout():
            raise EquipmentNotAvailableError(
                detail=f'Equipment is not available for checkout (status: {equipment.status})'
            )
        
        # Check for conflicting active rentals
        active_rental = Rental.objects.filter(
            equipment=equipment,
            status__in=[Rental.STATUS_CHECKED_OUT, Rental.STATUS_ACTIVE],
            checkin_at__isnull=True
        ).first()
        if active_rental:
            raise EquipmentNotAvailableError(
                detail=f'Equipment already has an active rental: {active_rental.rental_reference}'
            )
        
        # Get and validate operator
        try:
            operator = Operator.objects.get(id=operator_id)
        except Operator.DoesNotExist:
            raise OperatorNotActiveError(detail='Operator not found')
        
        if operator.status != Operator.STATUS_ACTIVE:
            raise OperatorNotActiveError(
                detail=f'Operator {operator.employee_id} is not active'
            )
        
        # Get and validate site
        try:
            site = Site.objects.get(id=site_id)
        except Site.DoesNotExist:
            raise SiteNotActiveError(detail='Site not found')
        
        if site.status != Site.STATUS_ACTIVE:
            raise SiteNotActiveError(
                detail=f'Site {site.site_code} is not active'
            )
        
        # Create rental
        rental = Rental.objects.create(
            rental_reference=f'RNT-{uuid.uuid4().hex[:8].upper()}',
            equipment=equipment,
            operator=operator,
            site=site,
            checkout_at=get_utc_now(),
            due_at=due_at,
            status=Rental.STATUS_CHECKED_OUT,
            created_by=user
        )
        
        # Update equipment status
        equipment.status = Equipment.STATUS_RENTED
        equipment.current_operator = operator
        equipment.site = site
        equipment.save()
        
        # Create audit log
        AuditLog.objects.create(
            actor=user,
            action='CHECKOUT',
            entity_type='RENTAL',
            entity_id=rental.id,
            metadata={
                'rental_reference': rental.rental_reference,
                'equipment_id': equipment.equipment_id,
                'operator_id': operator.employee_id,
                'site_id': site.site_code
            }
        )
        
        return rental
    
    @staticmethod
    @transaction.atomic
    def checkin_equipment(rental_id, user):
        """
        Check in rented equipment.
        
        Args:
            rental_id: Rental ID to check in
            user: User performing the action
        
        Returns:
            Updated Rental object
        
        Raises:
            RentalNotFoundError
            InvalidRentalStateError
        """
        try:
            rental = Rental.objects.select_for_update().get(id=rental_id)
        except Rental.DoesNotExist:
            raise RentalNotFoundError(detail='Rental not found')
        
        # Validate rental status
        if rental.status not in [Rental.STATUS_CHECKED_OUT, Rental.STATUS_ACTIVE, Rental.STATUS_OVERDUE]:
            raise InvalidRentalStateError(
                detail=f'Cannot check in rental with status: {rental.status}'
            )
        
        # Update rental
        rental.checkin_at = get_utc_now()
        rental.status = Rental.STATUS_CHECKED_IN
        rental.save()
        
        # Update equipment status
        equipment = rental.equipment
        equipment.status = Equipment.STATUS_AVAILABLE
        equipment.current_operator = None
        equipment.save()
        
        # Create audit log
        AuditLog.objects.create(
            actor=user,
            action='CHECKIN',
            entity_type='RENTAL',
            entity_id=rental.id,
            metadata={
                'rental_reference': rental.rental_reference,
                'equipment_id': equipment.equipment_id,
                'checkout_at': rental.checkout_at.isoformat(),
                'checkin_at': rental.checkin_at.isoformat()
            }
        )
        
        return rental
    
    @staticmethod
    @transaction.atomic
    def cancel_rental(rental_id, user):
        """
        Cancel a rental.
        
        Args:
            rental_id: Rental ID to cancel
            user: User performing the action
        
        Returns:
            Cancelled Rental object
        
        Raises:
            RentalNotFoundError
            InvalidRentalStateError
        """
        try:
            rental = Rental.objects.select_for_update().get(id=rental_id)
        except Rental.DoesNotExist:
            raise RentalNotFoundError(detail='Rental not found')
        
        # Validate rental status
        if rental.status in [Rental.STATUS_CHECKED_IN, Rental.STATUS_CANCELLED]:
            raise InvalidRentalStateError(
                detail=f'Cannot cancel rental with status: {rental.status}'
            )
        
        # Update rental
        rental.status = Rental.STATUS_CANCELLED
        rental.save()
        
        # Update equipment status if still rented
        equipment = rental.equipment
        if equipment.status == Equipment.STATUS_RENTED:
            equipment.status = Equipment.STATUS_AVAILABLE
            equipment.current_operator = None
            equipment.save()
        
        # Create audit log
        AuditLog.objects.create(
            actor=user,
            action='CANCEL',
            entity_type='RENTAL',
            entity_id=rental.id,
            metadata={
                'rental_reference': rental.rental_reference,
                'equipment_id': equipment.equipment_id,
                'reason': 'Manual cancellation'
            }
        )
        
        return rental
