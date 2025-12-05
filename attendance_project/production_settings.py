"""
Production settings for Attendance Management System
Optimized for high performance
"""
import os
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['145.223.22.228', 'localhost', 'mlworkers.com', 'www.mlworkers.com']

# Database with connection pooling - credentials from environment variables
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'attendance_db'),
        'USER': os.environ.get('DB_USER', 'attendance_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Keep connections alive for 10 minutes
        'CONN_HEALTH_CHECKS': True,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Static files
STATIC_ROOT = '/var/www/attendance_system/staticfiles'
STATIC_URL = '/static/'

# Security settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # Handled by nginx
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ============================================
# PERFORMANCE OPTIMIZATIONS
# ============================================

# Use database-backed cache with Redis-like performance
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 5000
        }
    }
}

# Session optimization
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'

# Template caching - only apply if APP_DIRS exists
if 'APP_DIRS' in TEMPLATES[0]:
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]
    del TEMPLATES[0]['APP_DIRS']

# Logging - minimal for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# File upload optimization
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

