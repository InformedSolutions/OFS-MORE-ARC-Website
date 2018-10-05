from .base import *

DEBUG = False

ALLOWED_HOSTS = ['*']

PROD_APPS = [
    'whitenoise',
]

INSTALLED_APPS = BUILTIN_APPS + THIRD_PARTY_APPS + PROD_APPS + PROJECT_APPS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB', 'postgres'),
        'USER': os.environ.get('POSTGRES_USER', 'ofsted'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'OfstedB3ta'),
        'HOST': os.environ.get('POSTGRES_HOST', 'ofsted-postgres'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432')
    }
}

# Automatic Django logging at the INFO level (i.e everything the comes to the console when ran locally)
LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'formatters': {
    'console': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        },
  'handlers': {
    'file': {
        'level': 'INFO',
        'class': 'logging.handlers.TimedRotatingFileHandler',
        'filename': 'logs/output.log',
        'formatter': 'console',
        'when': 'midnight',
        'backupCount': 10
    },
    'console': {
        'level': 'INFO',
        'class': 'logging.StreamHandler'
    },
   },
   'loggers': {
     '': {
       'handlers': ['file', 'console'],
         'level': 'ERROR',
           'propagate': True,
      },
      'django.server': {
       'handlers': ['file', 'console'],
         'level': 'ERROR',
           'propagate': True,
      },
    },
}
