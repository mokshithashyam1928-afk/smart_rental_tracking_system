"""
Custom validators for Smart Rental Tracking System backend.
"""
from django.core.exceptions import ValidationError
import re


class EquipmentIDValidator:
    """Validate equipment ID format."""
    pattern = r'^EQX[0-9]{4,}$'
    message = "Equipment ID must follow format: EQX followed by 4 or more digits."
    
    def __call__(self, value):
        if not re.match(self.pattern, value):
            raise ValidationError(self.message)


class OperatorIDValidator:
    """Validate operator ID format."""
    pattern = r'^OP[0-9]{3,}$'
    message = "Operator ID must follow format: OP followed by 3 or more digits."
    
    def __call__(self, value):
        if not re.match(self.pattern, value):
            raise ValidationError(self.message)


class SiteCodeValidator:
    """Validate site code format."""
    pattern = r'^S[0-9]{3,}$'
    message = "Site code must follow format: S followed by 3 or more digits."
    
    def __call__(self, value):
        if not re.match(self.pattern, value):
            raise ValidationError(self.message)


def validate_latitude(value):
    """Validate latitude is between -90 and 90."""
    if not -90 <= value <= 90:
        raise ValidationError("Latitude must be between -90 and 90.")


def validate_longitude(value):
    """Validate longitude is between -180 and 180."""
    if not -180 <= value <= 180:
        raise ValidationError("Longitude must be between -180 and 180.")


def validate_fuel_level(value):
    """Validate fuel level is between 0 and 100."""
    if not 0 <= value <= 100:
        raise ValidationError("Fuel level must be between 0 and 100.")


def validate_non_negative(value):
    """Validate value is non-negative."""
    if value < 0:
        raise ValidationError("This value must be non-negative.")


def validate_speed_range(value):
    """Validate speed is non-negative."""
    if value < 0:
        raise ValidationError("Speed cannot be negative.")
