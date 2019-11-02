from datetime import timedelta

from async_notifications.register import update_template_context
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
        dates_list = [
                (now + timedelta(days=x)).date() for x in [60, 45, 30, 15, 7, 0]]
        queryset = queryset.filter(expiration_date=dates_list,status='pending')
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


def loademailtemplates():
    update_template_context('pay_mail',
                                'Pago de membresía - Código Sur',
                                [('desc', 'Correo automático para el pago de membresias'), ],
                                'pay_email.html',
                                as_template=True)

    update_template_context('welcome_mail',
                                'Bienvenido(a) - Código Sur',
                                [('desc', 'Correo automatico de bienvenida a Código Sur'), ],
                                'subscribe_email.html',
                                as_template=True)

    update_template_context("notification_mail",
                                'Nuevo Aviso - Código Sur',
                                [('desc', 'Recordatorios automaticos de los pagos pendientes'), ],
                                'pay_email.html',
                                as_template=True)

    update_template_context("expiration_mail",
                                'Membresía desactivada - Código Sur',
                                [('desc', 'Correo automatico de expiración de membresías'), ],
                                'expiration_email.html',
                                as_template=True)
