from async_notifications.register import update_template_context
from async_notifications.utils import send_email_from_template
from celery.schedules import crontab
from celery.task import task, periodic_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from requests import request

#from membership_manager.admin_memberships import filter_memb_queryset
from membership_manager.admin_pdf import invoice_expiration_filter_queryset, renewal_expiration_filter_manager
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
    qset = MembershipRenew.objects.all() #queryset
    # get the memberships with 30 days to expire (this is cuz if there is any membership with 1moth renewal
    # period then we can halde it and create a invoice)
    four_weeks_to_expire_qset = renewal_expiration_filter_manager(qset,30)
    # get memberhsips with 60 days to expire then check if there is any invoice with his pk and pending, then create one,
    eight_weeks_to_expire_qset = renewal_expiration_filter_manager(qset,60)
    if four_weeks_to_expire_qset:
        for renew in four_weeks_to_expire_qset:
            tmp_checker = Invoice.objects.filter(renewal_period__id=renew.pk, status='pending')
            if len(tmp_checker) == 0:
                Invoice.objects.create(creation_date=timezone.now(),expiration_date=renew.end_date,
                                   payment_date=renew.end_date,
                                   membership = renew.membership, renewal_period= renew,
                                   description= f'{renew.membership.name} expire at {renew.end_date}. Must pay.',amount=renew.membership.annual_cost,
                                   currency= renew.membership.currency, status = 'pending')
    if eight_weeks_to_expire_qset:
        for renew in eight_weeks_to_expire_qset:
            tmp_checker = Invoice.objects.filter(renewal_period__id= renew.pk,status='pending')
            if len(tmp_checker) == 0:
                Invoice.objects.create(creation_date=timezone.now(), expiration_date=renew.end_date,
                                       payment_date=renew.end_date,
                                       membership=renew.membership, renewal_period=renew,
                                       description=f'{renew.membership.name} expire at {renew.end_date}. Must pay.',
                                       amount=renew.membership.annual_cost,
                                       currency=renew.membership.currency, status='pending')

def task_membership_deactivating_or_graceperiod():
    #this method will check if there is any invoices expired , then change them to graceperiod
    yesterday_date = timezone.now()-timezone.timedelta(days=1)
    grace_period_date = timezone.now() - timezone.timedelta(days=15)
    qset = Invoice.objects.filter(status='pending')  # queryset

    for invoice in qset:
        tmp_memb_renew = MembershipRenew.objects.get(pk = invoice.renewal_period.pk)
        #check if renewal graceperiod expire
        if tmp_memb_renew.graceperiod == True and tmp_memb_renew.end_date.date() == grace_period_date.date():
            #change membership to inactive
            tmp_membship = Membership.objects.get(pk = invoice.membership.pk)
            tmp_membship.state = 'inactive'
            tmp_membship.save()
            #now change renewal status
            tmp_memb_renew.graceperiod = False
            tmp_memb_renew.save()
        #check if renewal expire
        if tmp_memb_renew.active == True and tmp_memb_renew.end_date.date() == yesterday_date.date():
            # now change membership status
            tmp_membship = Membership.objects.get(pk=invoice.membership.pk)
            tmp_membship.state = 'graceperiod'
            tmp_membship.save()
            # now change renewal status
            tmp_memb_renew.graceperiod = True
            tmp_memb_renew.active = False
            tmp_memb_renew.save()

