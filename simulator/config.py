"""
Simulator configuration with machine profiles, sites, and simulation parameters.
"""
import os

MQTT_BROKER_HOST = os.getenv('MQTT_BROKER_HOST', 'localhost')
MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT', '1883'))
MQTT_TOPIC_PREFIX = os.getenv('MQTT_TOPIC_PREFIX', 'equipment/telemetry')

BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000/api/telemetry/ingest/')
SIMULATION_INTERVAL_SECONDS = float(os.getenv('SIMULATION_INTERVAL_SECONDS', '3.0'))

SITES = [
    {
        'site_code': 'S-BLR-01',
        'name': 'Bengaluru Metro Line 4 Construction',
        'center_lat': 12.9716,
        'center_lng': 77.5946,
        'radius_km': 1.5,
    },
    {
        'site_code': 'S-HYD-02',
        'name': 'Hyderabad Airport Expressway',
        'center_lat': 17.3850,
        'center_lng': 78.4867,
        'radius_km': 2.0,
    },
    {
        'site_code': 'S-MUM-03',
        'name': 'Mumbai Coastal Road Project',
        'center_lat': 18.9870,
        'center_lng': 72.8150,
        'radius_km': 1.2,
    }
]

SIMULATED_FLEET = [
    {
        'equipment_id': 'CAT-EXC-1001',
        'equipment_type': 'EXCAVATOR',
        'model': 'Cat 320 GC',
        'site_code': 'S-BLR-01',
        'operator_id': 'OP101',
        'base_fuel': 85.0,
        'burn_rate_per_min': 0.15,
        'max_speed': 5.5,
        'mode': 'NORMAL',
    },
    {
        'equipment_id': 'CAT-BLD-1002',
        'equipment_type': 'BULLDOZER',
        'model': 'Cat D6T XL',
        'site_code': 'S-BLR-01',
        'operator_id': 'OP102',
        'base_fuel': 90.0,
        'burn_rate_per_min': 0.22,
        'max_speed': 9.8,
        'mode': 'EXCESSIVE_IDLE',  # Machine with high idle hours
    },
    {
        'equipment_id': 'CAT-WHL-1003',
        'equipment_type': 'WHEEL_LOADER',
        'model': 'Cat 950M',
        'site_code': 'S-HYD-02',
        'operator_id': 'OP103',
        'base_fuel': 70.0,
        'burn_rate_per_min': 0.18,
        'max_speed': 38.0,
        'mode': 'NORMAL',
    },
    {
        'equipment_id': 'CAT-DMP-1004',
        'equipment_type': 'DUMP_TRUCK',
        'model': 'Cat 745 Articulated',
        'site_code': 'S-HYD-02',
        'operator_id': 'OP104',
        'base_fuel': 60.0,
        'burn_rate_per_min': 0.30,
        'max_speed': 55.0,
        'mode': 'SPEEDING',  # Generates speed burst anomaly
    },
    {
        'equipment_id': 'CAT-CRN-1005',
        'equipment_type': 'CRANE',
        'model': 'Cat TL1255D',
        'site_code': 'S-MUM-03',
        'operator_id': 'OP105',
        'base_fuel': 95.0,
        'burn_rate_per_min': 0.10,
        'max_speed': 15.0,
        'mode': 'FUEL_SIPHON',  # Simulates sudden fuel drop
    },
]
