import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academica.settings')

app = Celery('academica')

# Toda la configuración de celery vive en settings.py con el prefijo CELERY_.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'process_async_notifications': {  # envía los correos encolados de djgentelella
        'task': 'matricula.tasks.process_async_notifications',
        'schedule': crontab(minute='*/5'),
    },
    'poll_card_payments': {  # respaldo del webhook del servicio de pagos con tarjeta
        'task': 'matricula.tasks.poll_card_payments',
        'schedule': crontab(minute='*/5'),
    },
    'remove_invoices': {  # elimina las facturas no pagadas dentro del periodo de gracia
        'task': 'matricula.tasks.remove_invoices',
        'schedule': crontab(minute='*/20'),
    },
}
