"""
Equipment app for managing rental equipment assets.
"""
from django.db import models
from apps.sites.models import Site
from apps.operators.models import Operator


class Equipment(models.Model):
    """Model for equipment assets."""
    
    STATUS_AVAILABLE = 'AVAILABLE'
    STATUS_RENTED = 'RENTED'
    STATUS_IN_USE = 'IN_USE'
    STATUS_IDLE = 'IDLE'
    STATUS_MAINTENANCE = 'MAINTENANCE'
    STATUS_OVERDUE = 'OVERDUE'
    STATUS_OFFLINE = 'OFFLINE'
    
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_RENTED, 'Rented'),
        (STATUS_IN_USE, 'In Use'),
        (STATUS_IDLE, 'Idle'),
        (STATUS_MAINTENANCE, 'Maintenance'),
        (STATUS_OVERDUE, 'Overdue'),
        (STATUS_OFFLINE, 'Offline'),
    ]
    
    EQUIPMENT_TYPE_CHOICES = [
        ('EXCAVATOR', 'Excavator'),
        ('BULLDOZER', 'Bulldozer'),
        ('WHEEL_LOADER', 'Wheel Loader'),
        ('DUMP_TRUCK', 'Dump Truck'),
        ('CRANE', 'Crane'),
        ('COMPACTOR', 'Compactor'),
        ('GENERATOR', 'Generator'),
    ]
    
    equipment_id = models.CharField(max_length=50, unique=True)
    equipment_type = models.CharField(max_length=100, choices=EQUIPMENT_TYPE_CHOICES, default='EXCAVATOR')
    manufacturer = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True, unique=True, null=True)
    qr_code = models.CharField(max_length=255, unique=True, null=True, blank=True)
    rfid_uid = models.CharField(max_length=255, unique=True, null=True, blank=True)
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipment')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    current_operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipment')
    purchase_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'equipment_equipment'
        indexes = [
            models.Index(fields=['equipment_id']),
            models.Index(fields=['status']),
            models.Index(fields=['site']),
            models.Index(fields=['current_operator']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.equipment_id} - {self.equipment_type}"
    
    def is_available_for_checkout(self):
        """Check if equipment can be checked out."""
        return self.status in [self.STATUS_AVAILABLE, self.STATUS_IDLE]
