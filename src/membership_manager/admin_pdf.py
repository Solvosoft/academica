from django.contrib import admin
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe

from membership_manager.render_pdf import generate_invoice


def pay_invoice(modeladmin, request, queryset):
    for invoice in queryset:
        generate_invoice(invoice.membership, invoice)


pay_invoice.short_description = "Pagar factura"


class InvoiceAdmin(admin.ModelAdmin):
    actions = [pay_invoice]
    list_filter = ('membership', 'status')
    search_fields = ('membership__contact__first_name',
                     'membership__contact__last_name',
                     'membership__name')
    list_display = ( 'membership', 'expiration_date', 'amount', 'currency', 'status', 'download')
    readonly_fields = ('download', )


    def download(self, obj):
        dev = ""
        if obj and obj.pdf_invoice is not None:

            dev+= '<a href="%s" class="grp-button grp-button-state-inactive" target="_blank" >%s</a>'%(
                obj.pdf_invoice.url,
                "Descargar"
            )
            return mark_safe(dev)
        return dev