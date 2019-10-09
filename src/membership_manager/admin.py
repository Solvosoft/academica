from django.contrib import admin

# Register your models here.
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html

from membership_core.models import MembershipTemplate
from membership_manager import models

admin.site.register([models.Invoice])

class ContactAdmin(admin.ModelAdmin):
    list_filter = ('active', 'country')
    search_fields = ('first_name', 'last_name')
    #list_editable = ('active',)
    list_display = ("first_name",
                    "last_name",
                    "email",
                    "cellphone",
                    "country",
                    "organizations",
                    "memberships",
                    "create_membership_template",
                    "active" )

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
            reverse("admin:membership_manager_organization_changelist")+
            "?contact="+str(obj.pk),
            obj.organization_set.count(),
            reverse("admin:membership_manager_organization_add") +
            "?contact=" + str(obj.pk) +
            "&currency=" + str(obj.currency.pk) +"&"+
            "&".join([x+"="+str(getattr(obj, x)) for x in ("email",
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
            reverse("admin:membership_manager_membership_changelist")+
            "?contact="+str(obj.pk),
            obj.membership_set.filter(state="active").count(),
            reverse("admin:membership_manager_membership_add") +
               "?contact=" + str(obj.pk) + "&membership_type=Personal&currency=" +
               str(obj.currency.pk)
                    )
    memberships.short_description = "Membership"

    def create_membership_template(self, obj):
        return render_to_string(
            'partial/create_membership_template.html',
            context={
                'contact': obj,
                'templates': MembershipTemplate.objects.all()
            }
        )
    create_membership_template.short_description = "Create Membership from template"

class MembershipRenewAdmin(admin.StackedInline):
    model = models.MembershipRenew
    extra = 0

class MemberShipAdmin(admin.ModelAdmin):
    list_filter = ('state', 'contact__country', 'services')
    search_fields = ('contact__first_name', 'contact__last_name')
    list_display = ('name', 'contact',  'annual_cost',
                    'currency', 'renewal_period', 'state')
    filter_horizontal = ['services']
    inlines = [MembershipRenewAdmin]


class OrganizationAdmin(admin.ModelAdmin):
    list_filter = ('active', 'country')
    search_fields = ('name', 'initials')
    list_display = ( "name", "email", "cellphone",
            "contact",   "memberships", "active" )
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

admin.site.register(models.Organization, OrganizationAdmin)
admin.site.register(models.Contact, ContactAdmin)
admin.site.register(models.Membership, MemberShipAdmin)
admin.sites.DefaultAdminSite.title = "Membresias locas"
