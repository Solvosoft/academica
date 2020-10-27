from datetime import timedelta

from django.utils import timezone

from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from membership_manager.models import Invoice
from membership_manager.render_pdf import build_pdf_invoice, generate_invoice
from membership_manager.utils import stringcode_generator, get_emails, membership_payment_manager
from membership_telbot_manager.utils import get_telegram_group
from membership_telbot_manager.views import send_invoice_message, send_notification_message
from async_notifications.utils import send_email_from_template


def create_invoice(renew, startdate=None, buildpdf=True):
    if startdate is None:
        startdate =  timezone.localdate(timezone.now())
    expiration = startdate + timedelta(days=60)

    if renew.membership.membership_type != 'Streaming.la':

        invoice = Invoice.objects.create(creation_date=timezone.localtime(timezone.now()),
                                         expiration_date=expiration,
                                         membership=renew.membership,
                                         renewal_period=renew,
                                         description=f'{renew.membership.name} expira al {renew.end_date}. Debe ser pagada.',
                                         amount=renew.membership.annual_cost,
                                         currency=renew.membership.currency,
                                         status='pending')
        string_code = stringcode_generator()
        invoice.code = f'%s-%s' % (string_code, str(invoice.pk).rjust(6, "0"))
        if buildpdf:
            build_pdf_invoice(renew.membership, invoice)

        return invoice


def pay_invoice(invoice):
    membership = invoice.membership
    invoice.status = "paid"
    invoice.payment_date = timezone.now()
    generate_invoice(membership, invoice)
    membership_payment_manager(membership, invoice)


def pending_invoice(invoice):
    membership = invoice.membership
    renew = invoice.renewal_period
    generate_invoice(membership, invoice, email_template="notification_mail")
    renew.active = True
    renew.encobro = True
    renew.save()


def action_pay_invoice(queryset, request):
    for invoice in queryset.filter(status__in = ['pending','inactive']):
        membership = invoice.membership
        pay_invoice(invoice)
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(membership).pk,
            object_id=membership.pk,
            object_repr="Pago de membresía realizado.",
            action_flag=CHANGE
        )
        if membership.organization:
            telgroup = get_telegram_group(membership)
            if telgroup:
                send_notification_message(telgroup.chat_id, membership.organization)
                if invoice.pdf_invoice:
                    send_invoice_message(telgroup.chat_id, invoice.pdf_invoice)


def regenerate_invoice_code(queryset, request):
    for invoice in queryset:
        string_code = stringcode_generator()
        invoice.code = f'%s-%s' % (string_code, str(invoice.pk).rjust(6, "0"))
        invoice.save()


def regenerate_invoice_pdf(queryset, request):
    for invoice in queryset:
        generate_invoice(invoice.membership, invoice,  send_email=False)


def send_paid_invoice(queryset, request, templatename):
    for invoice in queryset:
        membership = invoice.membership
        emails = get_emails(membership)
        now = timezone.localdate(timezone.now())
        delta = invoice.expiration_date - now
        send_email_from_template(templatename, emails,
                             context={
                                 'invoice': invoice,
                                 'membership': membership,
                                 'today': now,
                                 'days': delta.days
                             },
                             enqueued=False,
                             user=None,
                             upfile=invoice.pdf_invoice)
        if membership.organization and emails:
            telgroup = get_telegram_group(membership)
            if telgroup:
                send_notification_message(telgroup.chat_id, membership.organization)
                if invoice.pdf_invoice:
                    send_invoice_message(telgroup.chat_id, invoice.pdf_invoice)
