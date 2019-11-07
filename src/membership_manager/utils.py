from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User

from django.utils import timezone

from membership_manager.models import MembershipRenew, Membership


def get_administrative_user():
    return User.objects.filter(is_superuser=True).first().pk


def get_dates(filt):
    max_date = timezone.now() + timedelta(days=int(filt))
    min_date = max_date - timedelta(days=1)
    return min_date, max_date


def renewal_expiration_filter_manager(now=None):
    if now is None:
        now = timezone.now()
    queryset = MembershipRenew.objects.all()  # queryset
    today_date = (now + timezone.timedelta(days=60)).date()
    return queryset.filter(end_date__date__lte=today_date,
                           active=True,
                           graceperiod=False,
                           membership__state="active",
                           inv_m_renews=None)


def memb_invoice_expiration_filter_add_graceperiod(now=None):
    if now is None:
        now = timezone.now()
    queryset = Membership.objects.all()  # queryset
    return queryset.filter(
        mem_inv__expiration_date__date__lte=now.date(),
        mem_inv__status='pending',
        mem_inv__renewal_period__active=True,
        mem_inv__renewal_period__graceperiod=False,
        state='active').distinct()


def memb_renewal_period_expiration_filter_deactivate_graceperiod(now=None):
    if now is None:
        now = timezone.now()
    queryset = Membership.objects.all()  # queryset
    today_date = now.date()
    return queryset.filter(renews__end_date__date__lte=today_date,
                           state='graceperiod', renews__active=True,
                           renews__graceperiod=True, mem_inv__status='pending')


def invoice_expiration_filter_queryset(queryset, filt=None):
    """
    Search the possibles expiration memberships on 60, 45, 30, 15 7 or 1 day left to send a notification.

    :param queryset:
    :param filt:
    :return: Membership for days specified in filt or membership for [60, 45, 30, 15 7 or 1] days after
    """
    if filt is not None:
        lookup_day = (timezone.now() + timedelta(days=int(filt))).date()
        queryset = queryset.filter(expiration_date__date=lookup_day,
                                   status='pending').distinct()
    else:
        now = timezone.now()
        queryset = queryset.filter(
            expiration_date__date__in=[
                (now + timedelta(days=x)).date() for x in [60, 45, 30, 15, 7, 0]],
            status='pending').distinct()
    return queryset

def  membership_filter(queryset, filt=None, now=None):
    # This is where you process parameters selected by use via filter options:
    if now is None:
        now = timezone.now()
    if filt is not False:
        if filt is not None:
            lookup_day = (now + timedelta(days=int(filt))).date()
            queryset=queryset.filter(
                renews__end_date__date=lookup_day,
                renews__active=True,
                state='active')
        else:
            queryset = queryset.filter(
                renews__end_date__date__in=[
                    (now + timedelta(days=x)).date() for x in [60, 45, 30, 15, 7, 0]],
                renews__active=True, state=True
                 )
    return queryset.distinct()

def membership_payment_manager(membership,invoice):
    """
    This util, help the manage of the invoice payment.
    Help with the management of MembershipRenews and Membership state (inactive, active, graceperiod).

    :param membership: Membership to update.
    :param invoice: Invoice to pay.
    :return:
    """
    renew = invoice.renewal_period
    if membership.state == 'active':
        renew.active = False
        renew.save()
        MembershipRenew.objects.create(
            membership=membership, creation_date=renew.end_date,
            start_date=renew.end_date,
            end_date=renew.end_date + relativedelta(
                months=+membership.renewal_period.months)
        )
    if membership.state == 'graceperiod':
        renew.active = False
        renew.save()
        invoice.membership.renews.filter(membership=membership, graceperiod=True, active=True).update(active=False)
        MembershipRenew.objects.create(
            membership=membership, creation_date=timezone.now(),
            start_date=timezone.now(),
            end_date=timezone.now() + relativedelta(
                months=+membership.renewal_period.months)
        )
        membership.state = 'active'
        membership.save()

    if membership.state == 'inactive':
        MembershipRenew.objects.create(
            membership=membership, creation_date=timezone.now(),
            start_date=timezone.now(),
            end_date=timezone.now() + relativedelta(
                months=+membership.renewal_period.months)
        )
        membership.state = 'active'
        membership.save()




