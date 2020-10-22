from django.contrib import admin

from django.utils import timezone
from django.utils.safestring import mark_safe

from membership_manager.invoice_utils import pay_invoice, pending_invoice, action_pay_invoice, regenerate_invoice_code, \
    regenerate_invoice_pdf, send_paid_invoice


def pay_invoice_action(modeladmin, request, queryset):
    """This actions take a queryset of invoice, and manage the membership and renewals, to apply a payment,
     send payment email, and Create LogEntry.

    :param modeladmin:
    :param request: helps to get the current user pk, for LogEntry porpoises.
    :param queryset: have the invoices qset to get paid.
    :return:
    """
    action_pay_invoice(queryset, request)


pay_invoice_action.short_description = "Pagar factura"


def recode_invoice(modeladmin, request, queryset):
    regenerate_invoice_code(queryset, request)


recode_invoice.short_description = 'Regenerar codigos de factura'


def regenerepdf_invoice(modeladmin, request, queryset):
    regenerate_invoice_pdf(request, queryset)


regenerepdf_invoice.short_description = 'Regenerar PDF de la factura'


def send_invoice_remainder_email(modeladmin, request, queryset):
    send_paid_invoice(queryset, request, 'notification_mail')


send_invoice_remainder_email.short_description = 'Enviar recordatorio facturas'


def send_invoice_paid_email(modeladmin, request, queryset):
    send_paid_invoice(queryset, request, 'pay_mail')


send_invoice_paid_email.short_description = 'Enviar notificación de pago de facturas'


class InvoiceAdmin(admin.ModelAdmin):
    actions = [pay_invoice_action, send_invoice_paid_email, send_invoice_remainder_email, recode_invoice,
               regenerepdf_invoice]

    list_filter = ('membership', 'status')

    search_fields = ('membership__organization__name', 'membership__organization__initials', 'code')
    list_display = ('code', 'membership_name', 'expiration_date',
                    'amount', 'currency', 'status', 'payment_date', 'download')
    list_editable = ()
    readonly_fields = ('download',)
    date_hierarchy = 'expiration_date'

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
