from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'membresias_codigosur.settings')
from django.conf import settings # noqa

app = Celery('membresias')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


from celery.schedules import crontab



app.conf.CELERYBEAT_SCHEDULE = {
    # execute 12:30 pm
    'send_daily_emails': {
        'task': 'async_notifications.tasks.send_daily',
        #'schedule': crontab(minute=30, hour=0),
        'schedule': crontab(minute='*/3'),
    },
    'update_rates': {
        'task': 'path.to.your.task',
        'schedule': crontab(minute=3, hour=2),
        'kwargs': {}  # For custom arguments
    }
}
app.conf.CELERY_TIMEZONE = settings.TIME_ZONE
