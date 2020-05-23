import random
import string
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q
from django.utils import timezone

from async_notifications.register import update_template_context
from membership_core.models import ServiceMT
from membership_manager.models import Invoice


def validateEmail( email ):
    try:
        validate_email( email )
        return True
    except ValidationError:
        return False

def get_emails(membership):
    emails = []
    if membership.contact:
        if validateEmail(membership.contact.email):
            emails.append(membership.contact.email )
    if membership.organization:
        if validateEmail(membership.organization.email):
            emails.append(membership.organization.email )
        if membership.organization.contact:
            if validateEmail(membership.organization.contact.email):
                emails.append(membership.organization.contact.email)
    if emails:
        emails = list(set(emails))
    return emails

def stringcode_generator(size=4, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))

def get_administrative_user():
    return User.objects.filter(is_superuser=True).first().pk

def get_membership_next_expired(queryset, value, now=None):
    if now is None:
        now = timezone.now()
    dates_list = (now + timedelta(days=int(value))).date()
    return queryset.filter(
        state="active",
        mem_inv__status='pending',
        mem_inv__expiration_date__lte=dates_list,
        mem_inv__renewal_period__encobro=True
    ).order_by('mem_inv__creation_date__date').distinct()

def get_membership_start_expired(queryset, value, now=None, start_in=None):
    if now is None:
        now = timezone.now()
    dates_list = (now + timedelta(days=int(value))).date()

    filters = {
        'state': "active",
        'renews__active': True,
        'renews__start_date__lte': dates_list,
        'renews__encobro': True
    }
    if start_in:
        filters['renews__start_date__gte']=start_in

    return queryset.filter( **filters ).order_by('renews__start_date__date').distinct()




def invoice_expiration_filter_queryset(now=None):
    """
    Search the possibles expiration invoice on 60, 45, 30, 15 7 or 1 day left to send a notification.

    :return: Invoice created in [60, 45, 30, 15 7 or 1] days after
    """

    if now is None:
        now = timezone.now()
    dates_list = [ (now + timedelta(days=x)).date() for x in [ 45, 30, 15, 7, 3,2, 1]]
    queryset = Invoice.objects.filter(
            Q( membership__contact__active=True)|Q( membership__organization__active=True),
            status='pending',
            membership__state="active",
            creation_date__in=dates_list,
            renewal_period__encobro=True, amount__gt=0 )
    return queryset


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

def membership_payment_manager(membership,invoice):
    """
    This util, help the manage of the invoice payment.
    Help with the management of MembershipRenews and Membership state (inactive, active, graceperiod).

    :param membership: Membership to update.
    :param invoice: Invoice to pay.
    :return:
    """
    renew = invoice.renewal_period
    renew.encobro = False
    renew.save()

    if membership.state == 'inactive':
        if not membership.renews.filter(encobro = True).exists():
            membership.state = 'active'
            membership.save()

def load_services_from_membership_template(template_id):
    initial = []
    services = ServiceMT.objects.filter(membership_id=template_id)
    if (services):
        for serv in services:
            initial.append({'servicetype': serv.servicetype, "membership": "", "description": serv.description,
                            "observations": serv.observations})
    extra = services.count()
    return initial, extra