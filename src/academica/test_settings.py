"""
Configuración para las pruebas de navegación (Selenium).

Uso: ``manage.py test --settings=academica.test_settings --tag=selenium``
(los targets ``make test-selenium*`` ya lo hacen).
"""
import os

from .settings import *  # noqa: F401,F403

INSTALLED_APPS = INSTALLED_APPS + ['academica_test']
# Marca las páginas como "listas" para que Selenium no dependa de sleeps.
MIDDLEWARE = MIDDLEWARE + ['academica_test.middleware.TestingReadyMiddleware']

DEBUG = False
ALLOWED_HOSTS = ['*']
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Pago con tarjeta activo contra un servicio simulado (ver academica_test.tests.fakes)
WEBCHECKOUT_BASE_URL = 'https://pagos.test'
WEBCHECKOUT_API_TOKEN = 'api-token'
WEBCHECKOUT_BUSINESS_ID = '11111111-1111-1111-1111-111111111111'
WEBCHECKOUT_NOTIFICATION_TOKEN = 's3cret'
CARD_PAYMENTS_ENABLED = True

TESTING_MODE = True
GENERATE_SCREENSHOTS = os.getenv('GENERATE_SCREENSHOTS', 'False') == 'True'
SELENIUM_RESULTS_DIR = os.getenv('SELENIUM_RESULTS_DIR', str(BASE_NOCODE_DIR / 'selenium-results'))

LOGGING = {'version': 1, 'disable_existing_loggers': False,
           'handlers': {'null': {'class': 'logging.NullHandler'}},
           'root': {'handlers': ['null']}}
