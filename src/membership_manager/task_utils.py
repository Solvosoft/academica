from datetime import timedelta

from async_notifications.utils import send_email_from_template
from django.conf import settings
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType

from membership_manager.models import Invoice, MembershipRenew
from membership_manager.render_pdf import generate_invoice
from membership_manager.utils import invoice_expiration_filter_queryset, renewal_expiration_filter_manager, \
    get_administrative_user


def notify_invoice_expiration(now):
    """
    Gets the membership invoices and notify if there is any in the expiration range.
    """
    qset = Invoice.objects.all()

    notify_qset = invoice_expiration_filter_queryset(qset)  # Specific remaining days

    for invoice in notify_qset:
        if invoice.membership.contact:
            email = invoice.membership.contact.email
        else:
            email = invoice.membership.organization.contact.email
        send_email_from_template('notification_mail', [email],
                                 context={
                                     'membership': invoice.membership
                                 },
                                 enqueued=True,
                                 user=None,
                                 upfile=None)
        LogEntry.objects.log_action(
            user_id=get_administrative_user(),
            content_type_id=ContentType.objects.get_for_model(invoice.membership).pk,
            object_id=invoice.membership.pk,
            object_repr="Notificación de pago pendiente enviada",
            action_flag=CHANGE
        )

def invoice_creation(now):
    renews = renewal_expiration_filter_manager(now)
    for renew in renews:
        invoice = Invoice.objects.create(creation_date=now,
                                         expiration_date=renew.end_date,
                                         payment_date=renew.end_date,
                                         membership=renew.membership,
                                         renewal_period=renew,
                                         description=f'{renew.membership.name} expira al {renew.end_date}. Debe ser pagada.',
                                         amount=renew.membership.annual_cost,
                                         currency=renew.membership.currency,
                                         status='pending')

        generate_invoice(invoice.membership, invoice, email_template="notification_mail", enqueued=True)
        LogEntry.objects.log_action(
            user_id=get_administrative_user(),
            content_type_id=ContentType.objects.get_for_model(invoice.membership).pk,
            object_id=invoice.membership.pk,
            object_repr="Factura creada pendiente de pago",
            action_flag=ADDITION
        )

def renew_graceperiod(now):
    renews = MembershipRenew.objects.filter(end_date__date=now.date(),
                                            active=True,
                                            graceperiod=False,
                                            membership__state="active"
                                            )
    for renew in renews:
        membership = renew.membership
        MembershipRenew.objects.create(
            creation_date=now,
            membership=renew.membership,
            start_date=now,
            end_date=now + timedelta(days=settings.GRACE_PERIOD_DAYS),
            graceperiod=True,
            active=True
        )
        membership.state = "graceperiod"
        membership.save()
        LogEntry.objects.log_action(
            user_id=get_administrative_user(),
            content_type_id=ContentType.objects.get_for_model(membership).pk,
            object_id=membership.pk,
            object_repr="Membresia ha cambiado a periodo de prueba",
            action_flag=ADDITION
        )

def membership_deactivating(now):
    renews = MembershipRenew.objects.filter(end_date__date__lte=now.date(),
                                            active=True,
                                            graceperiod=True,
                                            membership__state="graceperiod"
                                            )
    for renew in renews:
        membership = renew.membership
        if membership.contact:
            email = membership.contact.email
        else:
            email = membership.organization.contact.email
        send_email_from_template('expiration_mail', [email],
                                 context={
                                     'membership': membership
                                 },
                                 enqueued=True,
                                 user=None,
                                 upfile=None)

        membership.state = "inactive"
        membership.save()
        MembershipRenew.objects.filter(membership=membership).update(active=False)
        LogEntry.objects.log_action(
            user_id=get_administrative_user(),
            content_type_id=ContentType.objects.get_for_model(membership).pk,
            object_id=membership.pk,
            object_repr="Membresia inactiva por falta de pago",
            action_flag=CHANGE
        )
