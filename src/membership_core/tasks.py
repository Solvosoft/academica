from django.conf import settings
from django.utils.module_loading import import_string
import importlib
from djmoney import settings as djmoneysettings
app = importlib.import_module(settings.CELERY_MODULE).app

@app.task
def update_rates(backend=djmoneysettings.EXCHANGE_BACKEND, **kwargs):
    backend = import_string(backend)()
    backend.update_rates(**kwargs)