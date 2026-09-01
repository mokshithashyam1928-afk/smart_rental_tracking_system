"""
Development settings for Smart Rental Tracking System backend.
"""
from .base import *

DEBUG = True

# Development database (can use SQLite for quick setup)
# DATABASES['default'] = {
#     'ENGINE': 'django.db.backends.sqlite3',
#     'NAME': BASE_DIR / 'db.sqlite3',
# }

# All hosts allowed in development
ALLOWED_HOSTS = ['*']

# Development CORS
CORS_ALLOW_ALL_ORIGINS = True

# Disable some security features for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Add django-extensions for development commands
INSTALLED_APPS += ['django_extensions']

# Verbose logging
LOGGING['root']['level'] = 'DEBUG'
