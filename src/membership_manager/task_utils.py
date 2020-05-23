from dateutil.relativedelta import relativedelta
from django.db.models import Q

from async_notifications.utils import send_email_from_template
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from membership_manager import renew_utils as renewutils
from membership_manager import utils
from membership_manager.invoice_utils import create_invoice
from membership_manager.models import Membership, MembershipRenew, Invoice
from membership_manager.render_pdf import generate_invoice, build_pdf_invoice
from membership_manager.utils import get_emails

from membership_telbot_manager.views import send_notification_message, send_deactivated_message
from membership_telbot_manager.models import TelGroup

def get_telegram_group(membership):
    if membership.organization:
        return TelGroup.objects.filter(organization_id=membership.organization.pk).first()

def notify_invoice_expiration(now):
    """
    Gets the membership invoices and notify if there is any in the expiration range.
    """
    notify_qset = utils.invoice_expiration_filter_queryset(now=now)  # Specific remaining days
    total = notify_qset.count()
    dev = ''
    for invoice in notify_qset:
        emails=utils.get_emails(invoice.membership)
        delta = invoice.expiration_date - now
        send_email_from_template('notification_mail', emails,
                                 context={
                                     'membership': invoice.membership,
                                     'invoice': invoice,
                                     'today': now,
                                     'days': delta.days
                                 },
                                 enqueued=True,
                                 user=None,
                                 upfile=invoice.pdf_invoice)
        LogEntry.objects.log_action(
            user_id=utils.get_administrative_user(),
            content_type_id=ContentType.objects.get_for_model(invoice.membership).pk,
            object_id=invoice.membership.pk,
            object_repr="Notificación de pago pendiente enviada",
            action_flag=CHANGE,
            change_message="Notificación de pago pendiente enviada "+ str(invoice)
        )
        dev += str(invoice)+"\n"
        telgroup = get_telegram_group(invoice.membership)
        if telgroup:
            send_notification_message(telgroup.chat_id,invoice.membership.organization)

    return total, dev

def generate_renew(now):
    renews = renewutils.get_today_expired_renew(now)
    total = renews.count()
    dev = ''
    for renew in renews:
        membership = renew.membership
        new_renew = MembershipRenew.objects.create(
            creation_date=now,
            membership=renew.membership,
            start_date=renew.end_date+relativedelta(days=1),
            end_date=renew.end_date+relativedelta(months=membership.renewal_period.months),
            encobro=membership.annual_cost > 0 ,
            active=True
        )
        LogEntry.objects.log_action(
            user_id=utils.get_administrative_user(),
            content_type_id=ContentType.objects.get_for_model(membership).pk,
            object_id= membership.pk,
            object_repr="Periodo de renovación agregado " ,
            action_flag=ADDITION,
            change_message="Periodo de renovación agregado %s %s"%(str(new_renew), str(renew.membership))
        )
        dev += "%s %s %d\n"%(str(new_renew), str(renew.membership), membership.annual_cost)
        if membership.annual_cost == 0:
            emails = utils.get_emails(membership)
            send_email_from_template('membresia_gratuita', emails,
                                     context={
                                         'membership': membership,
                                     },
                                     enqueued=True,
                                     user=None,
                                     upfile=None)
    return total, dev

def inactive_renew(now):
    renews = renewutils.get_expired_renew(now)
    total = renews.count()
    if renews.exists():
        renews.update(active=False)
    return total, ''

def invoice_creation(now, extrafilters={}):
    # Devuelve los renews que en 60 días vencen
    renews = renewutils.get_renew_without_inovice(now)
    total = 0
    dev = ''
    for renew in renews.filter(**extrafilters):
        invoice = create_invoice(renew)
        if invoice.amount == 0:
            continue
        total += 1
        membership = invoice.membership
        generate_invoice(membership, invoice, buildpdf=False, email_template="notification_mail", enqueued=True, now=now)

        LogEntry.objects.log_action(
            user_id=utils.get_administrative_user(),
            content_type_id=ContentType.objects.get_for_model(membership).pk,
            object_id=membership.pk,
            object_repr="Factura creada pendiente de pago",
            action_flag=ADDITION,
            change_message="Factura creada pendiente de pago %s  " % (str(invoice),)
        )
        dev += str(invoice)+"\n"
        telgroup = get_telegram_group(membership)
        if telgroup:
            send_notification_message(telgroup.chat_id, membership.organization)

    return total, dev

def membership_deactivating(now):
    renews = renewutils.get_renew_with_invoice_expired_today(now)
    total = renews.count()
    dev = ''
    for renew in renews:
        membership = renew.membership
        emails = utils.get_emails(membership)
        invoice = Invoice.objects.filter(renewal_period=renew).first()
        send_email_from_template('expiration_mail', emails,
                                 context={
                                     'membership': membership,
                                     'renew': renew,
                                     'invoice': invoice
                                 },
                                 enqueued=True,
                                 user=None,
                                 upfile=invoice.pdf_invoice if invoice is not None else None)

        LogEntry.objects.log_action(
            user_id=utils.get_administrative_user(),
            content_type_id=ContentType.objects.get_for_model(membership).pk,
            object_id=membership.pk,
            object_repr="Membresia inactiva por falta de pago",
            action_flag=CHANGE,
            change_message="Membresia inactiva por falta de pago %s  " % (str(membership),)

        )
        dev += str(membership)+"\n"
        telgroup = get_telegram_group(membership)
        if telgroup:
            send_deactivated_message(telgroup.chat_id, membership.organization)
    return total, dev

def membership_deactivating_membership(id_membresia, email=True):
    membership = Membership.objects.get(pk=id_membresia)
    renews = membership.renews.filter(encobro=True, active=True).order_by('end_date')
    for renew in renews:
        invoice = renew.inv_m_renews.first()
        if not invoice:
            invoice = create_invoice(renew)
        generate_invoice(membership, invoice, email_template='expiration_mail',
                         enqueued=True, send_email=email)

        if membership.organization and email:
            telgroup = get_telegram_group(membership)
            if telgroup:
                send_deactivated_message(telgroup.chat_id, membership.organization)

def create_invoice_tool(id_renew):
    renew = MembershipRenew.objects.get(pk=id_renew)
    invoice = renew.inv_m_renews.first()
    if invoice is None:
        invoice = create_invoice(renew)
    else:
        if invoice.pdf_invoice:
            invoice.pdf_invoice.delete(False)
    build_pdf_invoice(renew.membership, invoice)
    return invoice

def send_welcome_notification(id_membership):
    instance = Membership.objects.filter(Q(contact__active=True)|Q(organization__active=True), pk=id_membership).first()
    if instance:
        emails = get_emails(instance)
        send_email_from_template('welcome_mail', emails,
                             context={
                                 'membership': instance
                             },
                             enqueued=True,
                             user=None,
                             upfile=None)


def update_last_daterenew():
    memberships = Membership.objects.filter(
        state="active"
    )

    for memb in memberships:
        memb.last_renew_start_date =memb.last_renew
        memb.save()