from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'membresias_codigosur.settings')
from django.conf import settings  # noqa

app = Celery('membresias')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

from celery.schedules import crontab

app.conf.CELERYBEAT_SCHEDULE = {
    'create_invoice': {
        'task': 'membership_manager.tasks.task_invoice_creation',
        'schedule': crontab(minute=20, hour=0),  # execute 00:01h
    },
    'membership_state': {
        'task': 'membership_manager.tasks.task_membership_deactivating_or_graceperiod',  # this creates the email notifications list
        'schedule': crontab(minute=32, hour=2),  # execute 00:30h
    },
    'load_notifications': {  # this adds email notifications to the list too
        'task': 'membership_manager.tasks.task_notify_invoice_expiration',
        'schedule': crontab(minute=11, hour=1),  # execute 00:01h
    },
    'send_daily_emails': {  # this sends the emails in the email notifications list
        'task': 'async_notifications.tasks.send_daily',
        'schedule': crontab(minute='*/5'),  # execute 01:00h
    },
    'update_last_daterenew_task': {
        'task': 'membership_manager.tasks.update_last_daterenew_task',
        'schedule': crontab(minute=11, hour=5),  # execute 00:01h

    }
}
app.conf.CELERY_TIMEZONE = settings.TIME_ZONE
