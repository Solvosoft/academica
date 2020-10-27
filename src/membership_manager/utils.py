import random
import string
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q
from django.http import QueryDict
from django.utils import timezone

from async_notifications.models import NewsLetterTemplate
from async_notifications.register import update_template_context
from async_notifications.utils import get_newsletter_context
from membership_core.models import ServiceMT
from membership_manager.models import Invoice, Membership
from membership_manager.newsletterform import FilterEmailsForm


def validateEmail( email ):
    try:
        validate_email( email )
        return True
    except ValidationError:
        return False

def get_emails(membership):
    emails = []
    if membership.organization:
        if validateEmail(membership.organization.email):
            emails.append(membership.organization.email )
        if membership.organization.contacts:
            for contact in membership.organization.contacts.all():
                if validateEmail(contact.email):
                    emails.append(contact.email)
    if emails:
        emails = list(set(emails))
    return emails

def stringcode_generator(size=4, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))

def get_administrative_user():
    return User.objects.filter(is_superuser=True).first().pk

def get_membership_next_expired(queryset, value, now=None):
    if now is None:
        now = timezone.localdate(timezone.now())
    dates_list = now + relativedelta(days=int(value))
    return queryset.filter(
        state="active",
        mem_inv__status='pending',
        mem_inv__expiration_date__lte=dates_list,
        mem_inv__renewal_period__encobro=True
    ).order_by('mem_inv__creation_date').distinct()

def get_membership_start_expired(queryset, value, now=None, start_in=None):
    if now is None:
        now = timezone.localdate(timezone.now())
    end_in = now + relativedelta(days=int(value))
    start_in  = start_in or now
    filters = {
        'state': "active",
        'renews__active': True,
        'renews__start_date__lte': end_in,
        'renews__start_date__gte': start_in,
        'renews__encobro': True
    }

    return queryset.filter( **filters ).order_by('renews__start_date').distinct()




def invoice_expiration_filter_queryset(now=None):
    """
    Search the possibles expiration invoice on 60, 45, 30, 15 7 or 1 day left to send a notification.

    :return: Invoice created in [60, 45, 30, 15 7 or 1] days after
    """

    if now is None:
        now = timezone.localdate(timezone.now())
    dates_list = [ now + relativedelta(days=x) for x in [ 45, 30, 15, 7, 3,2, 1]]
    queryset = Invoice.objects.filter( membership__organization__active=True,
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


def get_context_news_letter(template_pk):
    context_list = []
    template = NewsLetterTemplate.objects.filter(pk=template_pk).first()

    if template:
        context = get_newsletter_context(template.model_base)

        for x in context:

            context_list.append(

                (x[0], f'{x[0]} -- {x[1]}{x[2]}')
            )

    return context_list

def get_emails_news_letter(news_letter):

    form = FilterEmailsForm(QueryDict(news_letter.filters))
    form.is_valid()
    queryset = Membership.objects.all()
    filters = {}

    apply_filters = form.cleaned_data['apply_filters']
    search_in = form.cleaned_data['search_in']
    apply_fees = form.cleaned_data['apply_fees']

    if apply_filters:

        if form.cleaned_data['name']:
            filters['organization__in'] = form.cleaned_data['name']

        if form.cleaned_data['state']:
            filters['state'] = form.cleaned_data['state']

        if form.cleaned_data['country']:
            filters['organization__country__in'] = form.cleaned_data['country']

        if form.cleaned_data['currency']:
            filters['currency__in'] = form.cleaned_data['currency']

        if form.cleaned_data['payment_method']:
            filters['payment_method__in'] = form.cleaned_data['payment_method']

        if form.cleaned_data['membership_type']:
            filters['membership_type__in'] = form.cleaned_data['membership_type']

        if form.cleaned_data['service_type']:
            filters['service__servicetype__in'] = form.cleaned_data['service_type']

        if form.cleaned_data['invoices']:
            filters['mem_inv__status'] = form.cleaned_data['invoices']


        if search_in:
            if search_in == "contacto":
                filters['organization__type'] = True
            elif search_in == "organizacion":
                filters['organization__type'] = False

        if apply_fees:
            filters['apply_fees'] = apply_fees

        queryset = queryset.filter(**filters)

    mails = list(queryset.exclude(organization__email__isnull=True).values_list('organization__email', flat=True))

    return mails

def check_newsletter_update(news_letter):

    mails = news_letter.recipient.replace(' ', '').split(',')
    update_news_letter = False

    for email in get_emails_news_letter(news_letter):
        email = email.replace(' ', '')
        if not email in mails:
            update_news_letter = True
            break
    return update_news_letter

def get_contentype_choices():
    CHOICES = []

    for ct in ContentType.objects.all():
        CHOICES.append((ct.pk, ct.name))

    return tuple(CHOICES)


def add_logentry(app_label, model, object_pk, object_repr, user, action):
    contenttype = ContentType.objects.filter(app_label=app_label, model=model).first()
    entry = LogEntry()
    entry.action_time = datetime.now()
    entry.content_type = contenttype
    entry.object_id = object_pk
    entry.object_repr = object_repr
    entry.user = user
    entry.action_flag = action
    entry.save()