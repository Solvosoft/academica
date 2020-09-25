from djgentelella.groute import register_lookups
from djgentelella.views.select2autocomplete import BaseSelect2View
from membership_core.models import ServiceType
from membership_manager.models import Organization, Contact


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
