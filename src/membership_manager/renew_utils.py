from dateutil.relativedelta import relativedelta
from django.utils import timezone

from membership_manager.models import MembershipRenew
from membership_manager.render_pdf import generate_invoice


def create_renew(instance, now=None):

    if instance.membership_type != 'Streaming.la':

        if now is None:
            now = timezone.localdate(timezone.now())
        renew = MembershipRenew.objects.create(membership=instance, creation_date=now,
                                       start_date=now,
                                       encobro=True,
                                       end_date=now + relativedelta(
                                           months=+instance.renewal_period.months)
                                       )
        from membership_manager.task_utils import create_invoice_tool
        invoice=create_invoice_tool(renew.pk)
        generate_invoice(instance, invoice, buildpdf=False, email_template="notification_mail", enqueued=True, now=now)

        return renew


def get_expired_renew(now=None):
    if now is None:
        now = timezone.localdate(timezone.now())

    return MembershipRenew.objects.filter(membership__organization__active=True,
        end_date__lte=now, encobro=False, active=True, membership__state="active").exclude(
        membership__membership_type='Streaming.la')


def get_renew_without_inovice(now=None):
    if now is None:
        now = timezone.localdate(timezone.now())
    today_date = now + relativedelta(days=60)
    return MembershipRenew.objects.filter(membership__organization__active=True,
        start_date__lte=today_date,
        active=True, encobro=True,
        membership__state="active",
        inv_m_renews=None).exclude(
        membership__membership_type='Streaming.la')

def  get_renew_with_invoice_expired_today(now=None):
    if now is None:
        now = timezone.localdate(timezone.now())
    return MembershipRenew.objects.filter(
        inv_m_renews__expiration_date=now, active=True, encobro=True).exclude(
        membership__membership_type='Streaming.la')

def get_today_expired_renew(now=None):
    if now is None:
        now = timezone.localdate(timezone.now())

    membs = MembershipRenew.objects.filter(membership__organization__active=True,
        end_date=now, active=True, membership__state="active").exclude(
        membership__membership_type='Streaming.la')

    memb_none_end = MembershipRenew.objects.filter(membership__organization__active=True,
        membership__renewal_period__months__lt=60,
        end_date__lt=now, end_date__gt=now+relativedelta(days=-60), active=True, membership__state="active").exclude(
        membership__membership_type='Streaming.la')

    if memb_none_end.exists():
        membs = MembershipRenew.objects.filter(pk__in=
                                   list(membs.values_list('pk', flat=True)) +
                                   list(memb_none_end.values_list('pk', flat=True))
                                       )

    return membs