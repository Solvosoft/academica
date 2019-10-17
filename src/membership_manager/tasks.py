from async_notifications.register import update_template_context
from async_notifications.utils import send_email_from_template
from celery.schedules import crontab
from celery.task import task, periodic_task
from celery.utils.log import get_task_logger
from requests import request

from membership_manager.admin_memberships import filter_memb_queryset
from membership_manager.admin_pdf import invoice_expiration_filter_queryset
from membership_manager.models import Membership, Invoice

logger = get_task_logger(__name__)
#every 5 mins this taks gets executed
@periodic_task(run_every=(crontab(minute='*/5')), name="task_notify", ignore_result=True)
def task_notify_invoice_expiration():
    """
    Gets the membership invoices and notify if there is any in the expiration range.
    """
    qset = Invoice.objects.all()
    notify_qset = invoice_expiration_filter_queryset(qset)

@periodic_task(run_every=(crontab(minute='*/5')), name="task_notify", ignore_result=True)
def task_notify_membership_expiration():
    """
    Gets the membership , and notify is there is in the expiration range.
    """
    qset = Invoice.objects.all()
    notify_qset = filter_memb_queryset(qset)

@periodic_task(run_every=(crontab(minute='*/5')), name="task_notify", ignore_result=True)
def task__invoice_creation():
    """
    Create a invoice, at 60 days left - renewal expiration.
    """
    qset = Invoice.objects.all()
    notify_qset = invoice_expiration_filter_queryset(qset)


