"""
Telemetry app for handling equipment sensor data and live state.
"""
from django.db import models
from apps.equipment.models import Equipment
from apps.operators.models import Operator
from common.validators import validate_latitude, validate_longitude, validate_fuel_level, validate_non_negative, validate_speed_range


class Telemetry(models.Model):
    """Model for equipment telemetry data."""
    
    event_id = models.CharField(max_length=255, unique=True, db_index=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, related_name='telemetry')
    timestamp = models.DateTimeField(db_index=True)
    latitude = models.FloatField(validators=[validate_latitude])
    longitude = models.FloatField(validators=[validate_longitude])
    engine_hours = models.FloatField(validators=[validate_non_negative])
    idle_hours = models.FloatField(validators=[validate_non_negative])
    fuel_level = models.FloatField(validators=[validate_fuel_level])
    fuel_consumed = models.FloatField(default=0, validators=[validate_non_negative])
    speed = models.FloatField(default=0, validators=[validate_speed_range])
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True, related_name='telemetry')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'telemetry_telemetry'
        indexes = [
            models.Index(fields=['equipment', 'timestamp']),
            models.Index(fields=['event_id']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.equipment.equipment_id} - {self.timestamp}"


class EquipmentLiveState(models.Model):
    """Model for current live state of equipment (real-time)."""
    
    equipment = models.OneToOneField(Equipment, on_delete=models.CASCADE, related_name='live_state', primary_key=True)
    status = models.CharField(max_length=20, default='OFFLINE')
    last_seen = models.DateTimeField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True, validators=[validate_latitude])
    longitude = models.FloatField(null=True, blank=True, validators=[validate_longitude])
    engine_hours = models.FloatField(null=True, blank=True)
    idle_hours = models.FloatField(null=True, blank=True)
    fuel_level = models.FloatField(null=True, blank=True, validators=[validate_fuel_level])
    speed = models.FloatField(null=True, blank=True)
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True, related_name='live_states')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'telemetry_equipment_live_state'
    
    def __str__(self):
        return f"{self.equipment.equipment_id} - {self.status}"
