from django.contrib import admin
from django.shortcuts import render
from membership_manager.render_pdf import generate_invoice


def pay_invoice(modeladmin, request, queryset):
    for invoice in queryset:
        generate_invoice(invoice.membership, invoice)


pay_invoice.short_description = "Pagar factura"


class InvoiceAdmin(admin.ModelAdmin):
    actions = [pay_invoice]
