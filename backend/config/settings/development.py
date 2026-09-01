"""
Development settings for Caterpillar Smart Rental Tracking System backend.
"""
from .base import *

DEBUG = True

# All hosts allowed in development
ALLOWED_HOSTS = ['*']

# Development CORS
CORS_ALLOW_ALL_ORIGINS = True

# Database for local development:
# If DATABASE_URL or postgres env is not set, use SQLite for instant out-of-the-box running
if os.getenv('USE_POSTGRES', 'false').lower() == 'true':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME', 'cat_smart_rental_db'),
        'USER': os.getenv('DATABASE_USER', 'postgres'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'postgres'),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
    }
else:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }

# In-memory channel layer for local run without Redis
if os.getenv('USE_REDIS', 'false').lower() != 'true':
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'dev-cache',
        }
    }

# Disable some security features for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Optionally add django-extensions if installed
try:
    import django_extensions
    INSTALLED_APPS += ['django_extensions']
except ImportError:
    pass

# Logging
LOGGING['root']['level'] = 'INFO'
