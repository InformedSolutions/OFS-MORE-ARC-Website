from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

DEV_APPS = [
]

INSTALLED_APPS = BUILTIN_APPS + THIRD_PARTY_APPS + DEV_APPS + PROJECT_APPS

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': from_env('POSTGRES_DB', 'postgres'),
        'USER': from_env('POSTGRES_USER', 'ofsted'),
        'PASSWORD': from_env('POSTGRES_PASSWORD', 'OfstedB3ta'),
        'HOST': from_env('POSTGRES_HOST', 'ofsted-postgres'),
        'PORT': from_env('POSTGRES_PORT', '5432')
    }
}

