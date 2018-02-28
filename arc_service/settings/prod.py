from .base import *

DEBUG = False

ALLOWED_HOSTS = ['*']

PROD_APPS = [
    'whitenoise',
]

INSTALLED_APPS = BUILTIN_APPS + THIRD_PARTY_APPS + PROD_APPS + PROJECT_APPS

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'postgres',
#         'USER': os.environ.get('DATABASE_USER', 'ofsted'),
#         'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'OfstedB3ta'),
#         'HOST': os.environ.get('DATABASE_HOST', 'ofsted-postgres'),
#         'PORT': os.environ.get('DATABASE_PORT', '5432')
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': os.environ.get('DATABASE_USER', 'ofsted'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'OfstedB3ta'),
        'HOST': os.environ.get('DATABASE_HOST', '130.130.52.132'),
        'PORT': os.environ.get('DATABASE_PORT', '5462')
    }
}