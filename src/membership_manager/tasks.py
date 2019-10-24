from decimal import Decimal

from async_notifications.utils import send_email_from_template
from django.utils import timezone

from membership_manager.admin_memberships import filter_memb_queryset
from membership_manager.task_utils import notify_invoice_expiration
from membresias_codigosur.celery import app

from membership_manager.admin_pdf import invoice_expiration_filter_queryset, renewal_expiration_filter_manager
from membership_manager.models import Membership, Invoice, MembershipRenew


@app.task(name='task_notify_invoice')
def task_notify_invoice_expiration():
    notify_invoice_expiration(timezone.now())


def task_notify_membership_expiration():
    """
    Gets the membership , and notify is there is in the expiration range.
    """
    qset = Invoice.objects.all()
    notify_qset = filter_memb_queryset(qset)


@app.task(name='task_invoice_creation')
def task_invoice_creation():
    """
    Create a invoice, at 60 days left - renewal expiration.
    """
    qset = MembershipRenew.objects.all()  # queryset
    # get the memberships with 30 days to expire (this is cuz if there is any membership with 1moth renewal
    # period then we can handle it and create a invoice)
    four_weeks_to_expire_qset = renewal_expiration_filter_manager(qset, 30)
    # get memberships with 60 days to expire then check if there is any invoice with his pk and pending, then create
    # one,
    eight_weeks_to_expire_qset = renewal_expiration_filter_manager(qset, 60)
    if four_weeks_to_expire_qset:
        for renew in four_weeks_to_expire_qset:
            tmp_checker = Invoice.objects.filter(renewal_period__id=renew.pk, status='pending')
            if len(tmp_checker) == 0:
                Invoice.objects.create(creation_date=timezone.now(),
                                       expiration_date=renew.end_date,
                                       payment_date=renew.end_date,
                                       membership=renew.membership,
                                       renewal_period=renew,
                                       description=f'{renew.membership.name} expire at {renew.end_date}. Must pay.',
                                       amount=Decimal(renew.membership.annual_cost/renew.membership.renewal_period.months),
                                       currency=renew.membership.currency,
                                       status='pending')
    if eight_weeks_to_expire_qset:
        for renew in eight_weeks_to_expire_qset:
            tmp_checker = Invoice.objects.filter(renewal_period__id=renew.pk, status='pending')
            if len(tmp_checker) == 0:
                Invoice.objects.create(creation_date=timezone.now(),
                                       expiration_date=renew.end_date,
                                       payment_date=renew.end_date,
                                       membership=renew.membership,
                                       renewal_period=renew,
                                       description=f'{renew.membership.name} expire at {renew.end_date}. Must pay.',
                                       amount=renew.membership.annual_cost,
                                       currency=renew.membership.currency,
                                       status='pending')


@app.task(name='task_deactivating_or_graceperiod')
def task_membership_deactivating_or_graceperiod():
    # this method will check if there is any invoices expired , then change them to graceperiod
    yesterday_date = timezone.now() - timezone.timedelta(days=1)
    grace_period_date = timezone.now() - timezone.timedelta(days=15)
    qset = Invoice.objects.filter(status='pending')  # queryset

    for invoice in qset:
        tmp_memb_renew = MembershipRenew.objects.get(pk=invoice.renewal_period.pk)
        # check if renewal graceperiod expire
        if bool(tmp_memb_renew.graceperiod) and tmp_memb_renew.end_date.date() == grace_period_date.date():
            # change membership to inactive
            tmp_membship = Membership.objects.get(pk=invoice.membership.pk)
            tmp_membship.state = 'inactive'
            tmp_membship.save()
            # now change renewal status
            tmp_memb_renew.graceperiod = False
            tmp_memb_renew.save()

            # this notifies that membership has expired
            if tmp_membship.contact:
                email = tmp_membship.contact.email
            else:
                email = tmp_membship.organization.contact.email
            send_email_from_template('expiration_mail', [email],
                                     context={
                                         'membership': tmp_membship
                                     },
                                     enqueued=True,
                                     user=None,
                                     upfile=None)

        # check if renewal expire
        if bool(tmp_memb_renew.active) and tmp_memb_renew.end_date.date() == yesterday_date.date():
            # now change membership status
            tmp_membship = Membership.objects.get(pk=invoice.membership.pk)
            tmp_membship.state = 'graceperiod'
            tmp_membship.save()
            # now change renewal status
            tmp_memb_renew.graceperiod = True
            tmp_memb_renew.active = False
            tmp_memb_renew.save()
