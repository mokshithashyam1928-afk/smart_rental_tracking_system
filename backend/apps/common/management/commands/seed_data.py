"""
Management command to seed database with test data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.sites.models import Site
from apps.operators.models import Operator
from apps.equipment.models import Equipment
from apps.rentals.models import Rental
from apps.telemetry.models import Telemetry, EquipmentLiveState
from faker import Faker
from datetime import datetime, timedelta
import random

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = 'Seed the database with test data'
    
    def add_arguments(self, parser):
        parser.add_argument('--sites', type=int, default=10, help='Number of sites to create')
        parser.add_argument('--operators', type=int, default=30, help='Number of operators to create')
        parser.add_argument('--equipment', type=int, default=50, help='Number of equipment to create')
    
    def handle(self, *args, **options):
        self.stdout.write('Starting database seeding...')
        
        # Create users
        self.stdout.write('Creating users...')
        User.objects.filter(email__in=[
            'admin@example.com',
            'manager@example.com',
            'operator@example.com',
            'viewer@example.com'
        ]).delete()
        
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='admin123456',
            first_name='Admin',
            last_name='User',
            role='ADMIN'
        )
        
        manager = User.objects.create_user(
            email='manager@example.com',
            password='manager123456',
            first_name='Manager',
            last_name='User',
            role='MANAGER'
        )
        
        operator = User.objects.create_user(
            email='operator@example.com',
            password='operator123456',
            first_name='Operator',
            last_name='User',
            role='OPERATOR'
        )
        
        viewer = User.objects.create_user(
            email='viewer@example.com',
            password='viewer123456',
            first_name='Viewer',
            last_name='User',
            role='VIEWER'
        )
        
        self.stdout.write(f'Created 4 users')
        
        # Create sites
        self.stdout.write(f'Creating {options["sites"]} sites...')
        sites = []
        for i in range(options['sites']):
            site = Site.objects.create(
                site_code=f'S{i+1:03d}',
                name=f'Construction Site {i+1}',
                description=fake.text(),
                address=fake.address(),
                latitude=random.uniform(-90, 90),
                longitude=random.uniform(-180, 180),
                status='ACTIVE'
            )
            sites.append(site)
        
        self.stdout.write(f'Created {len(sites)} sites')
        
        # Create operators
        self.stdout.write(f'Creating {options["operators"]} operators...')
        operators = []
        for i in range(options['operators']):
            op = Operator.objects.create(
                employee_id=f'OP{i+1:04d}',
                name=fake.name(),
                phone=fake.phone_number(),
                email=fake.email(),
                status='ACTIVE'
            )
            operators.append(op)
        
        self.stdout.write(f'Created {len(operators)} operators')
        
        # Create equipment
        self.stdout.write(f'Creating {options["equipment"]} equipment...')
        equipment_list = []
        equipment_types = ['EXCAVATOR', 'BULLDOZER', 'CRANE', 'LOADER', 'GRADER', 'COMPACTOR']
        
        for i in range(options['equipment']):
            equipment_type = random.choice(equipment_types)
            site = random.choice(sites)
            status = random.choice([
                Equipment.STATUS_AVAILABLE,
                Equipment.STATUS_AVAILABLE,
                Equipment.STATUS_IDLE,
                Equipment.STATUS_MAINTENANCE
            ])
            
            eq = Equipment.objects.create(
                equipment_id=f'EQX{i+1:04d}',
                equipment_type=equipment_type,
                manufacturer='Caterpillar',
                model=f'{equipment_type}-MODEL-{random.randint(1000, 9999)}',
                serial_number=f'SN{random.randint(100000, 999999)}',
                qr_code=f'QR-EQX{i+1:04d}',
                rfid_uid=f'RFID-{random.randint(1000000000, 9999999999)}',
                site=site,
                status=status,
                purchase_date=fake.date_object(),
            )
            equipment_list.append(eq)
            
            # Create live state
            EquipmentLiveState.objects.create(
                equipment=eq,
                status=status,
                last_seen=datetime.now(),
                latitude=site.latitude + random.uniform(-0.5, 0.5),
                longitude=site.longitude + random.uniform(-0.5, 0.5),
                engine_hours=random.uniform(100, 5000),
                idle_hours=random.uniform(10, 500),
                fuel_level=random.uniform(20, 100),
                speed=0
            )
        
        self.stdout.write(f'Created {len(equipment_list)} equipment')
        
        # Create sample rentals
        self.stdout.write('Creating sample rentals...')
        for i in range(10):
            eq = random.choice(equipment_list)
            op = random.choice(operators)
            site = random.choice(sites)
            
            if eq.status not in [Equipment.STATUS_AVAILABLE, Equipment.STATUS_IDLE]:
                continue
            
            rental = Rental.objects.create(
                rental_reference=f'RNT-{random.randint(100000, 999999):06d}',
                equipment=eq,
                operator=op,
                site=site,
                checkout_at=datetime.now() - timedelta(days=random.randint(0, 5)),
                due_at=datetime.now() + timedelta(days=random.randint(1, 10)),
                status=Rental.STATUS_ACTIVE,
                created_by=admin
            )
            
            eq.status = Equipment.STATUS_RENTED
            eq.current_operator = op
            eq.save()
        
        self.stdout.write('Created 10 sample rentals')
        
        # Create sample telemetry
        self.stdout.write('Creating sample telemetry events...')
        for eq in equipment_list[:10]:  # Only for first 10 equipment
            for i in range(5):
                timestamp = datetime.now() - timedelta(hours=random.randint(0, 24))
                Telemetry.objects.create(
                    event_id=f'EVT-{eq.equipment_id}-{i}',
                    equipment=eq,
                    timestamp=timestamp,
                    latitude=eq.site.latitude + random.uniform(-0.1, 0.1),
                    longitude=eq.site.longitude + random.uniform(-0.1, 0.1),
                    engine_hours=random.uniform(100, 5000),
                    idle_hours=random.uniform(10, 500),
                    fuel_level=random.uniform(20, 100),
                    fuel_consumed=random.uniform(1, 50),
                    speed=random.uniform(0, 50),
                    operator=random.choice(operators)
                )
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
        self.stdout.write('\nTest credentials:')
        self.stdout.write('Admin: admin@example.com / admin123456')
        self.stdout.write('Manager: manager@example.com / manager123456')
        self.stdout.write('Operator: operator@example.com / operator123456')
        self.stdout.write('Viewer: viewer@example.com / viewer123456')
