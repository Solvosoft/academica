"""
Configuración de Django para Académica.

Toda la configuración que cambia entre entornos se lee de variables de
entorno (o de un archivo ``.env`` en la raíz del repositorio). Ver
``env.example`` para la lista completa.
"""
import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
BASE_NOCODE_DIR = BASE_DIR.parent

load_dotenv(BASE_NOCODE_DIR / '.env', override=False)


def env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')


def env_list(name, default=''):
    return [item.strip() for item in os.getenv(name, default).split(',') if item.strip()]


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-solo-para-desarrollo-cambiar-en-produccion')
DEBUG = env_bool('DEBUG', False)

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', 'localhost,127.0.0.1')
CSRF_TRUSTED_SCHEME = os.getenv('CSRF_TRUSTED_SCHEME', 'https')
CSRF_TRUSTED_ORIGINS = ["%s://%s" % (CSRF_TRUSTED_SCHEME, host) for host in ALLOWED_HOSTS
                        if host not in ('localhost', '127.0.0.1')]

ADMINS = [('Solvo', 'sitio@solvosoft.com')]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'djgentelella',
    'djgentelella.async_notification',
    'rest_framework',
    'django_filters',
    'django_celery_results',
    'django_celery_beat',
    'paypal.standard.ipn',
    'membership_core',
    'matricula',
    'matricula.contrib.bills',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'academica.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'academica.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DBNAME', 'academica'),
        'USER': os.getenv('DBUSER', 'academica_user'),
        'PASSWORD': os.getenv('DBPASSWORD', 'NOUSARENPROD'),
        'HOST': os.getenv('DBHOST', '127.0.0.1'),
        'PORT': os.getenv('DBPORT', '5432'),
        'TEST': {
            # Nombre propio para que nunca coincida con la base de producción.
            'NAME': os.getenv('DBTESTNAME', 'test_academica'),
        },
    },
}

# AutoField: evita migraciones pendientes en apps de terceros (django-paypal)
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTHENTICATION_BACKENDS = ["membership_core.authbackend.EmailBackend"]
# Días de validez del token de confirmación de correo
TOKEN_CONFIRMATION_EXPIRE_DAYS = 15

# Internationalization

LANGUAGE_CODE = 'es'
LANGUAGES = (
    ('es', _('Spanish')),
    ('en', _('English')),
)
TIME_ZONE = 'America/Costa_Rica'
USE_I18N = True
USE_TZ = True

# Desde Django 5 no existe USE_L10N: los formatos de fecha propios del sitio
# viven en academica/formats/<idioma>/formats.py.
FORMAT_MODULE_PATH = ['academica.formats']
DATE_INPUT_FORMATS = ['%d/%m/%Y', '%Y-%m-%d', '%d/%m/%y']
DATE_FORMAT = 'd/m/Y'
DATETIME_INPUT_FORMATS = [
    '%d/%m/%Y %H:%M',
    '%m/%d/%Y %H:%M',
    '%Y-%m-%d %H:%M',
    '%d/%m/%y %H:%M',
    '%Y/%m/%d %H:%M %A',
]

LOCALE_PATHS = (
    BASE_NOCODE_DIR / 'locale/',
)

# Static and media files

STATIC_URL = os.getenv('STATIC_URL', '/static/')
STATIC_ROOT = os.getenv('STATIC_ROOT', BASE_NOCODE_DIR / 'static/')
MEDIA_URL = os.getenv('MEDIA_URL', '/media/')
MEDIA_ROOT = Path(os.getenv('MEDIA_ROOT', BASE_NOCODE_DIR / 'media/'))

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/home/'
LOGOUT_REDIRECT_URL = '/'

# djgentelella
JQUERY_URL = None
TINYMCE_UPLOAD_PATH = MEDIA_ROOT / 'tinymce'

# Email (MailHog en desarrollo: docker compose levanta el servicio "mail")
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '1025'))
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'webmaster@localhost')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', 'webmaster@localhost')
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', False)
EMAIL_USE_SSL = env_bool('EMAIL_USE_SSL', False)

# djgentelella.async_notification
ASYNC_NOTIFICATION_USER_LOOKUP_FIELDS = ['username', 'email', 'first_name', 'last_name']
ASYNC_BCC = os.getenv('ASYNC_BCC', '')
# En staging, lista de correos a los que se restringe el envío (red de seguridad).
ASYNC_SEND_ONLY_EMAIL = env_list('ASYNC_SEND_ONLY_EMAIL')
ASYNC_SMTP_DEBUG = env_bool('ASYNC_SMTP_DEBUG', False)

# Celery
CELERY_BROKER_URL = os.getenv('BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'django-db')
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_ALWAYS_EAGER = env_bool('CELERY_TASK_ALWAYS_EAGER', False)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'my_cache_table',
    }
}

# PayPal
PAYPAL_TEST = env_bool('PAYPAL_TEST', False)
PAYPAL_RECEIVER_EMAIL = os.getenv('PAYPAL_RECEIVER_EMAIL', "paypal@solvosoft.com")
MY_PAYPAL_HOST = os.getenv('MY_PAYPAL_HOST', "https://matricula.solvosoft.com")
PAYPAL_ERROR_EMAIL_NOFIFY = tuple(env_list('PAYPAL_ERROR_EMAIL_NOFIFY', "info@solvosoft.com"))
PAYMENT_NOTIFICATION_MAIL = env_list('PAYMENT_NOTIFICATION_MAIL', 'german.zarate@solvosoft.com')

# URL pública del sitio: la usan los servicios externos para volver o notificar.
SITE_BASE_URL = os.getenv('SITE_BASE_URL', MY_PAYPAL_HOST).rstrip('/')

# Pago con tarjeta mediante el servicio webcheckout (../payments)
WEBCHECKOUT_BASE_URL = os.getenv('WEBCHECKOUT_BASE_URL', 'https://payments.dev.solvosoft.com').rstrip('/')
WEBCHECKOUT_API_TOKEN = os.getenv('WEBCHECKOUT_API_TOKEN', '')
WEBCHECKOUT_BUSINESS_ID = os.getenv('WEBCHECKOUT_BUSINESS_ID', '')
# Debe coincidir con el id_token del Business en el servicio (autentica el webhook)
WEBCHECKOUT_NOTIFICATION_TOKEN = os.getenv('WEBCHECKOUT_NOTIFICATION_TOKEN', '')
WEBCHECKOUT_TIMEOUT = int(os.getenv('WEBCHECKOUT_TIMEOUT', '10'))
CARD_PAYMENTS_ENABLED = bool(WEBCHECKOUT_API_TOKEN and WEBCHECKOUT_BUSINESS_ID)

# Académica
PROFESSOR_GROUP_NAME = "Profesores"
ADMIN_GROUP_NAME = "Administradores Académica"
HOURS_TO_PAY = 4

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', True)
    CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', True)
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
