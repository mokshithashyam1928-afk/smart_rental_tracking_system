"""
Operators app for managing certified heavy machinery operators.
Operators are industrial workers licensed to operate specific categories
of Caterpillar construction and mining equipment.
"""
from django.db import models


class Operator(models.Model):
    """
    Represents a certified Cat equipment operator assigned to job sites.
    Each operator has a unique employee ID, equipment category certifications,
    and tracks total engine hours operated across all machines.
    """

    STATUS_ACTIVE = 'ACTIVE'
    STATUS_INACTIVE = 'INACTIVE'
    STATUS_ON_LEAVE = 'ON_LEAVE'
    STATUS_SUSPENDED = 'SUSPENDED'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_ON_LEAVE, 'On Leave'),
        (STATUS_SUSPENDED, 'Suspended'),
    ]

    CERTIFICATION_CHOICES = [
        ('EXCAVATOR', 'Hydraulic Excavator Operator'),
        ('BULLDOZER', 'Track-Type Tractor / Dozer Operator'),
        ('WHEEL_LOADER', 'Wheel Loader Operator'),
        ('DUMP_TRUCK', 'Articulated Dump Truck Operator'),
        ('MOTOR_GRADER', 'Motor Grader Operator'),
        ('COMPACTOR', 'Compactor Operator'),
        ('CRANE', 'Crane / Telehandler Operator'),
        ('GENERATOR', 'Generator Set Operator'),
        ('MULTI', 'Multi-Equipment Certified'),
    ]

    # --- Identity ---
    employee_id = models.CharField(
        max_length=50, unique=True,
        help_text="Caterpillar employee ID, e.g. CAT-OP-1001"
    )
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    # --- Certification & Skills ---
    certification_type = models.CharField(
        max_length=50, choices=CERTIFICATION_CHOICES,
        default='MULTI', blank=True,
        help_text="Primary equipment category certification held by this operator"
    )
    license_number = models.CharField(
        max_length=100, blank=True,
        help_text="Government-issued heavy machinery operating license number"
    )
    license_expiry = models.DateField(
        null=True, blank=True,
        help_text="License expiry date — alerts triggered 30 days before expiry"
    )

    # --- Operational Stats ---
    total_engine_hours_operated = models.FloatField(
        default=0.0,
        help_text="Cumulative engine hours operated across all Cat machines"
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'operators_operator'
        verbose_name = 'Equipment Operator'
        verbose_name_plural = 'Equipment Operators'
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['status']),
            models.Index(fields=['certification_type']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee_id} — {self.name}"

    @property
    def is_license_valid(self):
        """Returns True if the operator license has not expired."""
        from django.utils import timezone
        if not self.license_expiry:
            return True
        return self.license_expiry >= timezone.now().date()
