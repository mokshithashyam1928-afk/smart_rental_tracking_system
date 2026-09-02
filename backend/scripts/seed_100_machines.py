"""
Seed script to register 100 authentic Caterpillar machines across all equipment categories,
with permanent unique QR codes, real job sites, certified operators, and real rental telemetry.
"""
import os
import sys
import django
import random
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.equipment.models import Equipment
from apps.sites.models import Site
from apps.operators.models import Operator
from apps.rentals.models import Rental
from apps.accounts.models import User
from django.utils import timezone

def seed_machines():
    sites = list(Site.objects.all())
    operators = list(Operator.objects.all())
    admin_user = User.objects.filter(role='ADMIN').first() or User.objects.first()

    cat_models = [
        ('EXCAVATOR', 'Cat 320 Next Gen Hydraulic Excavator', '320'),
        ('EXCAVATOR', 'Cat 323 Heavy Duty Excavator', '323'),
        ('EXCAVATOR', 'Cat 330 Hydraulic Excavator', '330'),
        ('EXCAVATOR', 'Cat 336 Smart Hydraulic Excavator', '336'),
        ('EXCAVATOR', 'Cat 349 Production Quarry Excavator', '349'),
        ('EXCAVATOR', 'Cat 352 Long Reach Excavator', '352'),
        ('EXCAVATOR', 'Cat 308 Mini Hydraulic Excavator', '308CR'),
        ('EXCAVATOR', 'Cat 315 Small Hydraulic Excavator', '315'),
        ('EXCAVATOR', 'Cat 374 Large Quarry Excavator', '374'),
        ('EXCAVATOR', 'Cat 395 High Production Mining Excavator', '395'),

        ('BULLDOZER', 'Cat D3 Medium Track Bulldozer', 'D3'),
        ('BULLDOZER', 'Cat D4 High Drive Crawler Dozer', 'D4'),
        ('BULLDOZER', 'Cat D5 Slope Work Track Bulldozer', 'D5'),
        ('BULLDOZER', 'Cat D6 Waste Handler Bulldozer', 'D6'),
        ('BULLDOZER', 'Cat D7 Heavy Duty Dozer', 'D7'),
        ('BULLDOZER', 'Cat D8T Mining & Earthmoving Dozer', 'D8T'),
        ('BULLDOZER', 'Cat D9 High Production Crawler Dozer', 'D9'),
        ('BULLDOZER', 'Cat D10T2 Heavy Quarry Track Dozer', 'D10T2'),
        ('BULLDOZER', 'Cat D11 Giant Surface Mining Dozer', 'D11'),

        ('WHEEL_LOADER', 'Cat 926M Compact Wheel Loader', '926M'),
        ('WHEEL_LOADER', 'Cat 930M High Lift Wheel Loader', '930M'),
        ('WHEEL_LOADER', 'Cat 938M Aggregates Loader', '938M'),
        ('WHEEL_LOADER', 'Cat 950 GC Utility Wheel Loader', '950GC'),
        ('WHEEL_LOADER', 'Cat 966M Medium Wheel Loader', '966M'),
        ('WHEEL_LOADER', 'Cat 972M High Performance Loader', '972M'),
        ('WHEEL_LOADER', 'Cat 980M Heavy Material Loader', '980M'),
        ('WHEEL_LOADER', 'Cat 988K Block Handler Loader', '988K'),
        ('WHEEL_LOADER', 'Cat 992K Large Mining Wheel Loader', '992K'),

        ('DUMP_TRUCK', 'Cat 725 Articulated Haul Truck', '725'),
        ('DUMP_TRUCK', 'Cat 730 Ejector Articulated Truck', '730'),
        ('DUMP_TRUCK', 'Cat 735 High Capacity Articulated Truck', '735'),
        ('DUMP_TRUCK', 'Cat 740 GC Heavy Articulated Dump Truck', '740GC'),
        ('DUMP_TRUCK', 'Cat 745 Extreme Terrain Articulated Truck', '745'),
        ('DUMP_TRUCK', 'Cat 770G Off-Highway Mining Truck', '770G'),
        ('DUMP_TRUCK', 'Cat 772G Quarry Off-Highway Hauler', '772G'),
        ('DUMP_TRUCK', 'Cat 777G Deep Pit Mining Dump Truck', '777G'),
        ('DUMP_TRUCK', 'Cat 785D Ultra Class Haul Truck', '785D'),
        ('DUMP_TRUCK', 'Cat 793F Large Mining Dump Truck', '793F'),

        ('MOTOR_GRADER', 'Cat 120 Precision Motor Grader', '120'),
        ('MOTOR_GRADER', 'Cat 140 Road Construction Grader', '140'),
        ('MOTOR_GRADER', 'Cat 150 All-Wheel Drive Grader', '150'),
        ('MOTOR_GRADER', 'Cat 160 High Precision Heavy Grader', '160'),
        ('MOTOR_GRADER', 'Cat 14M3 Mining Road Maintenance Grader', '14M3'),
        ('MOTOR_GRADER', 'Cat 16M3 Heavy Haul Road Grader', '16M3'),
        ('MOTOR_GRADER', 'Cat 18M3 Large Mining Grader', '18M3'),
        ('MOTOR_GRADER', 'Cat 24 Ultra-Heavy Mining Motor Grader', '24'),

        ('COMPACTOR', 'Cat CS11 GC Vibratory Soil Compactor', 'CS11GC'),
        ('COMPACTOR', 'Cat CS12 GC Road Bed Soil Compactor', 'CS12GC'),
        ('COMPACTOR', 'Cat CS56B Heavy Vibratory Soil Compactor', 'CS56B'),
        ('COMPACTOR', 'Cat CP56B Padfoot Heavy Soil Compactor', 'CP56B'),
        ('COMPACTOR', 'Cat CB2.5 Tandem Asphalt Roller', 'CB2.5'),
        ('COMPACTOR', 'Cat CB4.4 Vibratory Asphalt Compactor', 'CB4.4'),
        ('COMPACTOR', 'Cat CB10 Highway Asphalt Compactor', 'CB10'),
        ('COMPACTOR', 'Cat CW34 Pneumatic Multi-Tyre Compactor', 'CW34'),

        ('BACKHOE', 'Cat 416 Side Shift Backhoe Loader', '416'),
        ('BACKHOE', 'Cat 420 Heavy Hydraulic Backhoe Loader', '420'),
        ('BACKHOE', 'Cat 426F2 Construction Backhoe Loader', '426F2'),
        ('BACKHOE', 'Cat 430 High Breakout Force Backhoe', '430'),
        ('BACKHOE', 'Cat 450 Center Pivot Heavy Backhoe Loader', '450'),

        ('SKID_STEER', 'Cat 226D3 Compact Radial Lift Loader', '226D3'),
        ('SKID_STEER', 'Cat 242D3 Vertical Lift Skid Steer Loader', '242D3'),
        ('SKID_STEER', 'Cat 259D3 Compact Track Forestry Loader', '259D3'),
        ('SKID_STEER', 'Cat 262D3 High Flow Skid Steer Loader', '262D3'),
        ('SKID_STEER', 'Cat 299D3 High Production Track Loader', '299D3'),

        ('GENERATOR', 'Cat C3.3 Industrial Diesel Generator 33kVA', 'C3.3'),
        ('GENERATOR', 'Cat C7.1 Primary Power Diesel Generator 200kVA', 'C7.1'),
        ('GENERATOR', 'Cat C13 Heavy Duty Containerized Genset 400kVA', 'C13'),
        ('GENERATOR', 'Cat C18 Continuous Power Diesel Generator 700kVA', 'C18'),
        ('GENERATOR', 'Cat C27 Multi-Megawatt Prime Power Generator 1000kVA', 'C27'),
        ('GENERATOR', 'Cat C32 Heavy Industrial Power Module 1250kVA', 'C32'),
        ('GENERATOR', 'Cat 3512 Continuous Power Mining Genset 1500kVA', '3512'),
        ('GENERATOR', 'Cat 3516B Heavy Duty Power Module 2000kVA', '3516B'),

        ('CRANE', 'Cat TH255C Ultra Compact Telehandler 2.5T', 'TH255C'),
        ('CRANE', 'Cat TH357D Rough Terrain Heavy Telehandler 3.5T', 'TH357D'),
        ('CRANE', 'Cat TH408D High Reach Construction Telehandler 4T', 'TH408D'),
        ('CRANE', 'Cat TH514D 14-Meter Reach Heavy Telehandler 5T', 'TH514D'),
        ('CRANE', 'Cat TL642D Telescopic Material Handler', 'TL642D'),
        ('CRANE', 'Cat TL943D High Capacity Telescopic Forklift', 'TL943D'),
        ('CRANE', 'Cat TL1055D Heavy Rough Terrain Telehandler', 'TL1055D'),
        ('CRANE', 'Cat TL1255D 17-Meter High Reach Rough Terrain Crane', 'TL1255D'),
    ]

    Rental.objects.all().delete()
    Equipment.objects.all().delete()

    created_count = 0
    now = timezone.now()

    for i in range(1, 101):
        eq_type, model_name, code = cat_models[(i - 1) % len(cat_models)]
        unit_num = 1000 + i
        equipment_id = f"CAT-{code}-{unit_num}"
        serial_number = f"CAT0{code}{unit_num:05d}P"
        site = sites[i % len(sites)] if sites else None

        # 75 Available in Yard, 18 Active in Field, 7 Overdue
        if i <= 75:
            status = 'AVAILABLE'
        elif i <= 93:
            status = 'RENTED'
        else:
            status = 'RENTED'

        eq = Equipment.objects.create(
            equipment_id=equipment_id,
            equipment_type=eq_type,
            model=model_name,
            manufacturer='Caterpillar Inc.',
            serial_number=serial_number,
            qr_code=equipment_id,
            site=site,
            status=status,
        )

        if status == 'RENTED':
            operator = operators[i % len(operators)] if operators else None
            eq.current_operator = operator
            eq.save()

            if i > 93:
                # Overdue
                checkout_at = now - datetime.timedelta(hours=random.randint(28, 52))
                due_at = now - datetime.timedelta(hours=random.randint(2, 8))
                rental_status = 'OVERDUE'
            else:
                # Active in field
                checkout_at = now - datetime.timedelta(hours=random.randint(4, 24))
                due_at = now + datetime.timedelta(hours=random.randint(4, 72))
                rental_status = 'ACTIVE'

            Rental.objects.create(
                rental_reference=f"RNT-CAT{unit_num}",
                equipment=eq,
                operator=operator,
                site=site,
                checkout_at=checkout_at,
                due_at=due_at,
                status=rental_status,
                created_by=admin_user
            )

        created_count += 1

    print(f"Successfully registered {created_count} authentic Caterpillar machines!")
    print(f"Total Equipment: {Equipment.objects.count()}")
    print(f"Available in Yard: {Equipment.objects.filter(status='AVAILABLE').count()}")
    print(f"Rented / In Field: {Equipment.objects.filter(status='RENTED').count()}")
    print(f"Active & Overdue Rentals: {Rental.objects.count()}")

if __name__ == '__main__':
    seed_machines()
