from django.contrib import admin
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.safestring import mark_safe

from async_notifications.utils import send_email_from_template
from membership_manager.invoice_utils import pay_invoice, pending_invoice
from membership_manager.render_pdf import generate_invoice
from membership_manager.utils import stringcode_generator, get_emails
from membership_telbot_manager.models import TelGroup
from membership_telbot_manager.views import send_invoice_message, send_notification_message


def pay_invoice_action(modeladmin, request, queryset):
    """This actions take a queryset of invoice, and manage the membership and renewals, to apply a payment,
     send payment email, and Create LogEntry.

    :param modeladmin:
    :param request: helps to get the current user pk, for LogEntry porpoises.
    :param queryset: have the invoices qset to get paid.
    :return:
    """
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
            telgroup = TelGroup.objects.filter(organization_id=membership.organization.pk).first()
            if telgroup:
                send_notification_message(telgroup.chat_id, membership.organization)
                if invoice.pdf_invoice:
                    send_invoice_message(telgroup.chat_id, invoice.pdf_invoice)


pay_invoice_action.short_description = "Pagar factura"

def recode_invoice(modeladmin, request, queryset):
    for invoice in queryset:
        string_code = stringcode_generator()
        invoice.code = f'%s-%s' % (string_code, str(invoice.pk).rjust(6, "0"))
        invoice.save()
recode_invoice.short_description = 'Regenerar codigos de factura'

def regenerepdf_invoice(modeladmin, request, queryset):
    for invoice in queryset:
        generate_invoice(invoice.membership, invoice,  send_email = False)

regenerepdf_invoice.short_description = 'Regenerar PDF de la factura'

def send_paid_invoice(queryset, templatename):
    for invoice in queryset:
        membership = invoice.membership
        emails = get_emails(membership)
        now = timezone.now()
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
            telgroup = TelGroup.objects.filter(organization_id=membership.organization.pk).first()
            if telgroup:
                send_notification_message(telgroup.chat_id, membership.organization)
                if invoice.pdf_invoice:
                    send_invoice_message(telgroup.chat_id, invoice.pdf_invoice)

def send_invoice_remainder_email(modeladmin, request, queryset):
    send_paid_invoice(queryset, 'notification_mail')
send_invoice_remainder_email.short_description = 'Enviar recordatorio facturas'


def send_invoice_paid_email(modeladmin, request, queryset):
    send_paid_invoice(queryset, 'pay_mail')
send_invoice_paid_email.short_description = 'Enviar notificación de pago de facturas'


class InvoiceAdmin(admin.ModelAdmin):
    actions = [pay_invoice_action,send_invoice_paid_email, send_invoice_remainder_email, recode_invoice, regenerepdf_invoice]

    list_filter = ('membership', 'status')

    search_fields = ('membership__contact__first_name',
                     'membership__contact__last_name',
                     'membership__organization__name', 'membership__organization__initials', 'code')
    list_display = ('code', 'membership_name', 'expiration_date',
                    'amount', 'currency', 'status', 'payment_date', 'download')
    list_editable = ()
    readonly_fields = ('download',)

    class Media:
        js = ('js/membership.js',)


    def download(self, obj):
        dev = ""
        if bool(obj.pdf_invoice):
            dev += '<a href="%s" class="grp-button grp-button-state-inactive" target="_blank" >%s</a>' % (
                obj.pdf_invoice.url,
                "Descargar")
            dev = mark_safe(dev)
        return dev

    def save_model(self, request, obj, form, change):
        super(InvoiceAdmin, self).save_model(request, obj, form, change)
        if 'status' in form.changed_data:
            if form.cleaned_data['status'] == 'paid':
                pay_invoice(obj)
            if form.cleaned_data['status'] == 'pending':
                pending_invoice(obj)