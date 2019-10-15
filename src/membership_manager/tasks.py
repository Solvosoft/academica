from async_notifications.register import update_template_context
from async_notifications.utils import send_email_from_template
from celery.schedules import crontab
from celery.task import task, periodic_task
from celery.utils.log import get_task_logger
from requests import request

from membership_manager.admin import fiter_memb_queryset, q_generator
from membership_manager.admin_pdf import invoice_expiration_filter_queryset
from membership_manager.models import Membership, Invoice

logger = get_task_logger(__name__)

@periodic_task(run_every=(crontab(minute='*/1')), name="task_notify", ignore_result=True)
def task_notify():
    """
    Gets the membership invoices pending at optios especified in the filter method.
    """

    qset = Invoice.objects.all()
    notify_qset = invoice_expiration_filter_queryset(qset)
    print()

