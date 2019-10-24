from django.utils import timezone


#from membership_manager.admin_memberships import filter_memb_queryset
from membership_manager.admin_pdf import invoice_expiration_filter_queryset, renewal_expiration_filter_manager, \
    memb_invoice_expiration_filter_add_graceperiod, memb_renewal_period_expiration_filter_deactivate_graceperiod
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

def task_invoice_cr():

    #Create a invoice, at 60 days left - renewal expiration
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

def task_membership_add_graceperiod():
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
