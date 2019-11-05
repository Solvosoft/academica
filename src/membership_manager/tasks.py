from django.utils import timezone


from membership_manager.models import Membership, Invoice, MembershipRenew

from membership_manager.task_utils import notify_invoice_expiration, invoice_creation, renew_graceperiod, \
    membership_deactivating
from membresias_codigosur.celery import app

@app.task
def task_notify_invoice_expiration():
    notify_invoice_expiration(timezone.now())

@app.task
def task_invoice_creation():
    """
    Create a invoice, at 60 days left - renewal expiration.
    """
    invoice_creation(timezone.now())
@app.task
def task_membership_deactivating_or_graceperiod():
    renew_graceperiod(timezone.now())
    membership_deactivating(timezone.now())


