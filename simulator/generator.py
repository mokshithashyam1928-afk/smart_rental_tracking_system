"""
Telemetry generator for generating realistic IoT telemetry streams.
"""
import math
import random
import uuid
from datetime import datetime, timezone


class TelemetryGenerator:
    """Generates continuous realistic telemetry for a single equipment unit."""

    def __init__(self, machine_config: dict, site_config: dict):
        self.machine_config = machine_config
        self.site_config = site_config
        self.equipment_id = machine_config['equipment_id']
        self.operator_id = machine_config.get('operator_id')
        self.mode = machine_config.get('mode', 'NORMAL')

        self.current_lat = site_config['center_lat'] + random.uniform(-0.005, 0.005)
        self.current_lng = site_config['center_lng'] + random.uniform(-0.005, 0.005)
        self.engine_hours = float(random.randint(120, 850))
        self.idle_hours = float(random.randint(15, 60))
        self.fuel_level = float(machine_config.get('base_fuel', 80.0))
        self.total_fuel_consumed = 0.0
        self.tick_count = 0
        self.heading = random.uniform(0, 360)

    def next_telemetry(self) -> dict:
        """Produce the next telemetry data point based on operational mode."""
        self.tick_count += 1
        now_iso = datetime.now(timezone.utc).isoformat()
        event_id = f"SIM-{self.equipment_id}-{uuid.uuid4().hex[:8]}"

        # Base behavior
        is_active = random.random() > 0.35
        speed = 0.0

        if self.mode == 'EXCESSIVE_IDLE':
            is_active = False
            speed = 0.0
            self.idle_hours += 0.05
            self.engine_hours += 0.05
            self.fuel_level = max(5.0, self.fuel_level - 0.02)
            self.total_fuel_consumed += 0.02

        elif self.mode == 'SPEEDING' and self.tick_count % 8 == 0:
            # Trigger high speed anomaly (> 85 km/h)
            speed = round(random.uniform(85.0, 95.0), 1)
            self.engine_hours += 0.02
            self.fuel_level = max(5.0, self.fuel_level - 0.15)
            self.total_fuel_consumed += 0.15

        elif self.mode == 'FUEL_SIPHON' and self.tick_count == 5:
            # Sudden 18% fuel siphon drop
            self.fuel_level = max(2.0, self.fuel_level - 18.5)
            speed = 0.0
            self.idle_hours += 0.01

        elif is_active:
            max_spd = self.machine_config.get('max_speed', 20.0)
            speed = round(random.uniform(max_spd * 0.4, max_spd * 0.85), 1)
            self.engine_hours += 0.03
            fuel_burn = self.machine_config.get('burn_rate_per_min', 0.15) * 0.2
            self.fuel_level = max(5.0, self.fuel_level - fuel_burn)
            self.total_fuel_consumed += fuel_burn

            # Move lat/lng slightly along heading
            self.heading += random.uniform(-25, 25)
            rad = math.radians(self.heading)
            # ~0.0001 deg is approx 11 meters
            step = (speed / 3600.0) * 0.01
            self.current_lat += step * math.cos(rad)
            self.current_lng += step * math.sin(rad)
        else:
            speed = 0.0
            self.idle_hours += 0.02
            self.engine_hours += 0.02
            self.fuel_level = max(5.0, self.fuel_level - 0.01)
            self.total_fuel_consumed += 0.01

        return {
            'event_id': event_id,
            'equipment_id': self.equipment_id,
            'timestamp': now_iso,
            'latitude': round(self.current_lat, 6),
            'longitude': round(self.current_lng, 6),
            'engine_hours': round(self.engine_hours, 2),
            'idle_hours': round(self.idle_hours, 2),
            'fuel_level': round(self.fuel_level, 2),
            'fuel_consumed': round(self.total_fuel_consumed, 2),
            'speed': round(speed, 2),
            'operator_id': self.operator_id,
        }
