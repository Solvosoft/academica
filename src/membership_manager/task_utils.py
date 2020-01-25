from async_notifications.utils import send_email_from_template
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType

from membership_manager import utils
from membership_manager.invoice_utils import create_invoice
from membership_manager.models import Invoice, Membership
from membership_manager.render_pdf import generate_invoice
from membership_telbot_manager.models import TelGroup
from membership_telbot_manager.views import send_notification_message, send_deactivated_message


def notify_invoice_expiration(now):
    """
    Gets the membership invoices and notify if there is any in the expiration range.
    """
    notify_qset = utils.invoice_expiration_filter_queryset(now=now)  # Specific remaining days

    for invoice in notify_qset:
        emails=utils.get_emails(invoice.membership)
        send_email_from_template('notification_mail', emails,
                                 context={
                                     'membership': invoice.membership
                                 },
                                 enqueued=True,
                                 user=None,
                                 upfile=invoice.pdf_invoice)
        LogEntry.objects.log_action(
            user_id=utils.get_administrative_user(),
            content_type_id=ContentType.objects.get_for_model(invoice.membership).pk,
            object_id=invoice.membership.pk,
            object_repr="Notificación de pago pendiente enviada",
            action_flag=CHANGE
        )
        if TelGroup.objects.filter(organization_id=invoice.membership.organization.pk).first():
            send_notification_message(invoice.membership.organization.telgroup.chat_id,invoice.membership.organization)




def invoice_creation(now):
    renews = utils.renewal_expiration_filter_manager(now)
    for renew in renews:
        invoice = create_invoice(renew)
        generate_invoice(invoice.membership, invoice, email_template="notification_mail", enqueued=True)
        LogEntry.objects.log_action(
            user_id=utils.get_administrative_user(),
            content_type_id=ContentType.objects.get_for_model(invoice.membership).pk,
            object_id=invoice.membership.pk,
            object_repr="Factura creada pendiente de pago",
            action_flag=ADDITION
        )
        if TelGroup.objects.filter(organization_id=invoice.membership.organization.pk).first():
            send_notification_message(invoice.membership.organization.telgroup.chat_id,invoice.membership.organization)


def membership_deactivating(now):
    renews = utils.membership_deactivating_filter_manager(now)
    for renew in renews:
        membership = renew.membership
        emails = utils.get_emails(membership)
        send_email_from_template('expiration_mail', emails,
                                 context={
                                     'membership': membership
                                 },
                                 enqueued=True,
                                 user=None,
                                 upfile=None)

        LogEntry.objects.log_action(
            user_id=utils.get_administrative_user(),
            content_type_id=ContentType.objects.get_for_model(membership).pk,
            object_id=membership.pk,
            object_repr="Membresia inactiva por falta de pago",
            action_flag=CHANGE
        )
        if TelGroup.objects.filter(organization_id=membership.organization.pk).first():
            send_deactivated_message(membership.organization.telgroup.chat_id,membership.organization)


def membership_deactivating_membership(id_membresia, email=True):
    membership = Membership.objects.get(pk=id_membresia)
    renews = membership.renews.filter(encobro=True, active=True).order_by('end_date')
    for renew in renews:
        invoice = renew.inv_m_renews.first()
        if not invoice:
            create_invoice(renew)
        generate_invoice(membership, invoice, email_template='expiration_mail',
                         enqueued=True, send_email=email)

        if membership.organization and email:
            if TelGroup.objects.filter(organization_id=membership.organization.pk).first():
                send_deactivated_message(membership.organization.telgroup.chat_id,membership.organization)
