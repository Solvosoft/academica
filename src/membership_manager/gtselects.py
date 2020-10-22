from django.db.models import Q
from djgentelella.groute import register_lookups
from djgentelella.views.select2autocomplete import BaseSelect2View

from membership_core.models import ServiceType, Country, SystemCurrency
from membership_manager.models import Organization


@register_lookups(prefix="organization", basename="organizationbasename")
class OrganizationGModelLookup(BaseSelect2View):
    model = Organization
    fields = ['name', 'initials']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(type=False)

@register_lookups(prefix="contact", basename="contactbasename")
class ContactGModelLookup(BaseSelect2View):
    model = Organization
    fields = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(type=True)


@register_lookups(prefix="servicetype", basename="servicetypebasename")
class ServiceTypeGModelLookup(BaseSelect2View):
    model = ServiceType
    fields = ['name']


@register_lookups(prefix="orgacontact", basename="orgcontact")
class ContactGModelLookup(BaseSelect2View):
    model = Organization
    fields = []

    def filter_queryset(self, queryset):
        q = self.request.GET.get('term', '')
        self.selected = self.query_get('selected', '')
        self.tipo = self.query_get('tipo', '')
        queryset = queryset.filter(Q(name__icontains=q)|Q(initials__icontains=q))

        if self.tipo:
            if self.tipo[0] == "contacto":
                queryset = queryset.filter(type=True)
            else:
                queryset = queryset.filter(type=False)

        return queryset


@register_lookups(prefix="country", basename="countrybasename")
class CountryGModelLookup(BaseSelect2View):
    model = Country
    fields = ['name']


@register_lookups(prefix="currency", basename="currencybasename")
class CurrencyGModelLookup(BaseSelect2View):
    model = SystemCurrency
    fields = ['currency']
