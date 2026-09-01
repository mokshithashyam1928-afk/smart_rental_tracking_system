"""
Rentals app for managing equipment rental lifecycle.
"""
from django.db import models, transaction
from django.contrib.auth import get_user_model
from apps.equipment.models import Equipment
from apps.sites.models import Site
from apps.operators.models import Operator
from common.utilities import get_utc_now

User = get_user_model()


class Rental(models.Model):
    """Model for equipment rentals."""
    
    STATUS_CREATED = 'CREATED'
    STATUS_CHECKED_OUT = 'CHECKED_OUT'
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_CHECKED_IN = 'CHECKED_IN'
    STATUS_OVERDUE = 'OVERDUE'
    STATUS_CANCELLED = 'CANCELLED'
    
    STATUS_CHOICES = [
        (STATUS_CREATED, 'Created'),
        (STATUS_CHECKED_OUT, 'Checked Out'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_CHECKED_IN, 'Checked In'),
        (STATUS_OVERDUE, 'Overdue'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]
    
    rental_reference = models.CharField(max_length=50, unique=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, related_name='rentals')
    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, related_name='rentals')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='rentals')
    checkout_at = models.DateTimeField(null=True, blank=True)
    due_at = models.DateTimeField()
    checkin_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CREATED)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='rentals_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rentals_rental'
        indexes = [
            models.Index(fields=['rental_reference']),
            models.Index(fields=['equipment', 'status']),
            models.Index(fields=['operator']),
            models.Index(fields=['site']),
            models.Index(fields=['status']),
            models.Index(fields=['due_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.rental_reference} - {self.equipment.equipment_id}"
    
    def can_transition_to(self, new_status):
        """Check if rental can transition to the new status."""
        valid_transitions = {
            self.STATUS_CREATED: [self.STATUS_CHECKED_OUT, self.STATUS_CANCELLED],
            self.STATUS_CHECKED_OUT: [self.STATUS_ACTIVE, self.STATUS_CANCELLED],
            self.STATUS_ACTIVE: [self.STATUS_CHECKED_IN, self.STATUS_OVERDUE, self.STATUS_CANCELLED],
            self.STATUS_CHECKED_IN: [],
            self.STATUS_OVERDUE: [self.STATUS_CHECKED_IN],
            self.STATUS_CANCELLED: [],
        }
        return new_status in valid_transitions.get(self.status, [])
    
    def transition_to(self, new_status):
        """Transition rental to new status."""
        if not self.can_transition_to(new_status):
            raise ValueError(f"Cannot transition from {self.status} to {new_status}")
        self.status = new_status
        self.save()
    
    def is_overdue(self):
        """Check if rental is overdue."""
        if self.checkin_at:
            return False  # Already checked in
        return get_utc_now() > self.due_at
    
    def is_active(self):
        """Check if rental is currently active."""
        return self.status in [self.STATUS_CHECKED_OUT, self.STATUS_ACTIVE] and not self.is_overdue()
