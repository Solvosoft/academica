from django.contrib import admin
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.functional import curry
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_countries import countries

from membership_core.models import MembershipTemplate, SystemCurrency
from membership_manager import models
from membership_manager.admin_memberships import membership_payments_history, \
    organization_payments_history, send_email_to_owner, send_email_vencimiento, buscar_inconsistencias, \
    export_csv_fields
from membership_manager.admin_pdf import InvoiceAdmin
from membership_manager.adminfilters import PaisFilter, OrganizationFilter, MembershipPaisFilter, ContactPaisFilter, \
    InvoiceRenewalNotificationFilter
from membership_manager.forms import MembershipAddForm, ServiceForm
from membership_manager.renew_utils import create_renew
from membership_manager.utils import load_services_from_membership_template


class ContactAdmin(admin.ModelAdmin):
    actions = [export_csv_fields]
    list_filter = ('active', ContactPaisFilter)
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
               <a href="{}" class="grp-button grp-button-state-active" target="_blank">Agregar</a>
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

    organizations.short_description = "Organizaciones"

    def memberships(self, obj):
        return format_html(
            """<a href="{}" class="grp-button grp-button-state-inactive"  >{}</a> - 
               <a href="{}" class="grp-button grp-button-state-inactive" target="_blank">Agregar</a>
            """,
            reverse("admin:membership_manager_membership_changelist") +
            "?contact=" + str(obj.pk),
            obj.membership_set.filter(state="active").count(),
            reverse("admin:membership_manager_membership_add") +
            "?contact=" + str(obj.pk) + "&membership_type=Personal&currency=" +
            str(obj.currency.pk)
        )

    memberships.short_description = "Membresías"


class MembershipRenewAdmin(admin.TabularInline):
    model = models.MembershipRenew
    extra = 1
    classes = ['collapse', 'collapsed']
    fields = [ "creation_date",
                "start_date",
                "end_date",
               'encobro',
                "active",
               "show_invoice"
    ]
    readonly_fields = ['show_invoice']


    def show_invoice(self, obj):
        dev = "-"
        str(obj)
        if obj:
            invoice = obj.inv_m_renews.first()
            if invoice is None:
                dev = '<a href="%s" target="_blank">Crear</a>'%(
                    reverse_lazy("generate_invoice", args=(obj.pk,))
                )
            else:
                if invoice.pdf_invoice:
                    dev = '<a href="%s" target="_blank">Descargar</a>'%(
                        invoice.pdf_invoice.url
                    ) + '<a href="%s" target="_blank"> - Ver</a>'%(
                        reverse_lazy("admin:membership_manager_invoice_change", args=(invoice.pk,))
                    )
                else:
                    dev = '<a href="%s" target="_blank">Crear PDF</a>' % (
                        reverse_lazy("build_pdf_invoice", args=(obj.pk,))
                    )+ '<a href="%s" target="_blank"> - Ver</a>'%(
                        reverse_lazy("admin:membership_manager_invoice_change", args=(invoice.pk,))
                    )

        return mark_safe(dev)
    show_invoice.short_description = "Factura"



class ServiceAdmin(admin.TabularInline):
    model = models.Service
    extra = 1
    classes = ['collapse', 'collapsed']
    form = ServiceForm

    def get_formset(self, request, obj=None, **kwargs):
        initial = []
        if request.GET.get('tid'):
            initial, self.extra = load_services_from_membership_template(request.GET.get('tid'))
        formset = super(ServiceAdmin, self).get_formset(request, obj, **kwargs)
        formset.__init__ = curry(formset.__init__, initial=initial)
        return formset


class MemberShipAdmin(admin.ModelAdmin):
    actions = [membership_payments_history, send_email_to_owner,
               send_email_vencimiento, export_csv_fields, buscar_inconsistencias]
    list_filter = (OrganizationFilter, InvoiceRenewalNotificationFilter, MembershipPaisFilter)
    search_fields = ('contact__first_name', 'contact__last_name', 'organization__name')
    list_display = ('name', 'annual_cost', 'currency',
                    'countryspect', 'renewal_period', 'state', 'invoices', 'next_pay',
                    )
    readonly_fields = ['exchange_rates', 'invoices', 'next_pay', 'name', 'countryspect']

    inlines = [ServiceAdmin, MembershipRenewAdmin]
    form_class = MembershipAddForm
    fields = ['name',
              'membership_template',
              'membership_type', 'contact', 'organization',
              'annual_cost', 'currency', 'exchange_rates',
              'renewal_period', 'state']

    class Media:
        js = ('js/membership.js',)

    def exchange_rates(self, obj):
        if obj:
            dev = '<p style="letter-spacing:2px;" >'

            for currency in SystemCurrency.objects.all():
                if obj.annual_cost and obj.currency != currency:
                    # dev2 += str(convert_money(Money(obj.annual_cost, obj.currency.currency),
                    #                currency.currency))+" | "
                    dev += obj.currency.convert_money(
                        obj.annual_cost, currency.currency).__html__() + "  |  "

            dev += "</p>"
            return mark_safe(dev)

        return "Debes guardar primero para ver los tipos de cambio"

    exchange_rates.short_description = "Tipos de cambio"

    def countryspect(self, obj):
        if obj:
            country_data = dict(countries)
            country = ''
            if obj.organization:
                country = country_data[obj.organization.country]
            elif obj.contact:
                country = country_data[obj.contact.country]

            dev = '<p style="letter-spacing:2px;" >'
            dev += "%s <br> %s" % (country, obj.get_membership_type_display())
            dev += "</p>"
            return mark_safe(dev)
        return ""

    countryspect.short_description = "Información"

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = self.form_class
        return super().get_form(request, obj, **kwargs)

    def get_changeform_initial_data(self, request):
        args = {}
        for field in self.fields:
            getfield = request.GET.get(field, '')
            if getfield:
                args[field] = getfield

        tid = request.GET.get('tid')
        if tid:
            obj = MembershipTemplate.objects.filter(id=tid).first()
            if obj:
                args.update({'membership_template': obj.id,
                             'name': obj.name,
                             'annual_cost': obj.annual_cost,
                             'currency': obj.currency_id,
                             'description': obj.description,
                             'renewal_period': obj.renewal_period_id,
                             'state': obj.state,
                             })
        return args

    def save_formset(self, request, form, formset, change):
        super(MemberShipAdmin, self).save_formset(request, form, formset, change)
        instance = form.instance
        if not instance.renews.exists():
            create_renew(instance)

    def invoices(self, obj):
        dev = ""
        if obj:
            dev += '<a href="%s" class="grp-button grp-button-state-inactive" >%d</a>' % (
                reverse("admin:membership_manager_invoice_changelist") + "?membership=" + str(
                    obj.pk
                ),
                obj.mem_inv.count()
            )
            dev = mark_safe(dev)
        return dev

    def next_pay(self, obj):
        dev = ""
        if obj:
            for renew in obj.renews.filter(active=True, encobro=True):
                url = reverse_lazy('generate_invoice', args=(renew.pk,))
                color = "red"
                title="Generar factura"
                if renew.inv_m_renews.all().exists():
                    color = "gray"
                    invoice = renew.inv_m_renews.first()
                    if invoice.pdf_invoice:
                        url = invoice.pdf_invoice.url
                    title = "Pagar antes de %s"%(invoice.expiration_date.strftime("%d/%m/%Y"))
                dev += '<a href="%s" target="_blank" title="%s"><span style="color: %s">%s</span></a><br>' % (
                    url,
                    title,
                    color,
                    str(renew)
                )
            dev = mark_safe(dev)
        return dev

    next_pay.short_description = "Fecha de renovación"
    next_pay.admin_order_field = '-renews__encobro'
    invoices.short_description = "Facturas"


class OrganizationAdmin(admin.ModelAdmin):
    list_filter = ('active', PaisFilter)
    search_fields = ('name', 'initials')
    list_display = ("name", "email", "cellphone",
                    "contact", "memberships", "activities", "active")
    actions = [organization_payments_history, export_csv_fields]
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
        return format_html(
            """<a href="{}" class="grp-button grp-button-state-inactive"  >{}</a> - 
               <a href="{}" class="grp-button grp-button-state-inactive" target="_blank">Agregar</a>
            """,
            reverse("admin:membership_manager_membership_changelist") +
            "?organization=" + str(obj.pk),
            obj.membership_set.filter(state="active").count(),
            reverse("admin:membership_manager_membership_add") +
            "?organization=" + str(obj.pk) + "&membership_type=Organizacional&currency=" +
            str(obj.currency_id) + "&contact=" + str(obj.contact_id)
        )

    def activities(self, obj):
        return format_html(
            """<a href="{}" class="grp-button grp-button-state-inactive"  >{}</a> - 
               <a href="{}" class="grp-button grp-button-state-inactive" target="_blank">Agregar</a>
            """,
            reverse("admin:membership_manager_activityreport_changelist") +
            "?organization=" + str(obj.pk),
            obj.activities.count(),
            reverse("admin:membership_manager_activityreport_add") +
            "?organization=" + str(obj.pk)

        )

    memberships.short_description = "Membresías"


class AttentionAdmin(admin.StackedInline):
    model = models.Attention
    classes = ["collapse", "collapsed"]
    extra = 1


class ActivityReportAdmin(admin.ModelAdmin):
    search_fields = ('start_date',)
    list_display = ("organization", "duration", "get_description",
                    "start_date", "end_date")
    inlines = [AttentionAdmin]

    fields = [
        "organization",
        "start_date",
        "end_date",
        "description",
        "duration"
    ]

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_description(self, obj):
        return mark_safe(render_to_string('activity_description.html',
                                          {'obj': obj}))

    get_description.short_description = "Descripción"


admin.site.register(models.ActivityReport, ActivityReportAdmin)
admin.site.register(models.Invoice, InvoiceAdmin)
admin.site.register(models.Organization, OrganizationAdmin)
admin.site.register(models.Contact, ContactAdmin)
admin.site.register(models.Membership, MemberShipAdmin)
