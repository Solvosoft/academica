from django.db.models import Q
from djgentelella.groute import register_lookups
from djgentelella.views.select2autocomplete import BaseSelect2View
from membership_core.models import ServiceType
from membership_manager.models import Organization, Contact, Membership


@register_lookups(prefix="organization", basename="organizationbasename")
class OrganizationGModelLookup(BaseSelect2View):
    model = Organization
    fields = ['name']


@register_lookups(prefix="contact", basename="contactbasename")
class ContactGModelLookup(BaseSelect2View):
    model = Contact
    fields = ['name']


@register_lookups(prefix="servicetype", basename="servicetypebasename")
class ServiceTypeGModelLookup(BaseSelect2View):
    model = ServiceType
    fields = ['name']


@register_lookups(prefix="orgacontact", basename="orgcontact")
class ContactGModelLookup(BaseSelect2View):
    model = Membership
    fields = []

    def filter_queryset(self, queryset):
        q = self.request.GET.get('term', '')
        self.selected = self.query_get('selected', '')
        queryset = queryset.filter(Q(organization__name__icontains=q)|Q(
                                    organization__initials__icontains=q)|Q(
                                    contact__first_name__icontains=q)|Q(
                                    contact__last_name__icontains=q))
        return queryset