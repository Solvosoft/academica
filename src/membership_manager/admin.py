from django.contrib import admin

# Register your models here.
from django.urls import reverse
from django.utils.html import format_html
from membership_core.models import MembershipTemplate
from membership_manager import models
from membership_manager.admin_pdf import InvoiceAdmin
from membership_manager.models import Membership, MembershipRenew


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
                    'currency', 'renewal_period', 'state')
    filter_horizontal = ['services']
    inlines = [MembershipRenewAdmin]

    def changeform_view(self, request, obj_id, form_url, extra_context=None):
        query = Membership.objects.all()
        extra_context = {'data': query}
        return super(MemberShipAdmin, self).changeform_view(request, obj_id, form_url, extra_context=extra_context)

    def get_changeform_initial_data(self, request):
        if request.GET.get('temp'):
            obj = MembershipTemplate.objects.get(id=request.GET.get('temp'))
            return {'membership_template': obj.id,
                    'name': obj.name,
                    'annual_cost': obj.annual_cost,
                    'currency': obj.currency_id,
                    'description': obj.description,
                    'renewal_period': obj.renewal_period_id,
                    'state': obj.state,
                    'services': [svc.id for svc in obj.services.all()]}


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
admin.sites.DefaultAdminSite.title = "Membresias locas"
