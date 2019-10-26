from django.contrib import admin
# Register your models here.
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from membership_core.models import MembershipTemplate, SystemCurrency
from membership_manager import models
from membership_manager.admin_memberships import MembershipNotificationFilter, payments_history
from membership_manager.admin_pdf import InvoiceAdmin
from membership_manager.forms import MembershipAddForm
from membership_manager.models import MembershipRenew, Invoice


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

    organizations.short_description = "Organizaciones"

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

    memberships.short_description = "Membresías"


class MembershipRenewAdmin(admin.StackedInline):
    model = models.MembershipRenew
    extra = 0


class MemberShipAdmin(admin.ModelAdmin):
    actions = [payments_history]
    list_filter = (MembershipNotificationFilter, 'state', 'contact__country', 'services', 'contact', 'organization')
    search_fields = ('contact__first_name', 'contact__last_name')
    list_display = ('name', 'contact', 'organization', 'annual_cost',
                    'currency', 'renewal_period', 'state', 'invoices', 'next_pay',
                    'exchange_rates')
    readonly_fields = ['exchange_rates', 'invoices', 'next_pay']
    filter_horizontal = ['services']
    inlines = [MembershipRenewAdmin]
    form_class = MembershipAddForm
    fields = ['membership_template',
              'membership_type', 'contact', 'organization',
              'name', 'description', 'annual_cost', 'currency', 'exchange_rates',
              'services', 'renewal_period', 'state']

    def exchange_rates(self, obj):
        if obj:
            dev = '<p style="letter-spacing:2px;" >'

            for currency in SystemCurrency.objects.all():
                if obj.currency != currency:
                    # dev2 += str(convert_money(Money(obj.annual_cost, obj.currency.currency),
                    #                currency.currency))+" | "
                    dev += obj.currency.convert_money(
                        obj.annual_cost, currency.currency).__html__() + "  |  "

            dev += "</p>"
            return mark_safe(dev)

        return "Debes guardar primero para ver los tipos de cambio"

    exchange_rates.short_description = "Tipos de cambio"

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
                             'services': [svc.id for svc in obj.services.all()]})
        return args

    def save_formset(self, request, form, formset, change):
        instance = form.instance
        if not instance.renews.exists():
            MembershipRenew.objects.create(membership=instance, creation_date=timezone.now(), start_date=timezone.now(),
                                           end_date=timezone.now() + timezone.timedelta(
                                               days=30 * instance.renewal_period.months))
        else:
            lastRenew = False
            for form in formset:
                if bool(form.has_changed) and not bool(form.instance.active):
                    lastRenew = True    # if there is a renew in period of grace, when it has been inactivated,
                                            # there are going to be two renews in active = false.
                                            # We do not want two news renewals, just one.

            if instance.state == 'active' and bool(lastRenew):  # without the loop. Create a new renewal.
                MembershipRenew.objects.create(membership=instance, creation_date=timezone.now(),
                                               start_date=timezone.now(),
                                               end_date=timezone.now() + timezone.timedelta(
                                                   days=30 * instance.renewal_period.months))

            super(MemberShipAdmin, self).save_formset(request, form, formset, change)

    def invoices(self, obj):
        dev = ""
        if obj:
            dev += '<a href="%s" class="grp-button grp-button-state-inactive" >%d</a>' % (
                reverse("admin:membership_manager_invoice_changelist") + "?membership=" + str(
                    obj.pk
                ),
                obj.mem_inv.count()
                )
            dev= mark_safe(dev)
        return dev

    def next_pay(self, obj):
        dev = ""
        if obj:
            renew = obj.renews.filter(active=True).first()
            if renew is not None:
                dev += '<span style="color: %s">%s</span>'%(
                    "red" if renew.graceperiod else "gray",
                    str(renew)
                )
                dev= mark_safe(dev)
        return dev

    next_pay.short_description = "Fecha de renovación"
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
        return format_html(
            """<a href="{}" class="grp-button grp-button-state-inactive"  >{}</a> - 
               <a href="{}" class="grp-button grp-button-state-inactive" target="_blank">Add</a>
            """,
            reverse("admin:membership_manager_membership_changelist") +
            "?organization=" + str(obj.pk),
            obj.membership_set.filter(state="active").count(),
            reverse("admin:membership_manager_membership_add") +
            "?organization=" + str(obj.pk) + "&membership_type=Organizacional&currency=" +
            str(obj.currency_id) + "&contact=" + str(obj.contact_id)
        )

    memberships.short_description = "Membresías"


admin.site.register(models.Invoice, InvoiceAdmin)
admin.site.register(models.Organization, OrganizationAdmin)
admin.site.register(models.Contact, ContactAdmin)
admin.site.register(models.Membership, MemberShipAdmin)
