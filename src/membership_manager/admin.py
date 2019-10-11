import copy
import operator
from datetime import datetime, timedelta
from functools import reduce

from django.utils import timezone
from django.contrib import admin

# Register your models here.
from django.contrib.admin import SimpleListFilter
from django.db.models import Q
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

def q_generator():
    q = Membership.objects.all()
    qset = filter_queryset(q)
    return qset


def filter_queryset(queryset, filt = None):
    # This is where you process parameters selected by use via filter options:
    options = [Q(renews__end_date__range=(timezone.now()+timedelta(days=60)-timedelta(days=1), timezone.now()+timedelta(days=60))),
               Q(renews__end_date__range=(timezone.now()+timedelta(days=30)-timedelta(days=1), timezone.now()+timedelta(days=30))),
               Q(renews__end_date__range=(timezone.now()+timedelta(days=15)-timedelta(days=1), timezone.now()+timedelta(days=15))),
               Q(renews__end_date__range=(timezone.now()+timedelta(days=7)-timedelta(days=1), timezone.now()+timedelta(days=7))),
               Q(renews__end_date__range=(timezone.now()+timedelta(days=0)-timedelta(days=1), timezone.now()+timedelta(days=0)))
               ]
    if filt in ['60','30','15','7','0']:
        max_date = timezone.now()+timedelta(days=int(filt))
        min_date = max_date-timedelta(days=1)
        return queryset.distinct().filter(Q(renews__end_date__range=(min_date, max_date)) & Q(renews__active= True) & Q(state=True))
    else:
        return queryset.distinct().filter(reduce(operator.or_, options) & Q(renews__active= True) & Q(state=True))

class MembershipNotificationFilter(SimpleListFilter):
    title = 'Membership Renewals'  # a label for our filter
    parameter_name = 'renews'  # you can put anything here

    def lookups(self, request, model_admin):
        # This is where you create filter options; we have two:
        return [
            ('60', '60 days to pay'),
            ('30', '30 days to pay'),
            ('15', '15 days to pay'),
            ('7', '7 days to pay'),
            ('0', 'day to pay'),
            ]

    def queryset(self, request, queryset):
        # This is where you process parameters selected by use via filter options:


        q = q_generator()

        print(q)
        return filter_queryset(queryset,self.value())



class MemberShipAdmin(admin.ModelAdmin):
    list_filter = ('state', 'contact__country', 'services', MembershipNotificationFilter)
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
