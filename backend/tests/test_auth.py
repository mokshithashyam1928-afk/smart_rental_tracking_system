"""
Example tests for authentication.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestAuthentication:
    """Test suite for authentication endpoints."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.refresh_url = '/api/auth/refresh/'
        self.me_url = '/api/auth/me/'
    
    def test_user_registration(self):
        """Test user registration."""
        data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'role': 'VIEWER'
        }
        response = self.client.post(self.register_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data['data']
        assert 'refresh' in response.data['data']
    
    def test_user_login(self):
        """Test user login."""
        # Create user
        User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data['data']
    
    def test_invalid_login(self):
        """Test login with invalid credentials."""
        data = {
            'email': 'invalid@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user(self):
        """Test getting current user profile."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Login
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        login_response = self.client.post(self.login_url, login_data)
        token = login_response.data['data']['access']
        
        # Get user profile
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.me_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['email'] == 'test@example.com'
