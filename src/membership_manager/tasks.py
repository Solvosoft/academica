from async_notifications.register import update_template_context
from async_notifications.utils import send_email_from_template
from celery.schedules import crontab
from celery.task import task, periodic_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from requests import request

#from membership_manager.admin_memberships import filter_memb_queryset
from membership_manager.admin_pdf import invoice_expiration_filter_queryset, renewal_expiration_filter_manager, \
    memb_invoice_expiration_filter_add_graceperiod, memb_renewal_period_expiration_filter_deactivate_graceperiod
from membership_manager.models import Membership, Invoice, MembershipRenew

logger = get_task_logger(__name__)
#every 5 mins this taks gets executed
def task_notify_invoice_expiration():
    """
    Gets the membership invoices and notify if there is any in the expiration range.
    """
    qset = Invoice.objects.all()
    notify_qset = invoice_expiration_filter_queryset(qset)

def task_notify_membership_expiration():
    """
    Gets the membership , and notify is there is in the expiration range.
    """
    qset = Invoice.objects.all()
    # notify_qset = filter_memb_queryset(qset)

def task_invoice_creation():
    """
    Create a invoice, at 60 days left - renewal expiration.
    """
    filtered_qset = renewal_expiration_filter_manager()
    if filtered_qset:
        for renew in filtered_qset:
            if not renew.inv_m_renews.exists():
                Invoice.objects.create(creation_date=timezone.now(), expiration_date=renew.end_date,
                                       payment_date=renew.end_date,
                                       membership=renew.membership, renewal_period=renew,
                                       description=f'{renew.membership.name} expire at {renew.end_date}.',
                                       amount=renew.membership.annual_cost,
                                       currency=renew.membership.currency, status='pending')


def task_membership_graceperiod():
    #this method will check if there is any invoices expired , then change them to graceperiod
    grace_period_date = timezone.now() + timezone.timedelta(days=14)
    qset = memb_invoice_expiration_filter_add_graceperiod()
    for membership in qset:
            membership.renews.create(creation_date= timezone.now(), membership=membership, start_date=timezone.now(),
                                    end_date=grace_period_date, graceperiod=True, active=True)
            membership.state = 'graceperiod'
            membership.save()


def task_membership_deactivate_graceperiod():
    #this method will check if there is any graceperiod expired , and change memberhsip to inactve inactive
    qset = memb_renewal_period_expiration_filter_deactivate_graceperiod()
    for membership in qset:
        tmp_renew_graceperiod = membership.renews.filter(active=True, graceperiod=True,end_date__lte= timezone.now())
        tmp_renew_graceperiod.update(active=False)
        tmp_renew = membership.renews.filter(active=True,graceperiod=False)
        tmp_renew.update(active=False)
        membership.state = 'inactive'
        membership.save()

