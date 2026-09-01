"""
Sites app for managing Caterpillar construction and mining job sites.
Each site is a physical location where Cat equipment is deployed and tracked.
"""
from django.db import models


class Site(models.Model):
    """
    Represents a physical construction or mining job site where
    Caterpillar heavy equipment is deployed.

    Site coordinates (lat/lon) are used for geofencing — telemetry that
    reports GPS positions outside the site perimeter triggers an
    'unauthorized movement' anomaly alert.
    """

    STATUS_ACTIVE = 'ACTIVE'
    STATUS_INACTIVE = 'INACTIVE'
    STATUS_COMPLETED = 'COMPLETED'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_COMPLETED, 'Project Completed'),
    ]

    SITE_TYPE_CHOICES = [
        ('CONSTRUCTION', 'Construction Site'),
        ('MINING', 'Open-Cast Mining Site'),
        ('ROAD', 'Road / Highway Project'),
        ('TUNNEL', 'Tunneling / Underground Project'),
        ('MARINE', 'Marine / Port / Dredging Project'),
        ('QUARRY', 'Quarry / Aggregate Extraction'),
        ('DEPOT', 'Equipment Depot / Yard'),
    ]

    # --- Identity ---
    site_code = models.CharField(
        max_length=50, unique=True,
        help_text="Unique Caterpillar site code, e.g. S-CAT-BLR01"
    )
    name = models.CharField(
        max_length=255,
        help_text="Full project name, e.g. 'Bengaluru Metro Underground Line 4'"
    )
    site_type = models.CharField(
        max_length=30, choices=SITE_TYPE_CHOICES,
        default='CONSTRUCTION',
        help_text="Nature of the project at this site"
    )
    description = models.TextField(blank=True)
    address = models.CharField(max_length=500, blank=True)

    # --- Geolocation (center of site) ---
    latitude = models.FloatField(
        null=True, blank=True,
        help_text="Site centroid latitude — used for geofence boundary calculations"
    )
    longitude = models.FloatField(
        null=True, blank=True,
        help_text="Site centroid longitude — used for geofence boundary calculations"
    )
    geofence_radius_meters = models.PositiveIntegerField(
        default=2000,
        help_text="Radius in meters defining the site geofence boundary"
    )

    # --- Project Details ---
    project_manager = models.CharField(
        max_length=255, blank=True,
        help_text="Name of the Caterpillar project/site manager responsible"
    )
    client_name = models.CharField(
        max_length=255, blank=True,
        help_text="Client or contractor organization name"
    )
    project_start_date = models.DateField(null=True, blank=True)
    project_end_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sites_site'
        verbose_name = 'Job Site'
        verbose_name_plural = 'Job Sites'
        indexes = [
            models.Index(fields=['site_code']),
            models.Index(fields=['status']),
            models.Index(fields=['site_type']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.site_code} | {self.name}"
