from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

DEV_APPS = []

INSTALLED_APPS = BUILTIN_APPS + THIRD_PARTY_APPS + DEV_APPS + PROJECT_APPS

# Base URL of addressing-service gateway
ADDRESSING_URL = os.environ.get('APP_ADDRESSING_URL', 'http://localhost:8002/addressing-service')

NOTIFY_URL = os.environ.get('APP_NOTIFY_URL', 'http://localhost:8003/notify-gateway')

IDENTITY_URL = os.environ.get('APP_IDENTITY_URL', 'http://localhost:8007/identity/')

NANNY_GATEWAY_URL = os.environ.get('APP_NANNY_GATEWAY_URL', 'http://localhost:8009/nanny-gateway')

# Address of Childminder application
CHILDMINDER_EMAIL_VALIDATION_URL = os.environ.get('CHILDMINDER_EMAIL_VALIDATION_URL', 'http://localhost:8000/childminder')

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': os.environ.get('POSTGRES_PORT')
    }
}

MIGRATION_MODULES = {
    'arc_application': 'arc_application.tests.test_migrations',
}
