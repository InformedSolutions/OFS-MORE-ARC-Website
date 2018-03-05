from .base import *

DEBUG = True

# Base URL of notify gateway
NOTIFY_URL = 'http://130.130.52.132:8095/notify-gateway'

ALLOWED_HOSTS = ['*']

DEV_APPS = [
]

INSTALLED_APPS = BUILTIN_APPS + THIRD_PARTY_APPS + DEV_APPS + PROJECT_APPS

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB', 'postgres'),
        'USER': os.environ.get('POSTGRES_USER', 'ofsted'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'OfstedB3ta'),
        'HOST': os.environ.get('POSTGRES_HOST', '130.130.52.132'),
        'PORT': os.environ.get('POSTGRES_PORT', '5462')
    }
}
