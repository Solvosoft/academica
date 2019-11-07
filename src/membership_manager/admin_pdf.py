from dateutil.relativedelta import relativedelta
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.safestring import mark_safe

from membership_manager.models import MembershipRenew
from membership_manager.render_pdf import generate_invoice
from membership_manager import utils
from membership_manager.utils import membership_payment_manager


def pay_invoice(modeladmin, request, queryset):
    """This actions take a queryset of invoice, and manage the membership and renewals, to apply a payment,
     send payment email, and Create LogEntry.

    :param modeladmin:
    :param request: helps to get the current user pk, for LogEntry porpoises.
    :param queryset: have the invoices qset to get paid.
    :return:
    """
    for invoice in queryset:
        membership = invoice.membership
        generate_invoice(membership, invoice)
        invoice.status = "paid"
        invoice.payment_date = timezone.now()
        invoice.save()
        membership_payment_manager(membership,invoice)

        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(membership).pk,
            object_id=membership.pk,
            object_repr="Pago de membresía realizado, poniendo todos los periódos de gracia inactivos",
            action_flag=CHANGE
        )

pay_invoice.short_description = "Pagar factura"


class InvoiceRenewalNotificationFilter(SimpleListFilter):
    title = 'Facturas Pendientes'  # a label for our filter
    parameter_name = 'renews'

    def lookups(self, request, model_admin):
        # This is where you create filter options; we have two:
        return [
            ('60', 'a 60 días'),
            ('30', 'a 30 días'),
            ('15', 'a 15 días'),
            ('7', 'a 7 días'),
            ('0', 'Hoy'),
        ]

    def queryset(self, request, queryset):
        # This is where you process parameters selected by use via filter options:
        return utils.invoice_expiration_filter_queryset(queryset, self.value())


class InvoiceAdmin(admin.ModelAdmin):
    actions = [pay_invoice]

    list_filter = ('membership', 'status')

    search_fields = ('membership__contact__first_name',
                     'membership__contact__last_name',
                     'membership__name')
    list_display = ('membership', 'expiration_date', 'amount', 'currency', 'status', 'payment_date', 'download')
    list_editable = ()
    readonly_fields = ('download',)

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

