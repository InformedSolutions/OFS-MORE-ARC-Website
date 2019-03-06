from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = BUILTIN_APPS + THIRD_PARTY_APPS + PROJECT_APPS

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': from_env('POSTGRES_DB', 'postgres'),
        'USER': from_env('POSTGRES_USER', 'ofsted'),
        'PASSWORD': from_env('POSTGRES_PASSWORD', 'OfstedB3ta'),
        'HOST': from_env('POSTGRES_HOST', '130.130.52.132'),
        'PORT': from_env('POSTGRES_PORT', '5462')
    }
}

MIGRATION_MODULES = {
    'arc_application': 'arc_application.tests.test_migrations',
}
