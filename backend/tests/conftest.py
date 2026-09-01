"""
Pytest configuration and fixtures.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.sites.models import Site
from apps.operators.models import Operator
from apps.equipment.models import Equipment

User = get_user_model()


@pytest.fixture
def api_client():
    """Return API client."""
    return APIClient()


@pytest.fixture
@pytest.mark.django_db
def admin_user(db):
    """Create and return admin user."""
    return User.objects.create_superuser(
        email='admin@test.com',
        password='admin123',
        first_name='Admin',
        last_name='User',
        role='ADMIN'
    )


@pytest.fixture
@pytest.mark.django_db
def manager_user(db):
    """Create and return manager user."""
    return User.objects.create_user(
        email='manager@test.com',
        password='manager123',
        first_name='Manager',
        last_name='User',
        role='MANAGER'
    )


@pytest.fixture
@pytest.mark.django_db
def operator_user(db):
    """Create and return operator user."""
    return User.objects.create_user(
        email='operator@test.com',
        password='operator123',
        first_name='Operator',
        last_name='User',
        role='OPERATOR'
    )


@pytest.fixture
@pytest.mark.django_db
def site(db):
    """Create and return a test site."""
    return Site.objects.create(
        site_code='S001',
        name='Test Site',
        address='123 Test Street',
        latitude=10.0,
        longitude=20.0,
        status='ACTIVE'
    )


@pytest.fixture
@pytest.mark.django_db
def operator(db):
    """Create and return a test operator."""
    return Operator.objects.create(
        employee_id='OP001',
        name='John Operator',
        phone='555-0001',
        email='operator@test.com',
        status='ACTIVE'
    )


@pytest.fixture
@pytest.mark.django_db
def equipment(db, site):
    """Create and return test equipment."""
    return Equipment.objects.create(
        equipment_id='EQX0001',
        equipment_type='EXCAVATOR',
        manufacturer='Caterpillar',
        model='CAT 320',
        serial_number='SN12345',
        qr_code='QR-EQX0001',
        site=site,
        status='AVAILABLE'
    )


@pytest.fixture
def authenticated_client(api_client, admin_user):
    """Return API client authenticated as admin."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client
