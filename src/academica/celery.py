from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academica.settings')
from django.conf import settings  # noqa

app = Celery('academica')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

from celery.schedules import crontab

app.conf.CELERYBEAT_SCHEDULE = {
    'send_daily_emails': {  # this sends the emails in the email notifications list
        'task': 'async_notifications.tasks.send_daily',
        'schedule': crontab(minute='*/5'),  # execute every 5 minutes
    },
    'remove_invoices': {  # remove invoices generated that were not paid in the grace period
        'task': 'matricula.tasks.remove_invoices',
        'schedule': crontab(minute='*/20'),  # execute every 20 minutes
    },
}
app.conf.CELERY_TIMEZONE = settings.TIME_ZONE
