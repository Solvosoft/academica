from django.contrib import admin

# Register your models here.
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from membership_core.models import MembershipTemplate, SystemCurrency
from membership_manager import models
from membership_manager.admin_pdf import InvoiceAdmin
from membership_manager.forms import MembershipAddForm
from membership_manager.models import Membership, MembershipRenew
from djmoney.money import Money
from djmoney.contrib.exchange.models import convert_money

class ContactAdmin(admin.ModelAdmin):
    list_filter = ('active', 'country')
    search_fields = ('first_name', 'last_name')
    list_display = ("first_name",
                    "last_name",
                    "email",
                    "cellphone",
                    "country",
                    "organizations",
                    "memberships",
                    "active")

    fields = [
        "first_name",
        "last_name",
        "email",
        "cellphone",
        "phone",
        "address",
        "country",
        "city",
        "province",
        "postal_code",
        "active",
        "currency",
        "payment_method"
    ]

    def organizations(self, obj):
        return format_html(
            """
               <a href="{}"  class="grp-button grp-button-state-inactive" >{}</a> - 
               <a href="{}" class="grp-button grp-button-state-active" target="_blank">Add</a>
            """,
            reverse("admin:membership_manager_organization_changelist") +
            "?contact=" + str(obj.pk),
            obj.organization_set.count(),
            reverse("admin:membership_manager_organization_add") +
            "?contact=" + str(obj.pk) +
            "&currency=" + str(obj.currency.pk) + "&" +
            "&".join([x + "=" + str(getattr(obj, x)) for x in ("email",
                                                               "cellphone",
                                                               "country",
                                                               "city",
                                                               "province",
                                                               "postal_code",
                                                               "payment_method",)])
        )

    organizations.short_description = "Organizations"

    def memberships(self, obj):
        return format_html(
            """<a href="{}" class="grp-button grp-button-state-inactive"  >{}</a> - 
               <a href="{}" class="grp-button grp-button-state-inactive" target="_blank">Add</a>
            """,
            reverse("admin:membership_manager_membership_changelist") +
            "?contact=" + str(obj.pk),
            obj.membership_set.filter(state="active").count(),
            reverse("admin:membership_manager_membership_add") +
            "?contact=" + str(obj.pk) + "&membership_type=Personal&currency=" +
            str(obj.currency.pk)
        )

    memberships.short_description = "Membership"


class MembershipRenewAdmin(admin.StackedInline):
    model = models.MembershipRenew
    extra = 0


class MemberShipAdmin(admin.ModelAdmin):
    list_filter = ('state', 'contact__country', 'services')
    search_fields = ('contact__first_name', 'contact__last_name')
    list_display = ('name', 'contact', 'annual_cost',
                    'currency', 'renewal_period', 'state','invoices',
                    'exchange_rates')
    readonly_fields = ['exchange_rates', 'invoices']
    filter_horizontal = ['services']
    inlines = [MembershipRenewAdmin]
    form_class=MembershipAddForm
    fields = ['membership_template',
              'membership_type', 'contact', 'organization',
              'name','description', 'annual_cost', 'currency','exchange_rates',
              'services', 'renewal_period', 'state']


    def exchange_rates(self, obj):
        if obj:
            dev = ""
            for currency in SystemCurrency.objects.all():
                if obj.currency != currency:
                    dev += str(convert_money(Money(obj.annual_cost, obj.currency.currency),
                                    currency.currency))+" | "



            return dev

        return "Debes guardar primero para ver los tipos de cambio"

    exchange_rates.short_description = "Tipos de cambio"
    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = self.form_class
        return super().get_form(request, obj, **kwargs)

    def get_changeform_initial_data(self, request):
        tid = request.GET.get('tid')
        if tid:
            obj = MembershipTemplate.objects.filter(id=tid).first()
            if obj:
                return {'membership_template': obj.id,
                    'name': obj.name,
                    'annual_cost': obj.annual_cost,
                    'currency': obj.currency_id,
                    'description': obj.description,
                    'renewal_period': obj.renewal_period_id,
                    'state': obj.state,
                    'services': [svc.id for svc in obj.services.all()]}


    def invoices(self, obj):
        if obj:
            dev = ""
            dev += '<a href="%s" class="grp-button grp-button-state-inactive" >%d</a>'%(
                reverse("admin:membership_manager_invoice_changelist") +"?membership="+str(
                    obj.pk
                ),
                obj.invoice_set.all().count())
            return mark_safe(dev)
        return ""
    invoices.short_description = "Facturas"

class OrganizationAdmin(admin.ModelAdmin):
    list_filter = ('active', 'country')
    search_fields = ('name', 'initials')
    list_display = ("name", "email", "cellphone",
                    "contact", "memberships", "active")
    fields = [
        "name",
        "initials",
        "email",
        "cellphone",
        "phone",
        "address",
        "country",
        "city",
        "province",
        "postal_code",
        "active",
        "currency",
        "payment_method",
        "contact"
    ]

    def memberships(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>',
                           "#", obj.membership_set.filter(state="active").count()
                           )

    memberships.short_description = "Membership"


admin.site.register(models.Invoice, InvoiceAdmin)
admin.site.register(models.Organization, OrganizationAdmin)
admin.site.register(models.Contact, ContactAdmin)
admin.site.register(models.Membership, MemberShipAdmin)

