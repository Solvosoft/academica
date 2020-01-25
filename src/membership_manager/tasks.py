from django.utils import timezone

from membership_manager.task_utils import notify_invoice_expiration, invoice_creation, \
    membership_deactivating, membership_deactivating_membership
from membresias_codigosur.celery import app


@app.task
def task_invoice_creation():
    """
    Create a invoice, at 60 days left - renewal expiration.
    """
    now=timezone.localtime(timezone.now())
    invoice_creation(now)



@app.task
def task_notify_invoice_expiration():
    """
    For all pending invoice calc if notification needs to be send
    :return:
    """
    now=timezone.localtime(timezone.now())
    notify_invoice_expiration(now)

@app.task
def task_membership_deactivating_or_graceperiod():
    now=timezone.localtime(timezone.now())
    membership_deactivating(now)

@app.task
def task_membership_deactivating_membership(id_membership, email):
    membership_deactivating_membership(id_membership, email)
