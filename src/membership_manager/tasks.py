from django.utils import timezone

from membership_manager.task_utils import notify_invoice_expiration, invoice_creation, renew_graceperiod, \
    membership_deactivating, membership_deactivating_membership
from membresias_codigosur.celery import app

@app.task
def task_notify_invoice_expiration():
    """
    now=timezone.localtime(timezone.now())
    notify_invoice_expiration(now)
    """
    pass

@app.task
def task_invoice_creation():
    """
    Create a invoice, at 60 days left - renewal expiration.
    """
    now=timezone.localtime(timezone.now())
    #invoice_creation(now)
    pass

@app.task
def task_membership_deactivating_or_graceperiod():
    """
    now=timezone.localtime(timezone.now())
    renew_graceperiod(now)
    membership_deactivating(now)
    """
    pass

@app.task
def task_membership_deactivating_membership(id_membership, email):
    membership_deactivating_membership(id_membership, email)
