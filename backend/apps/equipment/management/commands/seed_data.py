"""
Management command to seed database with realistic Caterpillar heavy machinery test data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.sites.models import Site
from apps.operators.models import Operator
from apps.equipment.models import Equipment
from apps.rentals.models import Rental
from apps.telemetry.models import Telemetry, EquipmentLiveState
from apps.forecasting.models import Anomaly, Recommendation, Forecast
from faker import Faker
from datetime import datetime, timedelta
import random

User = get_user_model()
fake = Faker()

CAT_MODELS = [
    {'type': 'EXCAVATOR', 'model': 'Cat 320 GC Hydraulic Excavator', 'series': '320GC'},
    {'type': 'EXCAVATOR', 'model': 'Cat 336 Heavy Excavator', 'series': '336'},
    {'type': 'BULLDOZER', 'model': 'Cat D6T XL Track-Type Tractor', 'series': 'D6T'},
    {'type': 'BULLDOZER', 'model': 'Cat D8T Heavy Crawler Dozer', 'series': 'D8T'},
    {'type': 'WHEEL_LOADER', 'model': 'Cat 950M Medium Wheel Loader', 'series': '950M'},
    {'type': 'WHEEL_LOADER', 'model': 'Cat 980M High-Lift Wheel Loader', 'series': '980M'},
    {'type': 'DUMP_TRUCK', 'model': 'Cat 745 Articulated Mining Truck', 'series': '745'},
    {'type': 'DUMP_TRUCK', 'model': 'Cat 777G Off-Highway Haul Truck', 'series': '777G'},
    {'type': 'COMPACTOR', 'model': 'Cat CS56B Vibratory Soil Compactor', 'series': 'CS56B'},
    {'type': 'CRANE', 'model': 'Cat TL1255D Heavy Duty Telehandler', 'series': 'TL1255D'},
    {'type': 'GENERATOR', 'model': 'Cat C175-16 Industrial Diesel Generator Set', 'series': 'C175'},
]

JOB_SITES = [
    {
        'site_code': 'S-CAT-BLR01',
        'name': 'Bengaluru Metro Underground Line 4',
        'description': 'Heavy tunneling and soil excavation with 24/7 earth-moving operations.',
        'address': 'Kanakapura Corridor, Bengaluru, Karnataka, India',
        'latitude': 12.9716,
        'longitude': 77.5946
    },
    {
        'site_code': 'S-CAT-HYD02',
        'name': 'Hyderabad Airport Expressway Phase 3',
        'description': 'Grade preparation, compaction, and aggregate haulage.',
        'address': 'Shamshabad Outer Ring Road, Hyderabad, Telangana, India',
        'latitude': 17.3850,
        'longitude': 78.4867
    },
    {
        'site_code': 'S-CAT-MUM03',
        'name': 'Mumbai Coastal Road Reclamation & Seawall',
        'description': 'Heavy rock armor placement and high-tonnage wheel loader reclamation.',
        'address': 'Marine Drive Seawall Project, Mumbai, Maharashtra, India',
        'latitude': 18.9870,
        'longitude': 72.8150
    },
    {
        'site_code': 'S-CAT-KOL04',
        'name': 'Raniganj Open-Cast Coal Mine Project',
        'description': 'High-volume overburden removal with mining excavators and articulated dumpers.',
        'address': 'Raniganj Coalfield Sector 9, West Bengal, India',
        'latitude': 23.6200,
        'longitude': 87.1300
    },
    {
        'site_code': 'S-CAT-DEL05',
        'name': 'Delhi-Mumbai Expressway Bridge Incline',
        'description': 'Pylon foundation digging, dozing, and heavy ground leveling.',
        'address': 'Sector 82 Highway Hub, Gurugram, Haryana, India',
        'latitude': 28.4595,
        'longitude': 77.0266
    }
]


class Command(BaseCommand):
    help = 'Seed database with realistic Caterpillar construction & mining fleet data'

    def handle(self, *args, **options):
        self.stdout.write('Starting Caterpillar fleet database seeding...')

        # 1. Create Users
        User.objects.filter(email__in=[
            'admin@caterpillar.com',
            'fleet.manager@caterpillar.com',
            'operator1@caterpillar.com',
            'viewer@caterpillar.com'
        ]).delete()

        admin = User.objects.create_superuser(
            email='admin@caterpillar.com',
            password='admin123456',
            first_name='Cat',
            last_name='Admin',
            role='ADMIN'
        )

        manager = User.objects.create_user(
            email='fleet.manager@caterpillar.com',
            password='manager123456',
            first_name='Marcus',
            last_name='Vance',
            role='MANAGER'
        )

        operator_user = User.objects.create_user(
            email='operator1@caterpillar.com',
            password='operator123456',
            first_name='David',
            last_name='Kovacs',
            role='OPERATOR'
        )

        viewer = User.objects.create_user(
            email='viewer@caterpillar.com',
            password='viewer123456',
            first_name='Site',
            last_name='Auditor',
            role='VIEWER'
        )
        self.stdout.write('Created 4 Caterpillar RBAC users.')

        # 2. Create Job Sites
        Site.objects.all().delete()
        sites = []
        for site_info in JOB_SITES:
            s = Site.objects.create(
                site_code=site_info['site_code'],
                name=site_info['name'],
                description=site_info['description'],
                address=site_info['address'],
                latitude=site_info['latitude'],
                longitude=site_info['longitude'],
                status='ACTIVE'
            )
            sites.append(s)
        self.stdout.write(f'Created {len(sites)} Caterpillar job sites.')

        # 3. Create Heavy Machinery Operators
        Operator.objects.all().delete()
        operators = []
        operator_names = [
            'David Kovacs (Master Operator - Hydraulic Excavators)',
            'Rajesh Kumar (Class-A Heavy Dozers & Loaders)',
            'Ananya Sharma (Mining Dump Trucks Specialist)',
            'Carlos Mendez (Vibratory Compaction & Grading)',
            'Suresh Patel (Heavy Rigging & Telehandlers)'
        ]
        for idx, name in enumerate(operator_names):
            op = Operator.objects.create(
                employee_id=f'CAT-OP-{101+idx}',
                name=name,
                phone=f'+91 98765 {idx}4321',
                email=f'cat.op{idx+1}@caterpillar.com',
                status='ACTIVE'
            )
            operators.append(op)
        self.stdout.write(f'Created {len(operators)} certified heavy machinery operators.')

        # 4. Create Caterpillar Equipment Fleet
        Equipment.objects.all().delete()
        equipment_list = []

        for idx, cat in enumerate(CAT_MODELS):
            site = sites[idx % len(sites)]
            eq_id = f"CAT-{cat['series']}-{1001 + idx}"
            status = Equipment.STATUS_AVAILABLE if idx % 2 == 0 else Equipment.STATUS_RENTED

            eq = Equipment.objects.create(
                equipment_id=eq_id,
                equipment_type=cat['type'],
                manufacturer='Caterpillar Inc.',
                model=cat['model'],
                serial_number=f"CAT000{cat['series']}X{idx+100}",
                qr_code=f"QR-CAT-{eq_id}",
                rfid_uid=f"RFID-CAT-{100000000 + idx}",
                site=site,
                status=status,
                current_operator=operators[idx % len(operators)] if status == Equipment.STATUS_RENTED else None,
                purchase_date=datetime.now().date() - timedelta(days=random.randint(100, 1200))
            )
            equipment_list.append(eq)

            # Create Live State
            EquipmentLiveState.objects.create(
                equipment=eq,
                status=status,
                last_seen=datetime.now(),
                latitude=site.latitude + random.uniform(-0.008, 0.008),
                longitude=site.longitude + random.uniform(-0.008, 0.008),
                engine_hours=random.uniform(250, 4800),
                idle_hours=random.uniform(30, 350),
                fuel_level=random.uniform(45, 95),
                speed=round(random.uniform(5, 25), 1) if status == Equipment.STATUS_RENTED else 0.0,
                operator=operators[idx % len(operators)] if status == Equipment.STATUS_RENTED else None
            )

        self.stdout.write(f'Created {len(equipment_list)} Caterpillar industrial machines.')

        # 5. Create Active Rentals
        Rental.objects.all().delete()
        rented_machines = [eq for eq in equipment_list if eq.status == Equipment.STATUS_RENTED]
        for idx, eq in enumerate(rented_machines):
            Rental.objects.create(
                rental_reference=f"CAT-RNT-{10001 + idx}",
                equipment=eq,
                operator=eq.current_operator,
                site=eq.site,
                checkout_at=datetime.now() - timedelta(days=random.randint(1, 14)),
                due_at=datetime.now() + timedelta(days=random.randint(5, 30)),
                status=Rental.STATUS_ACTIVE,
                created_by=admin
            )
        self.stdout.write(f'Created {len(rented_machines)} Caterpillar job site rental contracts.')

        # 6. Seed Telemetry
        Telemetry.objects.all().delete()
        for eq in equipment_list:
            for t_idx in range(6):
                t_time = datetime.now() - timedelta(hours=(6 - t_idx) * 4)
                Telemetry.objects.create(
                    event_id=f"TEL-CAT-{eq.equipment_id}-{t_idx+1}",
                    equipment=eq,
                    timestamp=t_time,
                    latitude=eq.site.latitude + random.uniform(-0.004, 0.004),
                    longitude=eq.site.longitude + random.uniform(-0.004, 0.004),
                    engine_hours=round(500 + t_idx * 3.5, 2),
                    idle_hours=round(45 + t_idx * 0.4, 2),
                    fuel_level=round(90 - t_idx * 4.2, 1),
                    fuel_consumed=round(t_idx * 14.5, 2),
                    speed=round(random.uniform(0, 18), 1),
                    operator=eq.current_operator
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded Caterpillar Heavy Equipment Fleet Database!'))
