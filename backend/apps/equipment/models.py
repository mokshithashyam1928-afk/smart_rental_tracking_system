"""
Equipment app for managing Caterpillar heavy machinery rental assets.
Covers construction and mining equipment including excavators, bulldozers,
dump trucks, wheel loaders, compactors, cranes, and diesel generators.
"""
from django.db import models
from apps.sites.models import Site
from apps.operators.models import Operator


class Equipment(models.Model):
    """
    Represents a single Caterpillar heavy machine tracked in the rental system.

    Each machine has a unique CAT equipment ID and serial number, is associated
    with a construction/mining job site, and has a live operational status.
    IoT telemetry (GPS, engine hours, fuel, speed) is ingested via MQTT and
    stored against this record.
    """

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
        (STATUS_MAINTENANCE, 'Under Maintenance'),
        (STATUS_OVERDUE, 'Overdue - Not Returned'),
        (STATUS_OFFLINE, 'Offline / No Signal'),
    ]

    # Caterpillar machine type categories
    EQUIPMENT_TYPE_CHOICES = [
        ('EXCAVATOR', 'Hydraulic Excavator'),
        ('BULLDOZER', 'Track-Type Tractor / Bulldozer'),
        ('WHEEL_LOADER', 'Wheel Loader'),
        ('DUMP_TRUCK', 'Articulated / Off-Highway Dump Truck'),
        ('MOTOR_GRADER', 'Motor Grader'),
        ('COMPACTOR', 'Vibratory Soil / Asphalt Compactor'),
        ('CRANE', 'Telehandler / Rough Terrain Crane'),
        ('GENERATOR', 'Diesel Generator Set'),
        ('SKID_STEER', 'Skid Steer Loader'),
        ('BACKHOE', 'Backhoe Loader'),
        ('PIPELAYER', 'Pipelayer'),
        ('SCRAPER', 'Elevating / Push-Pull Scraper'),
    ]

    # --- Identity ---
    equipment_id = models.CharField(
        max_length=50, unique=True,
        help_text="Unique CAT fleet asset ID, e.g. CAT-336-1001"
    )
    equipment_type = models.CharField(
        max_length=100, choices=EQUIPMENT_TYPE_CHOICES, default='EXCAVATOR'
    )
    manufacturer = models.CharField(
        max_length=100, default='Caterpillar Inc.',
        help_text="Always 'Caterpillar Inc.' for this system"
    )
    model = models.CharField(
        max_length=150, blank=True,
        help_text="Full Cat model name, e.g. 'Cat 336 Heavy Excavator'"
    )
    serial_number = models.CharField(
        max_length=100, blank=True, unique=True, null=True,
        help_text="Caterpillar PIN (Product Identification Number)"
    )

    # --- Telematics & Identification Hardware ---
    qr_code = models.CharField(
        max_length=255, unique=True, null=True, blank=True,
        help_text="QR code sticker value for field scanning and checkout"
    )
    rfid_uid = models.CharField(
        max_length=255, unique=True, null=True, blank=True,
        help_text="RFID tag UID attached to the machine frame"
    )
    telematics_device_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True,
        help_text="Cat Product Link / VisionLink device serial number"
    )

    # --- Operational Data ---
    site = models.ForeignKey(
        Site, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='equipment',
        help_text="Current assigned construction/mining job site"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE
    )
    current_operator = models.ForeignKey(
        Operator, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='equipment',
        help_text="Certified operator currently assigned to this machine"
    )

    # --- Asset Lifecycle ---
    purchase_date = models.DateField(null=True, blank=True)
    manufacture_year = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Year the machine was manufactured"
    )
    rated_payload_tonnes = models.FloatField(
        null=True, blank=True,
        help_text="Rated payload capacity in metric tonnes (for trucks/loaders)"
    )
    engine_model = models.CharField(
        max_length=100, blank=True,
        help_text="Cat engine model powering this machine, e.g. 'Cat C9.3B'"
    )
    maintenance_interval_hours = models.PositiveIntegerField(
        default=500,
        help_text="Preventive maintenance interval in engine hours (default 500h)"
    )
    last_maintenance_hours = models.FloatField(
        null=True, blank=True,
        help_text="Engine hours reading at last completed service"
    )
    notes = models.TextField(blank=True, help_text="Internal fleet notes")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'equipment_equipment'
        verbose_name = 'Caterpillar Equipment'
        verbose_name_plural = 'Caterpillar Equipment Fleet'
        indexes = [
            models.Index(fields=['equipment_id']),
            models.Index(fields=['status']),
            models.Index(fields=['equipment_type']),
            models.Index(fields=['site']),
            models.Index(fields=['current_operator']),
            models.Index(fields=['telematics_device_id']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.equipment_id} | {self.model or self.equipment_type}"

    def is_available_for_checkout(self):
        """Check if machine can be checked out for a job site assignment."""
        return self.status in [self.STATUS_AVAILABLE, self.STATUS_IDLE]

    def hours_until_maintenance(self, current_engine_hours: float) -> float:
        """Returns remaining engine hours before next preventive maintenance."""
        if self.last_maintenance_hours is None:
            return float(self.maintenance_interval_hours)
        return max(0.0, (self.last_maintenance_hours + self.maintenance_interval_hours) - current_engine_hours)

    def save(self, *args, **kwargs):
        """Auto-populate qr_code with equipment_id if not present."""
        if not self.qr_code and self.equipment_id:
            self.qr_code = self.equipment_id
        super().save(*args, **kwargs)
