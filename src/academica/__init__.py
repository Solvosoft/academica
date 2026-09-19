# Carga la app de celery al iniciar Django para que @shared_task la use.
from .celery import app as celery_app

__version__ = '2.0.0'

__all__ = ('celery_app',)
