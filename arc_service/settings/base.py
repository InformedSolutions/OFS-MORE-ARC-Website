import os

# Server name for showing server that responded to request under load balancing conditions
SERVER_LABEL = 'Test_1'

ARC_GROUP = 'arc'
CONTACT_CENTRE= 'contact-centre'
APPLICATION_LIMIT = 5

NOTIFY_URL = os.environ.get('APP_NOTIFY_URL')

# Base URL of addressing-service gateway
ADDRESSING_URL = os.environ.get('APP_ADDRESSING_URL')

# Address of Childminder application
CHILDMINDER_EMAIL_VALIDATION_URL = os.environ.get('CHILDMINDER_EMAIL_VALIDATION_URL')

# Address of Nanny application
NANNY_PUBLIC_URL = os.environ.get('NANNY_PUBLIC_URL')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'm$9lif+zcnb5i5n21q9yecn8vs4h%(%7=!k%#6rlbhkfuq1mfq'

EXECUTING_AS_TEST = os.environ.get('EXECUTING_AS_TEST')

# Application definition

BUILTIN_APPS = [
    'django_extensions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'govuk_forms',
    'govuk_template',
    'govuk_template_base',
    'timeline_logger',
]

PROJECT_APPS = [
    'arc_application',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'arc_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'arc_application/templates/'),
                 os.path.join(BASE_DIR, 'arc_application/templates/nanny_templates/'),
                 os.path.join(BASE_DIR, 'arc_application/templates/childminder_templates/')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'govuk_template_base.context_processors.govuk_template_base',
                "arc_application.middleware.globalise_url_prefix",
                "arc_application.middleware.globalise_server_name",
                "arc_application.middleware.set_review_tab_visibility",
            ],
        },
    },
]

WSGI_APPLICATION = 'arc_service.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Session settings
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Left hand portion of below is the number of minutes after
# which a user will be logged out due to inactivity
SESSION_COOKIE_AGE = 30 * 60
SESSION_SAVE_EVERY_REQUEST = True

# Locales

LANGUAGE_CODE = 'en-GB'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)

URL_PREFIX = '/arc'
STATIC_URL = URL_PREFIX + '/static/'
REVIEW_URL_PREFIX = '/arc/review'
LOGIN_URL = URL_PREFIX + '/login'

SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Test outputs
TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
TEST_OUTPUT_VERBOSE = True
TEST_OUTPUT_DESCRIPTIONS = True
TEST_OUTPUT_DIR = 'xmlrunner'

MIGRATION_MODULES = {}

# Regex Validation Strings
REGEX = {
    "EMAIL": "^([a-zA-Z0-9_\-\.']+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$",
    "MOBILE": "^(\+44|0044|0)[7][0-9]{3,14}$",
    "PHONE": "^(?:(?:\(?(?:0(?:0|11)\)?[\s-]?\(?|\+)44\)?[\s-]?(?:\(?0\)?[\s-]?)?)|(?:\(?0))(?:(?:\d{5}\)?[\s-]?\d{4,"
             "5})|(?:\d{4}\)?[\s-]?(?:\d{5}|\d{3}[\s-]?\d{3}))|(?:\d{3}\)?[\s-]?\d{3}[\s-]?\d{3,4})|(?:\d{2}\)?["
             "\s-]?\d{4}[\s-]?\d{4}))(?:[\s-]?(?:x|ext\.?|\#)\d{3,4})?$",
    "INTERNATIONAL_PHONE": "^(\+|[0-9])[0-9]{5,20}$",
    "POSTCODE_UPPERCASE": "^[A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9][A-Z][A-Z]$",
    "LAST_NAME": "^[A-zÀ-ÿ- ']+$",
    "MIDDLE_NAME": "^[A-zÀ-ÿ- ']+$",
    "FIRST_NAME": "^[A-zÀ-ÿ- ']+$",
    "TOWN": "^[A-Za-z- ]+$",
    "COUNTY": "^[A-Za-z- ]+$",
    "COUNTRY": "^[A-Za-z- ]+$",
    "VISA": "^4[0-9]{12}(?:[0-9]{3})?$",
    "MASTERCARD": "^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$",
    "MAESTRO": "^(?:5[0678]\d\d|6304|6390|67\d\d)\d{8,15}$",
    "CARD_SECURITY_NUMBER": "^[0-9]{3,4}$"
}

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
        'level': 'DEBUG',
        'class': 'logging.handlers.TimedRotatingFileHandler',
        'filename': 'logs/output.log',
        'formatter': 'console',
        'when': 'midnight',
        'backupCount': 10
    },
    'console': {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler'
    },
   },
   'loggers': {
     '': {
       'handlers': ['file', 'console'],
         'level': 'DEBUG',
           'propagate': True,
      },
      'django.server': {
       'handlers': ['file', 'console'],
         'level': 'INFO',
           'propagate': True,
      },
    },
}
