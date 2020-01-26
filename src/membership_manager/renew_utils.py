from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.utils import timezone

from membership_manager.invoice_utils import create_invoice
from membership_manager.models import MembershipRenew


def create_renew(instance):
    now = timezone.now()
    renew = MembershipRenew.objects.create(membership=instance, creation_date=now,
                                   start_date=now,
                                   encobro=True,
                                   end_date=now + relativedelta(
                                       months=+instance.renewal_period.months)
                                   )
    create_invoice(renew)
    return renew


def get_expired_renew(now=None):
    if now is None:
        now = timezone.now()
    today_date = now.date()
    return MembershipRenew.objects.filter(
        Q(membership__contact__active=True) | Q(membership__organization__active=True),
        end_date__date__lte=today_date, encobro=False, active=True, membership__state="active")


def get_renew_without_inovice(now=None):
    if now is None:
        now = timezone.now()
    today_date = now.date()
    return MembershipRenew.objects.filter(
        Q(membership__contact__active=True) | Q(membership__organization__active=True),
        creation_date__date__lte=today_date,
        active=True, encobro=True,
        membership__state="active",
        inv_m_renews=None)

def  get_renew_with_invoice_expired_today(now=None):
    if now is None:
        now = timezone.now()
    return MembershipRenew.objects.filter(
        inv_m_renews__expiration_date__date=now.date(), active=True, encobro=True )

def get_comming_expired_renew(now=None):
    if now is None:
        now = timezone.now()
    today_date = (now + timezone.timedelta(days=60)).date()
    return MembershipRenew.objects.filter(
        Q(membership__contact__active=True) | Q(membership__organization__active=True),
        end_date__date=today_date, active=True, membership__state="active")