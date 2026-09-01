"""
Services for telemetry processing.
"""
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.equipment.models import Equipment
from apps.operators.models import Operator
from .models import Telemetry, EquipmentLiveState
from common.exceptions import InvalidTelemetryError, DuplicateTelemetryError
from common.utilities import get_utc_now, get_time_difference_seconds


class TelemetryService:
    """Service for processing telemetry events."""
    
    @staticmethod
    def validate_telemetry_event(data):
        """
        Validate telemetry event data.
        
        Args:
            data: Dict with telemetry fields
        
        Returns:
            Validated data dict
        
        Raises:
            InvalidTelemetryError
        """
        required_fields = [
            'event_id', 'equipment_id', 'timestamp',
            'latitude', 'longitude', 'engine_hours', 'idle_hours',
            'fuel_level', 'speed'
        ]
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                raise InvalidTelemetryError(detail=f'Missing required field: {field}')
        
        # Validate numeric ranges
        try:
            latitude = float(data['latitude'])
            longitude = float(data['longitude'])
            engine_hours = float(data['engine_hours'])
            idle_hours = float(data['idle_hours'])
            fuel_level = float(data['fuel_level'])
            speed = float(data['speed'])
            
            if not -90 <= latitude <= 90:
                raise InvalidTelemetryError(detail='Latitude must be between -90 and 90')
            if not -180 <= longitude <= 180:
                raise InvalidTelemetryError(detail='Longitude must be between -180 and 180')
            if engine_hours < 0:
                raise InvalidTelemetryError(detail='Engine hours cannot be negative')
            if idle_hours < 0:
                raise InvalidTelemetryError(detail='Idle hours cannot be negative')
            if not 0 <= fuel_level <= 100:
                raise InvalidTelemetryError(detail='Fuel level must be between 0 and 100')
            if speed < 0:
                raise InvalidTelemetryError(detail='Speed cannot be negative')
        except (ValueError, TypeError) as e:
            raise InvalidTelemetryError(detail=f'Invalid numeric value: {str(e)}')
        
        return data
    
    @staticmethod
    @transaction.atomic
    def process_event(event_data):
        """
        Process a telemetry event.
        
        Args:
            event_data: Dict with telemetry data
        
        Returns:
            Telemetry object
        
        Raises:
            InvalidTelemetryError
            DuplicateTelemetryError
        """
        # Validate event
        validated_data = TelemetryService.validate_telemetry_event(event_data)
        
        event_id = validated_data['event_id']
        equipment_id = validated_data['equipment_id']
        
        # Check for duplicate event
        if Telemetry.objects.filter(event_id=event_id).exists():
            raise DuplicateTelemetryError(
                detail=f'Telemetry event {event_id} has already been processed'
            )
        
        # Get equipment
        try:
            equipment = Equipment.objects.get(equipment_id=equipment_id)
        except Equipment.DoesNotExist:
            raise InvalidTelemetryError(detail=f'Equipment {equipment_id} not found')
        
        # Get operator if provided
        operator = None
        if 'operator_id' in validated_data and validated_data['operator_id']:
            try:
                operator = Operator.objects.get(employee_id=validated_data['operator_id'])
            except Operator.DoesNotExist:
                pass  # Optional field
        
        # Create telemetry record
        telemetry = Telemetry.objects.create(
            event_id=event_id,
            equipment=equipment,
            timestamp=validated_data['timestamp'],
            latitude=validated_data['latitude'],
            longitude=validated_data['longitude'],
            engine_hours=validated_data['engine_hours'],
            idle_hours=validated_data['idle_hours'],
            fuel_level=validated_data['fuel_level'],
            fuel_consumed=validated_data.get('fuel_consumed', 0),
            speed=validated_data['speed'],
            operator=operator
        )
        
        # Update or create live state
        live_state, created = EquipmentLiveState.objects.get_or_create(
            equipment=equipment,
            defaults={
                'status': equipment.status,
                'last_seen': telemetry.timestamp,
                'latitude': telemetry.latitude,
                'longitude': telemetry.longitude,
                'engine_hours': telemetry.engine_hours,
                'idle_hours': telemetry.idle_hours,
                'fuel_level': telemetry.fuel_level,
                'speed': telemetry.speed,
                'operator': operator
            }
        )
        
        if not created:
            live_state.status = equipment.status
            live_state.last_seen = telemetry.timestamp
            live_state.latitude = telemetry.latitude
            live_state.longitude = telemetry.longitude
            live_state.engine_hours = telemetry.engine_hours
            live_state.idle_hours = telemetry.idle_hours
            live_state.fuel_level = telemetry.fuel_level
            live_state.speed = telemetry.speed
            live_state.operator = operator
            live_state.save()
        
        return telemetry
    
    @staticmethod
    def get_equipment_latest_telemetry(equipment_id, limit=100):
        """Get latest telemetry for equipment."""
        try:
            equipment = Equipment.objects.get(equipment_id=equipment_id)
            return Telemetry.objects.filter(equipment=equipment).order_by('-timestamp')[:limit]
        except Equipment.DoesNotExist:
            return Telemetry.objects.none()
